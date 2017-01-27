import xml.etree.ElementTree

import grequests
from eveapimongo import MongoProvider
import re

def lambda_handler(event, context):
    ContractsParser().main()
    return "done"


class ExternalProvider:
    def get_apis(self):
        result = []
        for api in MongoProvider().find('apis'):
            result.append(api)
        return result

    def get_parallel_api_results(self, urls):
        rs = (grequests.get(u['url'], timeout=10) for u in urls)
        result = grequests.imap(rs)
        return result

class ContractsParser:
    base_url = "https://api.eveonline.com"
    contract_endpoint = "Contracts.xml.aspx"
    contract_items_endpoint = "ContractItems.xml.aspx"
    external_provider = ExternalProvider()

    def main(self):
        apis = self.external_provider.get_apis()
        apis_with_contracts = self.get_contracts(apis)
        apis_with_contracts_and_items = self.extend_contracts_with_items(apis_with_contracts, apis)
        contracts = self.merge_api_into_contract(apis_with_contracts_and_items)
        self.write(contracts)

    def write(self, documents):
        if len(documents) > 0:
            cursor = MongoProvider().cursor('contracts')
            for document in documents:
                existing_document = cursor.find_one({'contractId': document['contractId']})
                if existing_document is not None:
                    # Preserve existing items, as we don't pull them in again.
                    if 'items' in existing_document:
                        document['items'] = existing_document['items']

                    cursor.update({'contractId': document['contractId']}, document)
                else:
                    cursor.insert(document)

    def get_contracts(self, apis):
        urls = self.build_contract_urls(apis)
        responses = self.external_provider.get_parallel_api_results(urls)
        apis_with_responses = self.create_dict_with_apis_and_responses(responses, apis)
        apis_with_contracts = self.transform_contract_responses_to_contracts(apis_with_responses)
        return apis_with_contracts

    def create_dict_with_apis_and_responses(self, responses, apis):
        result = {}
        for response in responses:
            api_key_pattern = re.compile("keyID=(?P<keyID>\d+)")
            api_v_code_pattern = re.compile("vCode=(?P<vCode>[^&]+)")
            response_api_key = api_key_pattern.search(response.url).group("keyID")
            response_api_v_code = api_v_code_pattern.search(response.url).group("vCode")
            for api in apis:
                if int(api['key']) == int(response_api_key) and api['vCode'] == response_api_v_code:
                    api_id = api['_id']
                    result[api_id] = response
                    break
        return result

    def build_contract_urls(self, apis):
        urls = []
        for api in apis:
            verification = self.build_api_verifications(api)
            # type can be corp or char
            api_type = "/%s/" % api['type']
            url = self.base_url + api_type + self.contract_endpoint + "?" + verification
            urls.append({'apiId': api['_id'], 'url': url})
        return urls

    def build_api_verifications(self, api):
        key = api['key']
        v_code = api['vCode']
        return "keyID=%d&vCode=%s" % (key, v_code)

    def transform_contract_responses_to_contracts(self, responses):
        result = {}
        for apiId in responses:
            contracts = self.transform_contract_response_to_contracts(responses[apiId])
            entry_value = []
            for contract in contracts:
                entry_value.append(contract)
            result[apiId] = entry_value
        return result

    def transform_contract_response_to_contracts(self, response):
        rows = self.get_rows(response.text)
        result = []

        if rows is None:
            return result

        for row in rows:
            result.append(self.create_contract_from_row(row))
        return result

    def create_contract_from_row(self, row):
        return {
            'contractId': int(row.get('contractID')),
            # Contract Types:
            # ItemExchange
            # Courier
            # Loan
            # Auction
            'type': row.get('type'),
            'issuerId': int(row.get('issuerID')),
            'issuerCorpId': int(row.get('issuerCorpID')),
            'assigneeId': int(row.get('assigneeID')),
            'acceptorId': int(row.get('acceptorID')),
            'volume': float(row.get('volume')),
            'startStationId': int(row.get('startStationID')),
            'forCorp': int(row.get('forCorp')) == 1,
            # Public
            # Private
            'availability': row.get('availability'),
            'endStationId': int(row.get('endStationID')),
            'dateIssued': row.get('dateIssued'),
            'dateExpired': row.get('dateExpired'),
            'dateAccepted': row.get('dateAccepted'),
            'dateCompleted': row.get('dateCompleted'),
            'numDays': int(row.get('numDays')),
            # Outstanding
            # Deleted
            # Completed
            # Failed
            # CompletedByIssuer
            # CompletedByContractor
            # Cancelled
            # Rejected
            # Reversed
            # InProgress
            'status': row.get('status'),
            'title': row.get('title'),
            'price': float(row.get('price')),
            'reward': float(row.get('reward')),
            'collateral': float(row.get('collateral')),
            'buyout': float(row.get('buyout')),
        }

    def get_rows(self, xml_string):
        try:
            e = xml.etree.ElementTree.fromstring(xml_string)
        except xml.etree.ElementTree.ParseError:
            return None

        xml_result = e[1]

        if xml_result.tag == 'error':
            print("ERROR: " + xml_result.text)
            return None

        result = []
        for row in xml_result[0]:
            result.append(row)
        return result

    def merge_api_into_contract(self, apis_with_contracts):
        result = []
        for api_id in apis_with_contracts:
            contracts = apis_with_contracts[api_id]
            for contract in contracts:
                contract['apiId'] = api_id
                result.append(contract)
        return result

    def extend_contracts_with_items(self, apis_with_contracts, apis):
        urls = self.build_contract_items_urls(apis_with_contracts, apis)
        api_response = self.external_provider.get_parallel_api_results(urls)
        for response in api_response:
            if response is None:
                continue
            items = self.parse_items(response.text)
            contract = self.find_contract_for_url(response.url, apis_with_contracts, apis)
            contract['items'] = items
        return apis_with_contracts

    def find_api_by_id(self, api_id, apis):
        for api in apis:
            if api['_id'] == api_id:
                return api
        return None

    def build_contract_items_urls(self, apis_with_contracts, apis):
        result = []
        for api_id in apis_with_contracts:
            api = self.find_api_by_id(api_id, apis)
            contracts = apis_with_contracts[api_id]
            for contract in contracts:
                # Cannot view items in a Courier Contract
                if contract['type'] == 'Courier':
                    continue

                existing_contract = MongoProvider().cursor('contracts').find_one({'contractId': contract['contractId']})

                # Do not update existing contract items to save on web requests
                if existing_contract is not None\
                        and 'items' in existing_contract\
                        and len(existing_contract['items']) > 0:
                    continue

                contract_id = contract['contractId']
                result.append(self.build_contract_items_url(api, contract_id))
        return result

    def build_contract_items_url(self, api, contract_id):
        url = 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=%d&vCode=%s&contractID=%d' \
              % (api['key'], api['vCode'], contract_id)
        return {
            'apiId': api['_id'],
            'contractId': contract_id,
            'url': url
        }

    def parse_items(self, response_text):
        items = []

        rows = self.get_rows(response_text)

        if rows is None:
            return []

        for row in rows:
            items.append({
                'recordId': int(row.get('recordID')),
                'typeId': int(row.get('typeID')),
                'quantity': int(row.get('quantity')),
                # -1: Singleton or BPO
                # -2: BPC
                'rawQuantity': int(row.get('rawQuantity')) if row.get('rawQuantity') is not None else 0,
                'singleton': int(row.get('singleton')) == 1,
                'included': int(row.get('included')) == 1,
            })
        aggregated = self.aggregate_items(items)
        return aggregated

    def aggregate_items(self, items):
        result = []
        for item in items:
            existing_item = self.find_item_by_type_id(item['typeId'], result)
            if existing_item is None:
                result.append(item)
            else:
                existing_item['quantity'] += item['quantity']
        return result

    def find_item_by_type_id(self, type_id, items):
        for item in items:
            if type_id == item['typeId']:
                return item
        return None

    def find_contract_for_url(self, url, apis_with_contracts, apis):
        api = self.find_api_from_url(url, apis)
        contract_id = self.get_contract_id_from_url(url)
        for api_id in apis_with_contracts:
            try:
                contracts_for_api = apis_with_contracts[api_id]
                result = self.find_by_contract_id(contract_id, contracts_for_api)
                return result
            except KeyError:
                continue

    def find_api_from_url(self, url, apis):
        for api in apis:
            if str(api['key']) in url and api['vCode'] in url:
                return api
        return None

    def get_contract_id_from_url(self, url):
        return int(url.split('contractID=')[1])

    def find_by_contract_id(self, contract_id, contracts):
        for contract in contracts:
            if contract['contractId'] == contract_id:
                return contract
        return None


if __name__ == '__main__':
    ContractsParser().main()
