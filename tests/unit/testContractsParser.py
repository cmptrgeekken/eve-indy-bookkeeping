import unittest
from unittest import mock

from functions.contractsParser.contractsParser import ContractsParser
from functions.contractsParser.contractsParser import lambda_handler
from .contractsExternalProviderMock import Mock


class Response:
    def __init__(self, status_code, url, text):
        self.status_code = status_code
        self.url = url
        self.text = text


class ContractsParserTest(unittest.TestCase):
    def setUp(self):
        self.sut = ContractsParser()
        self.provider_mock = Mock()
        self.sut.external_provider = self.provider_mock

    def tearDown(self):
        mock.patch.stopall()

    def test_lambda(self):
        main_method = mock.patch.object(ContractsParser, 'main').start()

        lambda_handler('event', 'context')

        self.assertEqual(main_method.call_count, 1)

    class Matcher(object):
        def __init__(self, compare, some_obj):
            self.compare = compare
            self.some_obj = some_obj

        def __eq__(self, other):
            return self.compare(self.some_obj, other)

    def test_main(self):
        write_method = mock.patch.object(self.sut, 'write').start()

        self.sut.main()

        # args = write_method.call_args
        k_all = write_method.mock_calls[0]
        self.assertIsNotNone(k_all)
        name, args, kwargs = k_all

        args_ = args[0]
        expected = self.provider_mock.expected_result_with_items_and_api_ids()
        self.assertEqual(len(expected), len(args_))
        self.assertEqual(len(str(expected)), len(str(args_)))

    def test_get_contracts(self):
        expected_result = {'id': []}
        self.maxDiff = None
        for contract in self.sut.external_provider.expected_result_without_items_and_api():
            expected_result['id'].append(contract)

        result = self.sut.get_contracts(self.sut.external_provider.apis)
        self.assertEqual(expected_result, result)

    def test_build_contract_urls(self):
        expected = [
            {'apiId': 'id',
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=verificationCode'},
        ]
        result = self.sut.build_contract_urls(self.sut.external_provider.apis)
        self.assertEqual(expected, result)

        char_apis = [{'type': 'char', '_id': '2', 'key': 1337, 'vCode': 'hola'}]
        expected = [
            {'apiId': '2',
             'url': 'https://api.eveonline.com/char/Contracts.xml.aspx?keyID=1337&vCode=hola'},
        ]
        result = self.sut.build_contract_urls(char_apis)
        self.assertEqual(expected, result)

    def test_build_api_verification(self):
        expected = "keyID=123456&vCode=verificationCode"
        result = self.sut.build_api_verifications(self.sut.external_provider.apis[0])
        self.assertEqual(expected, result)

        expected = "keyID=1&vCode=test"
        api = {'key': 1, 'vCode': 'test'}
        result = self.sut.build_api_verifications(api)
        self.assertEqual(expected, result)

    def test_transform_contract_responses_to_contracts(self):
        self.maxDiff = None
        apis_with_responses = {'1': self.sut.external_provider.contract_response}
        expected = {'1': self.sut.external_provider.expected_result_without_items_and_api()}

        result = self.sut.transform_contract_responses_to_contracts(apis_with_responses)

        self.assertIsNotNone(result)
        for expect in expected:
            self.assertIn(expect, result)

    def test_transform_contract_response_to_contracts(self):
        # todo: handling of response with status code != 200
        # todo: response with 0 rows
        expected_result = self.provider_mock.expected_result_without_items_and_api()
        response = self.sut.external_provider.contract_response

        result = self.sut.transform_contract_response_to_contracts(response)

        self.assertIsNotNone(result)
        self.assertEqual(len(expected_result), len(result))
        for el in expected_result:
            self.assertIn(el, result)

    def test_get_rows(self):
        xml_string = self.sut.external_provider.contract_response.text

        result = self.sut.get_rows(xml_string)

        self.assertEqual(5, len(result))
        import xml.etree.ElementTree as ET
        self.assertEqual(result[0].attrib, ET.fromstring(
            '<row title="MWD Scimitar + Kin Hardener - Rigs in cargo" volume="89000" buyout="0.00" collateral="0.00" reward="0.00" price="220000000.00" dateCompleted="2015-10-16 04:36:30" numDays="0" dateAccepted="2015-10-16 04:36:30" dateExpired="2015-10-23 15:32:31" dateIssued="2015-10-09 15:32:31" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="673319797" issuerID="91512526" contractID="97809127"/>').attrib)
        self.assertEqual(result[1].attrib, ET.fromstring(
            '<row title="" volume="216000" buyout="0.00" collateral="0.00" reward="0.00" price="149000000.00" dateCompleted="2015-10-16 04:39:27" numDays="0" dateAccepted="2015-10-16 04:39:27" dateExpired="2015-10-26 03:31:21" dateIssued="2015-10-12 03:31:21" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="1941177176" issuerID="1524136743" contractID="97884327"/>').attrib)
        self.assertEqual(result[2].attrib, ET.fromstring(
            '<row title="" volume="43000" buyout="0.00" collateral="0.00" reward="0.00" price="74000000.00" dateCompleted="2015-10-16 04:36:47" numDays="0" dateAccepted="2015-10-16 04:36:47" dateExpired="2015-10-28 05:30:02" dateIssued="2015-10-14 05:30:02" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="98254901" issuerID="1077170504" contractID="97937400"/>').attrib)
        self.assertEqual(result[3].attrib, ET.fromstring(
            '<row title="" volume="47000" buyout="0.00" collateral="0.00" reward="0.00" price="70000000.00" dateCompleted="2015-10-16 04:37:09" numDays="0" dateAccepted="2015-10-16 04:37:09" dateExpired="2015-10-29 23:44:29" dateIssued="2015-10-15 23:44:29" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="98416600" issuerID="92084830" contractID="97981024"/>').attrib)
        self.assertEqual(result[4].attrib, ET.fromstring(
            '<row title="" volume="35900" buyout="0.00" collateral="0.00" reward="0.00" price="55000000.00" dateCompleted="2015-11-03 19:14:05" numDays="0" dateAccepted="2015-11-03 19:14:05" dateExpired="2015-11-07 22:22:47" dateIssued="2015-10-24 22:22:47" availability="Public" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015106" startStationID="60015106" acceptorID="258695360" assigneeID="0" issuerCorpID="116777001" issuerID="337129922" contractID="98256398"/>').attrib)

    def test_create_contract_from_row(self):
        # this is the same like self.sut.external_provider.expected_result[0], but without the items
        expected = {
            'title': 'MWD Scimitar + Kin Hardener - Rigs in cargo',
            'volume': 89000.0,
            'reward': 0.0,
            'price': 220000000.0,
            'dateCompleted': "2015-10-16 04:36:30",
            'numDays': 0,
            'status': 'Completed',
            'type': 'ItemExchange',
            'endStationId': 60015108,
            'acceptorId': 258695360,
            'assigneeId': 386292982,
            'contractId': 97809127
        }

        import xml.etree.ElementTree as ET
        row = ET.fromstring(
            '<row title="MWD Scimitar + Kin Hardener - Rigs in cargo" volume="89000" buyout="0.00" collateral="0.00" reward="0.00" price="220000000.00" dateCompleted="2015-10-16 04:36:30" numDays="0" dateAccepted="2015-10-16 04:36:30" dateExpired="2015-10-23 15:32:31" dateIssued="2015-10-09 15:32:31" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="673319797" issuerID="91512526" contractID="97809127"/>')

        result = self.sut.create_contract_from_row(row)

        self.assertEqual(expected, result)

    def test_create_dict_with_apis_and_responses(self):
        apis = [{'_id': '1', 'key': 123456, 'vCode': 'firstCode'}, {'_id': '2', 'key': 654321, 'vCode': 'secondCode'}]
        responses = [Response(200, 'url?key=123456&vCode=firstCode', 'test'),
                     Response(200, 'url?key=654321&vCode=secondCode', 'test')]
        expected = {'1': responses[0], '2': responses[1]}

        result = self.sut.create_dict_with_apis_and_responses(responses, apis)

        self.assertEqual(expected, result)

    def test_merge_api_into_contracts(self):
        input_data = {'some_id_1': [{'contractId': 1}, {'contractId': 2}],
                      'some_id_2': [{'contractId': 3}],
                      'some_id_3': []}
        expected = [{'apiId': 'some_id_1', 'contractId': 1}, {'apiId': 'some_id_1', 'contractId': 2},
                    {'apiId': 'some_id_2', 'contractId': 3}]

        result = self.sut.merge_api_into_contract(input_data)

        for contract in expected:
            self.assertIn(contract, result)

    def test_extend_contracts_with_items(self):
        self.maxDiff = None
        input_data = {'id': [{'contractId': 123}]}

        result = self.sut.extend_contracts_with_items(input_data, self.provider_mock.apis)
        result_contracts = result['id']
        for item in self.provider_mock.expected_items:
            self.assertIn(item, result_contracts[0]['items'])

    def test_get_api_by_id(self):
        needle = 'some_id'
        haystack = [{'_id': 'some_id', 'key': 'match'}, {'_id': 'some_other_id', 'key': 'noMatch'}]

        result = self.sut.find_api_by_id(needle, haystack)

        self.assertEqual(haystack[0], result)

    def test_get_api_by_id_no_match(self):
        needle = 'some_id'
        haystack = [{'_id': 'no_match', 'key': 'match'}, {'_id': 'some_other_id', 'key': 'noMatch'}]

        result = self.sut.find_api_by_id(needle, haystack)

        self.assertIsNone(result)

    def test_build_contract_items_url(self):
        expected = {
            'apiId': 'id',
            'contractId': 97884327,
            'url': 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456'
                   '&vCode=verificationCode&contractID=97884327'
        }

        api = {'_id': 'id', 'type': 'corp', 'key': 123456, 'vCode': 'verificationCode'}
        result = self.sut.build_contract_items_url(api, 97884327)

        self.assertEqual(expected, result)

        # second run
        expected = {
            'apiId': 'id',
            'contractId': 123456,
            'url': 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=312'
                   '&vCode=code&contractID=123456'
        }

        api = {'_id': 'id', 'type': 'corp', 'key': 312, 'vCode': 'code'}
        result = self.sut.build_contract_items_url(api, 123456)

        self.assertEqual(expected, result)

    def test_build_contract_items_urls(self):
        expected = [
            {
                'apiId': 'id',
                'contractId': 97884327,
                'url': 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456'
                       '&vCode=verificationCode&contractID=97884327'
            },
            {
                'apiId': 'id',
                'contractId': 123456,
                'url': 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456'
                       '&vCode=verificationCode&contractID=123456'
            }
        ]
        input_data = {
            'id': [{'contractId': 97884327}, {'contractId': 123456}]
        }

        result = self.sut.build_contract_items_urls(input_data, self.provider_mock.apis)

        self.assertIsNotNone(result)
        for entry in expected:
            self.assertIn(entry, result)

    def test_parse_items(self):
        self.maxDiff = None
        response_text = '<eveapi version="2"><currentTime>2017-01-16 15:12:59</currentTime><result>    <rowset columns="recordID,typeID,quantity,rawQuantity,singleton,included" key="recordID" name="itemList">        <row included="1" singleton="0" quantity="1" typeID="4310" recordID="1737516979"/>        <row included="1" singleton="0" quantity="1" typeID="35659" recordID="1737516980"/>        <row included="1" singleton="0" quantity="1" typeID="519" recordID="1737516981"/>        <row included="1" singleton="0" quantity="2" typeID="28999" recordID="1737516982"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516983"/>        <row included="1" singleton="0" quantity="1" typeID="2048" recordID="1737516984"/>        <row included="1" singleton="0" quantity="2" typeID="29001" recordID="1737516985"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516986"/>        <row included="1" singleton="0" quantity="2000" typeID="21894" recordID="1737516987"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516988"/>        <row included="1" singleton="0" quantity="1" typeID="1952" recordID="1737516989"/>        <row included="1" singleton="0" quantity="1" typeID="29009" recordID="1737516990"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516991"/>        <row included="1" singleton="0" quantity="1" typeID="1978" recordID="1737516992"/>        <row included="1" singleton="0" quantity="1" typeID="29011" recordID="1737516993"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516994"/>        <row included="1" singleton="0" quantity="1" typeID="1978" recordID="1737516995"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516996"/>        <row included="1" singleton="0" quantity="1" typeID="2605" recordID="1737516997"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516998"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516999"/>        <row included="1" singleton="0" quantity="1" typeID="31360" recordID="1737517000"/>        <row included="1" singleton="0" quantity="1" typeID="8529" recordID="1737517001"/>        <row included="1" singleton="0" quantity="1" typeID="519" recordID="1737517002"/>        <row included="1" singleton="0" quantity="1" typeID="31360" recordID="1737517003"/>        <row included="1" singleton="0" quantity="1" typeID="31113" recordID="1737517004"/>    </rowset></result><cachedUntil>2017-01-16 15:39:59</cachedUntil></eveapi>'
        expected = self.provider_mock.expected_items

        result = self.sut.parse_items(response_text)

        for entry in expected:
            self.assertIn(entry, result)

    def test_aggregate_items(self):
        self.maxDiff = None

        items = [{'quantity': 1, 'typeId': 2961},
                 {'quantity': 1, 'typeId': 35659},
                 {'quantity': 1, 'typeId': 2961},
                 {'quantity': 2, 'typeId': 28999},
                 {'quantity': 1, 'typeId': 2961}]
        expected = [{'quantity': 1, 'typeId': 35659},
                    {'quantity': 2, 'typeId': 28999},
                    {'quantity': 3, 'typeId': 2961}]

        result = self.sut.aggregate_items(items)

        self.assertIsNotNone(result)
        for entry in expected:
            self.assertIn(entry, items)

    def test_find_item_by_type_id(self):
        items = [{'quantity': 1, 'typeId': 35659}]
        needle_positive = 35659
        needle_negative = -1

        result_positive = self.sut.find_item_by_type_id(needle_positive, items)
        self.assertIsNotNone(result_positive)
        self.assertEqual(result_positive, items[0])

        result_negative = self.sut.find_item_by_type_id(needle_negative, items)
        self.assertIsNone(result_negative)

    def test_find_contract_for_url(self):
        apis_with_contracts = {'id': [{'contractId': 123}]}
        apis = self.provider_mock.apis
        url = 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456&vCode=verificationCode&contractID=123'

        result = self.sut.find_contract_for_url(url, apis_with_contracts, apis)

        self.assertEqual({'contractId': 123}, result)

        # second run
        url = 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456&vCode=verificationCode&contractID=97809127'
        apis = [{'_id': 'id', 'key': 123456, 'vCode': 'verificationCode', 'type': 'corp'}]
        apis_with_contracts = {'id': [
            {'type': 'ItemExchange', 'status': 'Completed', 'dateCompleted': '2015-10-16 04:36:30',
             'assigneeId': 386292982, 'reward': 0.0, 'price': 220000000.0, 'numDays': 0, 'contractId': 97809127,
             'acceptorId': 258695360, 'title': 'MWD Scimitar + Kin Hardener - Rigs in cargo', 'endStationId': 60015108,
             'volume': 89000.0}, {'type': 'ItemExchange', 'status': 'Completed', 'dateCompleted': '2015-10-16 04:39:27',
                                  'assigneeId': 386292982, 'reward': 0.0, 'price': 149000000.0, 'numDays': 0,
                                  'contractId': 97884327, 'acceptorId': 258695360, 'title': '',
                                  'endStationId': 60015108, 'volume': 216000.0},
            {'type': 'ItemExchange', 'status': 'Completed', 'dateCompleted': '2015-10-16 04:36:47',
             'assigneeId': 386292982, 'reward': 0.0, 'price': 74000000.0, 'numDays': 0, 'contractId': 97937400,
             'acceptorId': 258695360, 'title': '', 'endStationId': 60015108, 'volume': 43000.0},
            {'type': 'ItemExchange', 'status': 'Completed', 'dateCompleted': '2015-10-16 04:37:09',
             'assigneeId': 386292982, 'reward': 0.0, 'price': 70000000.0, 'numDays': 0, 'contractId': 97981024,
             'acceptorId': 258695360, 'title': '', 'endStationId': 60015108, 'volume': 47000.0},
            {'type': 'ItemExchange', 'status': 'Completed', 'dateCompleted': '2015-11-03 19:14:05', 'assigneeId': 0,
             'reward': 0.0, 'price': 55000000.0, 'numDays': 0, 'contractId': 98256398, 'acceptorId': 258695360,
             'title': '', 'endStationId': 60015106, 'volume': 35900.0}]}

        result = self.sut.find_contract_for_url(url, apis_with_contracts, apis)

        self.assertEqual(97809127, result['contractId'])

    def test_find_url_from_api(self):
        url = 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456&vCode=verificationCode&contractID=123'
        apis = [
            {
                '_id': '1',
                'key': 123456,
                'vCode': 'nothing'
            },
            {
                '_id': 'abc',
                'key': 123456,
                'vCode': 'verificationCode'
            }
        ]

        result = self.sut.find_api_from_url(url, apis)

        self.assertEqual(apis[1], result)

    def test_get_contract_id_from_url(self):
        url = 'someUrl?keyID=123456&vCode=verificationCode&contractID=123'

        result = self.sut.get_contract_id_from_url(url)

        self.assertEqual(123, result)

    def test_find_by_contract_id(self):
        contracts = [{'contractId': 3123, 'sth': 'sth'}, {'contractId': 123, 'sth': 'sth'}]
        contract_id = 123

        result = self.sut.find_by_contract_id(contract_id, contracts)

        self.assertEqual(contracts[1], result)

    def test_find_contract_for_url_should_not_return_none(self):
        response_url = 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456&vCode=verificationCode&contractID=97809127'
        apis_with_contracts = {'id': [
            {'status': 'Completed', 'title': 'MWD Scimitar + Kin Hardener - Rigs in cargo', 'type': 'ItemExchange',
             'assigneeId': 386292982, 'reward': 0.0, 'acceptorId': 258695360, 'endStationId': 60015108,
             'price': 220000000.0, 'volume': 89000.0, 'dateCompleted': '2015-10-16 04:36:30', 'contractId': 97809127,
             'numDays': 0},
            {'status': 'Completed', 'title': '', 'type': 'ItemExchange', 'assigneeId': 386292982, 'reward': 0.0,
             'acceptorId': 258695360, 'endStationId': 60015108, 'price': 149000000.0, 'volume': 216000.0,
             'dateCompleted': '2015-10-16 04:39:27', 'contractId': 97884327, 'numDays': 0},
            {'status': 'Completed', 'title': '', 'type': 'ItemExchange', 'assigneeId': 386292982, 'reward': 0.0,
             'acceptorId': 258695360, 'endStationId': 60015108, 'price': 74000000.0, 'volume': 43000.0,
             'dateCompleted': '2015-10-16 04:36:47', 'contractId': 97937400, 'numDays': 0},
            {'status': 'Completed', 'title': '', 'type': 'ItemExchange', 'assigneeId': 386292982, 'reward': 0.0,
             'acceptorId': 258695360, 'endStationId': 60015108, 'price': 70000000.0, 'volume': 47000.0,
             'dateCompleted': '2015-10-16 04:37:09', 'contractId': 97981024, 'numDays': 0},
            {'status': 'Completed', 'title': '', 'type': 'ItemExchange', 'assigneeId': 0, 'reward': 0.0,
             'acceptorId': 258695360, 'endStationId': 60015106, 'price': 55000000.0, 'volume': 35900.0,
             'dateCompleted': '2015-11-03 19:14:05', 'contractId': 98256398, 'numDays': 0}]}
        apis = [{'vCode': 'verificationCode', 'key': 123456, 'type': 'corp', '_id': 'id'}]

        result = self.sut.find_contract_for_url(response_url, apis_with_contracts, apis)

        self.assertIsNotNone(result)
