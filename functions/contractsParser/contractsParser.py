import grequests
from eveapimongo import MongoProvider
import xml.etree.ElementTree


def lambda_handler(event, context):
    ContractsParser().main()
    return "done"


class ContractsParser:
    def main(self):
        apis = self.load_apis()
        api_results = self.get_api_results(apis)
        transformed = self.transform(api_results)
        self.delete_updatable(transformed)
        filtered = self.filter_existing(transformed)
        self.write(filtered)

    def delete_updatable(self, contract_documents):
        contract_id_list = self.get_contract_ids(contract_documents)
        contract_filter = {'status': {"$in": ['Outstanding', 'InProgress']}, 'contractId': {"$in": contract_id_list}}
        MongoProvider().cursor('contracts').delete_many(contract_filter)

    def get_contract_ids(self, contract_documents):
        result = []
        for contract in contract_documents:
            result.append(contract['contractId'])
        return result

    def load_apis(self):
        result = []
        for document in MongoProvider().find('apis'):
            result.append(document)
        return result

    def get_api_results(self, apis):
        urls = self.build_urls(apis)
        responses = self.get_async_result(urls)

        result = []
        api_by_key_dict = {}
        for api in apis:
            api_by_key_dict[api['key']] = api

        for response in responses:
            if response is None or response.status_code == 200:
                response_api_key = response.url.split('keyID=')[1].split("&vCode")[0]
                response_api_v_code = response.url.split('&vCode=')[1].split("&accountKey")[0]
                api = api_by_key_dict[int(response_api_key)]
                if api['vCode'] == response_api_v_code:
                    # now we matched an api with the response
                    result.append({'apiId': api['_id'], 'text': response.text})

        return result

    def get_async_result(self, urls):
        rs = (grequests.get(u['url']) for u in urls)
        result = grequests.map(rs)
        return result

    def build_urls(self, apis):
        base_url = "https://api.eveonline.com"
        urls = []
        for api in apis:
            verification = "keyID=%d&vCode=%s" % (api['key'], api['vCode'])
            if api['type'] == 'corp':
                endpoint = "/corp/Contracts.xml.aspx"
            else:
                endpoint = "/char/Contracts.xml.aspx"
            endpoint_url = base_url + endpoint
            api_url = endpoint_url + "?" + verification
            urls.append({'apiId': api['_id'], 'url': api_url})

        return urls

    def transform(self, api_results):
        result = []
        for api_result in api_results:
            e = xml.etree.ElementTree.fromstring(api_result['text'])
            xml_result = e[1]

            if xml_result.tag == 'error':
                print("ERROR: " + xml_result.text)
                continue

            xml_rowset = xml_result[0]
            for row in xml_rowset:
                result.append({
                    'apiId': api_result['apiId'],
                    'contractId': int(row.get('contractID')),
                    'title': row.get('title'),
                    'status': row.get('status'),
                    'type': row.get('type'),
                    'volume': float(row.get('volume')),
                    'reward': float(row.get('reward')),
                    'price': float(row.get('price')),
                    'endStationId': int(row.get('endStationID')),
                    'numDays': int(row.get('numDays')),
                    'assigneeId': int(row.get('assigneeID')),
                    'dateCompleted': row.get('dateCompleted')
                })

        return result

    def filter_existing(self, documents):
        result = []
        for document in documents:
            found = MongoProvider().find_one('contracts', {'contractId': document['contractId']})
            # if it doesn't exist
            if found is None:
                result.append(document)
        return result

    def write(self, documents):
        cursor = MongoProvider().cursor('contracts')
        cursor.insert_many(documents)

if __name__ == '__main__':
    ContractsParser().main()