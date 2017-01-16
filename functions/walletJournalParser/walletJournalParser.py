import grequests
from eveapimongo import MongoProvider
import xml.etree.ElementTree


def lambda_handler(event, context):
    WalletJournalParser().main()
    return "done"


class WalletJournalParser:
    def main(self):
        apis = self.load_apis()
        api_results = self.get_api_results(apis)
        transformed = self.transform(api_results)
        filtered = self.filter_irrelevant_and_existing(transformed)
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
                endpoint = "/corp/WalletJournal.xml.aspx"
                endpoint_url = base_url + endpoint
                api_url = endpoint_url + "?" + verification
                for accountKey in [1000, 1001, 1002, 1003, 1004, 1005, 1006]:
                    api_url_with_account = api_url + "&accountKey=" + str(accountKey)
                    urls.append({'apiId': api['_id'], 'url': api_url_with_account})
            else:
                endpoint = "/char/WalletJournal.xml.aspx"
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
                    'journalId': int(row.get('refID')),
                    'refTypeId': int(row.get('refTypeID')),
                    'timestamp': row.get('date'),
                    'amount': float(row.get('amount'))
                })

        return result

    def filter_irrelevant_and_existing(self, documents):
        without_irrelevant = self.filter_irrelevant(documents)
        return self.filter_existing(without_irrelevant)

    def filter_irrelevant(self, documents):
        result = []
        for doc in documents:
            # relevant refTypeIDs
            # 1 Player Trading
            # 46 Broker Fee
            # 54 Sales Tax
            if doc['refTypeId'] in [1, 46, 54]:
                result.append(doc)
        return result

    def filter_existing(self, documents):
        result = []
        for document in documents:
            found = MongoProvider().find_one('walletJournal', {'journalId': document['journalId']})
            # if it doesn't exist
            if found is None:
                result.append(document)
        return result

    def write(self, documents):
        cursor = MongoProvider().cursor('walletJournal')
        cursor.insert_many(documents)
