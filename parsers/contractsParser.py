import evelink.api
import evelink.char
import evelink.eve
from eveapimongo import MongoProvider
from .baseParser import BaseParser
import datetime

class ContractsParser(BaseParser):
    contract_cursor = MongoProvider().cursor('contracts')

    def import_contracts(self):
        messages = []
        for api in self.apis:
            eve_api = evelink.api.API(api_key=(int(api['key']), api['vCode']))

            contract_entity = None

            if api['type'] == 'corp':
                contract_entity = evelink.corp.Corp(api=eve_api)
            elif api['type'] == 'char':
                contract_entity = evelink.char.Char(api=eve_api, char_id=int(api['charId']))
            
            api_contracts = contract_entity.contracts()

            idx = 0

            for contract_id in api_contracts.result:
                idx+=1

                contract = api_contracts.result[contract_id]
                existing_contract = self.contract_cursor.find_one({'id': contract['id']})

                if (existing_contract is None
                        or 'contract_items' not in existing_contract) \
                    and contract['type'] != 'Courier':

                    try:
                        api_contract_items = contract_entity.contract_items(contract_id=contract['id'])

                        contract_items = []

                        for contract_item in api_contract_items.result:
                            item = self.find_item(contract_item['type_id'])

                            contract_item['type_name'] = item.typeName

                            contract_items.append(contract_item)
                        contract['contract_items'] = contract_items
                    except Exception:
                        continue

                if contract['start'] > 0:
                    contract['start_location'] = self.find_location(contract['start'])

                if contract['end'] > 0:
                    contract['end_location'] = self.find_location(contract['end'])

                if contract['acceptor'] > 0:
                    contract['acceptor_name'] = self.find_char_or_corp(contract['acceptor'], eve_api)

                if contract['assignee'] > 0:
                    contract['assignee_name'] = self.find_char_or_corp(contract['assignee'], eve_api)
                else:
                    contract['assignee_name'] = 'Public'

                if contract['issuer'] > 0:
                    contract['issuer_name'] = self.find_char(contract['issuer'])

                if contract['issuer_corp'] > 0:
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
        search_filter = {'contract_items': {'$elemMatch': {'type_name': {'$regex': '.*Fuel Block'}}},
                         'status': 'Outstanding' if active else 'Completed'}
        contracts = self.contract_cursor.find(search_filter)

        fuel_blocks = {}

        value = 0

        for contract in contracts:
            value += max(contract['reward'], contract['price'])
            for contract_item in contract['contract_items']:
                type_name = contract_item['type_name']
                qty = contract_item['quantity']
                if type_name not in fuel_blocks:
                    fuel_blocks[type_name] = 0
                fuel_blocks[type_name] += qty

        message = 'Total Value: %s\r\n' % ('{:,.0f}'.format(value)) 
        for fuel_block in fuel_blocks:
            message += '%s: %s\r\n' % (fuel_block, '{:,.0f}'.format(fuel_blocks[fuel_block]))

        return message

    def write(self, contract, api_id):
        contract['api_id'] = api_id
        existing_contract = self.contract_cursor.find_one({'id': contract['id']})

        message = None
        base_message = None

        date_text = ""
        date = ""

        if contract['status'] == 'Outstanding':
            date_text = 'Created'
            date = contract['issued']
        elif 'Completed' in contract['status']:
            date_text = 'Completed'
            date = contract['completed']
        elif contract['status'] == 'InProgress':
            date_text = 'Accepted'
            date = contract['accepted']
        elif contract['status'] == 'Failed' \
            or contract['status'] == 'Cancelled' \
            or contract['status'] == 'Rejected' \
            or contract['status'] == 'Reversed' \
            or contract['status'] == 'Deleted':
            date_text = contract['status']
            date = contract['expired']

        date_str = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
        expires_str = datetime.datetime.fromtimestamp(contract['expired']).strftime('%Y-%m-%d %H:%M:%S')

        if contract['type'] == 'Courier':
            base_message = 'Courier Contract by **%s**\r\n  + %s: %s\r\n  + Expires: %s\r\n  + Note: **%s**\r\n  + Status: **%s**\r\n  + For **%s**\r\n  + From **%s**\r\n  + To **%s**\r\n  + %s m3\r\n  + %s Collateral\r\n  + %s Reward' \
                      % (contract['issuer_name'],
                         date_text,
                         date_str,
                         expires_str,
                         contract['title'],
                         contract['status'],
                         contract['assignee_name'],
                         contract['start_location']['station_name'],
                         contract['end_location']['station_name'],
                         '{:,.0f}'.format(contract['volume']),
                         '{:,.0f}'.format(contract['collateral']),
                         '{:,.0f}'.format(contract['reward']))
        elif contract['price'] > 0:
            base_message = '**%s** Contract by **%s**\r\n  + %s: %s\r\n  + Expires: %s\r\n  + Note: **%s**\r\n  + Status: **%s**\r\n  + For **%s**\r\n  + At **%s**\r\n  + Price: %s' \
                % (contract['type'],
                   contract['issuer_name'],
                   date_text,
                   date_str,
                   expires_str,
                   contract['title'],
                   contract['status'],
                   contract['assignee_name'],
                   contract['start_location']['station_name'],
                   '{:,.0f}'.format(contract['price']))
        elif contract['reward'] > 0:
            base_message = '**%s** Contract by **%s**\r\n  + %s: %s\r\n  + Expires: %s\r\n  + Note: **%s**\r\n  + Status: **%s**\r\n  + For **%s**\r\n  + At **%s**\r\n  + Reward: %s' \
                  % (contract['type'],
                     contract['issuer_name'],
                     date_text,
                     date_str,
                     expires_str,
                     contract['title'],
                     contract['status'],
                     contract['assignee_name'],
                     contract['start_location']['station_name'],
                     '{:,.0f}'.format(contract['reward']))
        contract_items = None

        if existing_contract is not None \
            and 'contract_items' in existing_contract:
            contract_items = existing_contract['contract_items']
        elif 'contract_items' in contract:
            contract_items = contract['contract_items']

        if base_message is not None and contract_items is not None:
            for item in contract_items:
                base_message += '\r\n  + %s: %s **%s**' \
                    % ('BUY' if item['action'] == 'requested' else 'SELL',
                        '{:,.0f}'.format(item['quantity']),
                         item['type_name'] )

        if existing_contract is None:
            if base_message is not None \
                and (contract['issuer_name'] != "Penny's Flying Circus" or contract['status'] != 'Outstanding'):
                message = 'New %s' % (base_message)
            self.contract_cursor.insert(contract)
        elif existing_contract['status'] != contract['status']\
            or set(existing_contract.keys()) != set(contract.keys()):
            
            if existing_contract['status'] != contract['status'] \
                and base_message is not None:
                message = 'Updated %s' % (base_message)
                
            existing_contract.update(contract)

            self.contract_cursor.remove({'id': contract['id']})
            self.contract_cursor.insert(existing_contract)
        if message is not None:
            print(message)
            if contract['type'] == 'Courier' and contract['assignee_name'] == "Penny's Flying Circus":
                return {
                    'type': 'courier',
                    'message': message
                }
            elif contract['type'] == 'ItemExchange' and contract['assignee_name'] == "Penny's Flying Circus":
                return {
                    'type': 'fuel',
                    'message': message
                }
            else:
                return {
                    'type': 'misc',
                     'message': message
                }
        return None

if __name__ == '__main__':
    ContractsParser().import_contracts()
