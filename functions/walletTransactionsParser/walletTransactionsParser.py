import grequests
from eveapimongo import MongoProvider
import xml.etree.ElementTree


def lambda_handler(event, context):
    WalletTransactionsParser().main()
    return "done"


class WalletTransactionsParser:
    def main(self):
        apis = self.load_apis()
        api_results = self.get_api_results(apis)
        transformed = self.transform(api_results)
        filtered = self.filter_existing(transformed)
        self.write(filtered)

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
                endpoint = "/corp/WalletTransactions.xml.aspx"
                endpoint_url = base_url + endpoint
                api_url = endpoint_url + "?" + verification
                for accountKey in [1000, 1001, 1002, 1003, 1004, 1005, 1006]:
                    api_url_with_account = api_url + "&accountKey=" + str(accountKey)
                    urls.append({'apiId': api['_id'], 'url': api_url_with_account})
            else:
                endpoint = "/char/WalletTransactions.xml.aspx"
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
                    'transactionId': int(row.get('transactionID')),
                    'timestamp': row.get('transactionDateTime'),
                    'quantity': int(row.get('quantity')),
                    'typeName': row.get('typeName'),
                    'typeId': int(row.get('typeID')),
                    'price': float(row.get('price')),
                    'transactionType': row.get('transactionType'),
                    'stationId': int(row.get('stationID')),
                    'clientId': int(row.get('clientID'))
                })

        return result

    def filter_existing(self, documents):
        result = []
        for document in documents:
            found = MongoProvider().find_one('walletTransactions', {'transactionId': document['transactionId']})
            # if it doesn't exist
            if found is None:
                result.append(document)
        return result

    def write(self, documents):
        cursor = MongoProvider().cursor('walletTransactions')
        cursor.insert_many(documents)
