import unittest
from unittest import mock

from eveapimongo import MongoProvider

from functions.contractsParser.contractsParser import ContractsParser

from functions.contractsParser.contractsParser import lambda_handler


class ContractsParserTest(unittest.TestCase):
    def setUp(self):
        self.sut = ContractsParser()

    def tearDown(self):
        mock.patch.stopall()

    def test_lambda(self):
        main_method = mock.patch.object(ContractsParser, 'main').start()

        lambda_handler('event', 'context')

        self.assertEqual(main_method.call_count, 1)

    def test_main(self):
        load_apis_method = mock.patch.object(self.sut, 'load_apis', return_value="apis").start()
        api_results_method = mock.patch.object(self.sut, 'get_api_results', return_value="apiResults").start()
        transform_method = mock.patch.object(self.sut, 'transform', return_value="transformed").start()
        delete_updatable_method = mock.patch.object(self.sut, 'delete_updatable').start()
        filter_method = mock.patch.object(self.sut, 'filter_existing', return_value="filtered").start()
        write_method = mock.patch.object(self.sut, 'write').start()

        self.sut.main()

        self.assertEqual(load_apis_method.call_count, 1)
        api_results_method.assert_called_once_with("apis")
        transform_method.assert_called_once_with("apiResults")
        delete_updatable_method.assert_called_once_with("transformed")
        filter_method.assert_called_once_with("transformed")
        write_method.assert_called_once_with("filtered")

    def test_load_apis(self):
        mocked_data = [{'_id': 123, 'key': 123456}, {'_id': 312, 'key': 654321}]
        mock.patch.object(MongoProvider, 'find', return_value=mocked_data).start()
        expected = [{'_id': 123, 'key': 123456}, {'_id': 312, 'key': 654321}]

        result = self.sut.load_apis()

        self.assertEqual(expected, result)

    class MockRow:
        def __init__(self, data):
            self.data = data

        def get(self, key):
            return self.data[key]

    class MockResponse:
        def __init__(self, status_code, url, text):
            self.url = url
            self.status_code = status_code
            self.text = text

    def test_get_api_results(self):
        responses = [
            self.MockResponse(200, 'urlWithEndpoint?keyID=123456&vCode=abc&accountKey=1000', 'api_payload')
        ]
        get_result_method = mock.patch.object(self.sut, 'get_async_result', return_value=responses).start()

        expected = [{'apiId': 123, 'text': 'api_payload'}]
        apis = [{'_id': 123, 'key': 123456, 'vCode': 'abc', 'type': 'corp'}]

        result = self.sut.get_api_results(apis)

        self.assertIn(expected[0], result)
        self.assertEqual(get_result_method.call_count, 1)

    def test_build_urls(self):
        expected = [
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 321, 'url': 'https://api.eveonline.com/char/Contracts.xml.aspx?keyID=654321&vCode=cde'},
        ]
        apis = [{'_id': 123, 'key': 123456, 'vCode': 'abc', 'type': 'corp'},
                {'_id': 321, 'key': 654321, 'vCode': 'cde', 'type': 'char'}]

        result = self.sut.build_urls(apis)

        for expectation in expected:
            self.assertIn(expectation, result)

    def test_transform(self):
        api_payload = '<eveapi version="2"><currentTime>2017-01-16 19:56:26</currentTime><result>    <rowset columns="contractID,issuerID,issuerCorpID,assigneeID,acceptorID,startStationID,endStationID,type,status,title,forCorp,availability,dateIssued,dateExpired,dateAccepted,numDays,dateCompleted,price,reward,collateral,buyout,volume" key="contractID" name="contractList">        <row title="MWD Scimitar + Kin Hardener - Rigs in cargo" volume="89000" buyout="0.00" collateral="0.00" reward="0.00" price="220000000.00" dateCompleted="2015-10-16 04:36:30" numDays="0" dateAccepted="2015-10-16 04:36:30" dateExpired="2015-10-23 15:32:31" dateIssued="2015-10-09 15:32:31" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="673319797" issuerID="91512526" contractID="97809127"/>        </rowset>    </result><cachedUntil>2017-01-16 20:07:50</cachedUntil></eveapi>'
        api_results = [{'apiId': 123, 'text': api_payload}]

        expected = [{'apiId': 123, 'contractId': 97809127,
                     'title': 'MWD Scimitar + Kin Hardener - Rigs in cargo',
                     'volume': 89000.0, 'reward': 0.0, 'price': 220000000.0, 'dateCompleted': "2015-10-16 04:36:30",
                     'status': "Completed", 'type': "ItemExchange", 'endStationId': 60015108, 'numDays': 0,
                     'assigneeId': 386292982
                     }
                    ]

        result = self.sut.transform(api_results)

        self.assertEqual(expected, result)

    def test_filter_existing_is_new(self):
        documents = [{'contractId': 1}]
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value=None).start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(result, documents)
        self.assertEqual(find_method.call_count, 1)
        find_method.assert_called_with('contracts', {'contractId': 1})

    def test_filter_existing_exists(self):
        documents = [{'contractId': 1}]
        found_contract = {'status': 'Completed'}
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value=found_contract).start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(len(result), 0)
        self.assertEqual(find_method.call_count, 1)
        find_method.assert_called_with('contracts', {'contractId': 1})

    def test_delete_contracts_to_be_updated(self):
        documents = [{'contractId': 1}]
        found_contract = {'status': 'Outstanding'}
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value=found_contract).start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(len(result), 0)
        self.assertEqual(find_method.call_count, 1)
        find_method.assert_called_with('contracts', {'contractId': 1})

    class MockedCursor:
        def insert_many(self, documents):
            pass

        def delete_many(self, filter):
            pass

    def test_write(self):
        cursor_method = mock.patch.object(MongoProvider, 'cursor', return_value=self.MockedCursor()).start()

        self.sut.write([{'some': 'thing'}])

        cursor_method.assert_called_once_with('contracts')

    def test_delete_updatable(self):
        cursor = self.MockedCursor()
        delete_method = mock.patch.object(cursor, 'delete_many').start()
        cursor_method = mock.patch.object(MongoProvider, 'cursor', return_value=cursor).start()

        contracts = [{'contractId': 1}, {'contractId': 2}, {'contractId': 3}]

        self.sut.delete_updatable(contracts)

        cursor_method.assert_called_once_with('contracts')
        expected_filter = {'status': {'$in': ['Outstanding', 'InProgress']}, 'contractId': {'$in': [1, 2, 3]}}
        delete_method.assert_called_once_with(expected_filter)
