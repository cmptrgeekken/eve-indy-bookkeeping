import unittest
from unittest import mock

# cache timer: 30 minutes
from eveapimongo import MongoProvider

from functions.walletJournalParser.walletJournalParser import WalletJournalParser

from functions.walletJournalParser.walletJournalParser import lambda_handler


class WalletJournalParserTest(unittest.TestCase):
    def setUp(self):
        self.sut = WalletJournalParser()

    def tearDown(self):
        mock.patch.stopall()

    def test_lambda(self):
        main_method = mock.patch.object(WalletJournalParser, 'main').start()

        lambda_handler('event', 'context')

        self.assertEqual(main_method.call_count, 1)

    def test_main(self):
        load_apis_method = mock.patch.object(self.sut, 'load_apis', return_value="apis").start()
        api_results_method = mock.patch.object(self.sut, 'get_api_results', return_value="apiResults").start()
        transform_method = mock.patch.object(self.sut, 'transform', return_value="transformed").start()
        filter_method = mock.patch.object(self.sut, 'filter_irrelevant_and_existing', return_value="filtered").start()
        write_method = mock.patch.object(self.sut, 'write').start()

        self.sut.main()

        self.assertEqual(load_apis_method.call_count, 1)
        api_results_method.assert_called_once_with("apis")
        transform_method.assert_called_once_with("apiResults")
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
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1000'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1001'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1002'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1003'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1004'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1005'},
            {'apiId': 123,
             'url': 'https://api.eveonline.com/corp/WalletJournal.xml.aspx?keyID=123456&vCode=abc&accountKey=1006'},
            {'apiId': 321, 'url': 'https://api.eveonline.com/char/WalletJournal.xml.aspx?keyID=654321&vCode=cde'},
        ]
        apis = [{'_id': 123, 'key': 123456, 'vCode': 'abc', 'type': 'corp'},
                {'_id': 321, 'key': 654321, 'vCode': 'cde', 'type': 'char'}]

        result = self.sut.build_urls(apis)

        for expectation in expected:
            self.assertIn(expectation, result)

    def test_transform(self):
        api_payload = '<eveapi version="2"><currentTime>2017-01-16 19:56:26</currentTime><result><rowset name="entries" key="refID" columns="date,refID,refTypeID,ownerName1,ownerID1,ownerName2,ownerID2,argName1,argID1,amount,balance,reason,owner1TypeID,owner2TypeID"><row date="2017-01-16 17:17:25" refID="13572108307" refTypeID="54" ownerName1="Joe Beck" ownerID1="96287435" ownerName2="Secure Commerce Commission" ownerID2="1000132" argName1="" argID1="0" amount="-48000.00" balance="123" reason="" owner1TypeID="1383" owner2TypeID="2"/></rowset></result><cachedUntil>2017-01-16 20:07:50</cachedUntil></eveapi>'
        api_results = [{'apiId': 123, 'text': api_payload}]

        expected = [{'apiId': 123, 'journalId': 13572108307,
                     'timestamp': "2017-01-16 17:17:25",
                     'refTypeId': 54, 'amount': -48000.00}
                    ]

        result = self.sut.transform(api_results)

        self.assertEqual(expected, result)

    def test_filter_existing_is_new(self):
        documents = [{'journalId': 1}]
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value=None).start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(result, documents)
        self.assertEqual(find_method.call_count, 1)
        find_method.assert_called_with('walletJournal', {'journalId': 1})

    def test_filter_existing_exists(self):
        documents = [{'journalId': 1}]
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value="notNone").start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(len(result), 0)
        self.assertEqual(find_method.call_count, 1)
        find_method.assert_called_with('walletJournal', {'journalId': 1})

    def test_filter_irrelevant(self):
        documents = [{'refTypeId': -1}, {'refTypeId': 1}, {'refTypeId': 10}, {'refTypeId': 37}, {'refTypeId': 46}, {'refTypeId': 54}]

        result = self.sut.filter_irrelevant(documents)

        self.assertEqual(len(result), 5)

    class MockedCursor:
        def insert_many(self, documents):
            pass

    def test_write(self):
        cursor_method = mock.patch.object(MongoProvider, 'cursor', return_value=self.MockedCursor()).start()

        self.sut.write([{'some': 'thing'}])

        cursor_method.assert_called_once_with('walletJournal')
