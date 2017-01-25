import grequests
from eveapimongo import MongoProvider
import xml.etree.ElementTree
import re


def lambda_handler(event, context):
    AssetsParser().main()
    return "done"


class AssetsParser:
    apis = []

    def main(self):
        self.apis = self.load_apis()
        api_results = self.get_api_results(self.apis)
        transformed = self.transform(api_results)
        filtered = self.filter_irrelevant(transformed)
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
                api_key_pattern = re.compile("keyID=(?P<keyID>\d+)")
                api_v_code_pattern = re.compile("vCode=(?P<vCode>[^&]+)")
                response_api_key = api_key_pattern.search(response.url).group("keyID")
                response_api_v_code = api_v_code_pattern.search(response.url).group("vCode")
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
            query = "keyID=%d&vCode=%s&flat=%d" % (api['key'], api['vCode'], 1)
            if api['type'] == 'corp':
                endpoint = "/corp/AssetList.xml.aspx"
                endpoint_url = base_url + endpoint
                api_url = endpoint_url + "?" + query
                urls.append({'apiId': api['_id'], 'url': api_url})
            else:
                endpoint = "/char/AssetList.xml.aspx"
                endpoint_url = base_url + endpoint
                api_url = endpoint_url + "?" + query
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
                    'itemId': int(row.get('itemID')),
                    'locationId': int(row.get('locationID')),
                    'typeId': int(row.get('typeID')),
                    'quantity': int(row.get('quantity')),

                    # 62: Deliveries
                    'flag': int(row.get('flag')),
                    'singleton': int(row.get('singleton')),

                    # -1: BPO or Singleton
                    # -2: BPC
                    'rawQuantity': int(row.get('rawQuantity')) if row.get('rawQuantity') else 0,
                })

        return result

    def filter_irrelevant_and_existing(self, documents):
        without_irrelevant = self.filter_irrelevant(documents)
        return self.filter_existing(without_irrelevant)

    def filter_irrelevant(self, documents):
        result = []
        for doc in documents:
            result.append(doc)
        return result

    def filter_existing(self, documents):
        result = []
        for document in documents:
            found = MongoProvider().find_one('assetList', {'itemId': document['itemId']})
            # if it doesn't exist
            if found is None:
                result.append(document)
        return result

    def write(self, documents):
        cursor = MongoProvider().cursor('assetList')

        # Delete existing assets
        for api in self.apis:
            cursor.delete_many({'apiId': api['_id']})

        cursor.insert_many(documents)

if __name__ == '__main__':
    AssetsParser().main()