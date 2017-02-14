import evelink.api
import evelink.char
import evelink.eve
from eveapimongo import MongoProvider
from functions.baseParser.baseParser import BaseParser


class ContractsParser(BaseParser):
    contract_cursor = MongoProvider().cursor('contracts')

    def import_contracts(self):
        messages = []
        for api in self.apis:
            eve_api = evelink.api.API(api_key=(int(api['key']), api['vCode']))
            corp = evelink.corp.Corp(api=eve_api)
            api_contracts = corp.contracts()

            '''
            contract = {
                'id': int(a['contractID']),
                'issuer': int(a['issuerID']),
                'issuer_corp': int(a['issuerCorpID']),
                'assignee': int(a['assigneeID']),
                'acceptor': int(a['acceptorID']),
                'start': int(a['startStationID']),
                'end': int(a['endStationID']),
                'type': a['type'],
                'status': a['status'],
                'corp': a['forCorp'] == '1',
                'availability': a['availability'],
                'issued': api.parse_ts(a['dateIssued']),
                'days': int(a['numDays']),
                'price': float(a['price']),
                'reward': float(a['reward']),
                'collateral': float(a['collateral']),
                'buyout': float(a['buyout']),
                'volume': float(a['volume']),
                'title': a['title'],
                'expired': api.parse_ts(a['dateExpired'])
                'accepted': api.parse_ts(a['dateAccepted']),
                'completed': api.parse_ts(a['dateCompleted'])
            }
            '''

            idx = 0

            for contract_id in api_contracts.result:
                idx+=1

                # if idx % 10 == 0:
                #    print('%d/%d' % (idx, len(api_contracts.result)))

                contract = api_contracts.result[contract_id]
                existing_contract = self.contract_cursor.find_one({'id': contract['id']})

                if (existing_contract is None
                        or 'contract_items' not in existing_contract) \
                    and contract['type'] != 'Courier':

                    try:
                        api_contract_items = corp.contract_items(contract_id=contract['id'])

                        contract_items = []

                        for contract_item in api_contract_items.result:
                            item = self.find_item(contract_item['type_id'])

                            contract_item['type_name'] = item.typeName

                            contract_items.append(contract_item)
                        contract['contract_items'] = contract_items
                    except Exception:
                        continue

                if contract['start'] > 0 and 'start_location' not in contract:
                    contract['start_location'] = self.find_location(contract['start'])
                if contract['end'] > 0 and 'end_location' not in contract:
                    contract['end_location'] = self.find_location(contract['end'])

                if contract['acceptor'] > 0 and 'acceptor_char' not in contract:
                    contract['acceptor_name'] = self.find_char_or_corp(contract['acceptor'], eve_api)

                if contract['assignee'] > 0 and 'assignee_name' not in contract:
                    contract['assignee_name'] = self.find_char_or_corp(contract['assignee'], eve_api)

                if contract['issuer'] > 0 and 'issuer_name' not in contract:
                    contract['issuer_name'] = self.find_char(contract['issuer'])

                if contract['issuer_corp'] > 0 and 'issuer_corp_name' not in contract:
                    contract['issuer_corp_name'] = self.find_corp(contract['issuer_corp'], eve_api)

                if contract['issuer_corp'] == api['corpId']:
                    contract['is_issuer'] = True
                else:
                    contract['is_issuer'] = False

                message = self.write(contract, api['_id'])
                if message is not None:
                    messages.append(message)

        return messages

    def summarize_fuel(self, active):
        search_filter = {'contract_items': {'$elemMatch': {'type_name': {'$regex': '/.*Fuel Block/'}}},
                         'status': 'Outstanding' if active else 'Completed'}
        contracts = self.contract_cursor.find(search_filter)

        return contracts

    def write(self, contract, api_id):
        contract['api_id'] = api_id
        existing_contract = self.contract_cursor.find_one({'id': contract['id']})

        if existing_contract is None:
            '''TODO: Trigger event'''
            message = None

            if not contract['is_issuer'] \
                    and contract['status'] == 'Outstanding':
                if contract['type'] == 'Courier':
                    message = 'New Courier Contract by **%s** from **%s** to **%s** (%d m3, %s Collateral, %s Reward)' \
                              % (contract['issuer_name'],
                                 contract['start_location']['station_name'],
                                 contract['end_location']['station_name'],
                                 contract['volume'],
                                 '{:,.0f}'.format(contract['collateral']),
                                 '{:,.0f}'.format(contract['reward']))
                elif contract['price'] > 0:
                    message = 'New **%s** Contract by **%s** at **%s** (Price: %s)' \
                        % (contract['type'],
                           contract['issuer_name'],
                           contract['start_location']['station_name'],
                           '{:,.0f}'.format(contract['price']))
                elif contract['reward'] > 0:
                    message = 'New **%s** Contract by **%s** at **%s** (Reward: %s)' \
                          % (contract['type'],
                             contract['issuer_name'],
                             contract['start_location']['station_name'],
                             '{:,.0f}'.format(contract['reward']))

                if 'contract_items' in contract:
                    for item in contract['contract_items']:
                        message += '\r\n  * %d %s (%s)' % (item['quantity'],
                                                         item['type_name'],
                                                         item['action'])

            self.contract_cursor.insert(contract)

            if message is not None:
                print(message)

            return message

        elif existing_contract['status'] != contract['status']\
            or ('contract_items' in contract and 'contract_items' not in existing_contract)\
            or set(existing_contract.keys()) != set(contract.keys()):

            if existing_contract['status'] != contract['status']:
                '''TODO: Trigger event'''
                print("Status changed!")

            existing_contract.update(contract)

            self.contract_cursor.remove({'id': contract['id']})
            self.contract_cursor.insert(existing_contract)

if __name__ == '__main__':
    ContractsParser().import_contracts()
