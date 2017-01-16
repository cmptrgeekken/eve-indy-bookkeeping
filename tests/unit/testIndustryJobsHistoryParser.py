import unittest
from unittest import mock

from eveapimongo import MongoProvider

from functions.industryJobsHistoryParser.industryJobsHistoryParser import IndustryJobsHistoryParser

from functions.industryJobsHistoryParser.industryJobsHistoryParser import lambda_handler


class IndustryJobsHistoryTest(unittest.TestCase):
    def setUp(self):
        self.sut = IndustryJobsHistoryParser()

    def tearDown(self):
        mock.patch.stopall()

    def test_lambda(self):
        main_method = mock.patch.object(IndustryJobsHistoryParser, 'main').start()

        lambda_handler('event', 'context')

        self.assertEqual(main_method.call_count, 1)

    def test_main(self):
        load_apis_method = mock.patch.object(self.sut, 'load_apis', return_value="apis").start()
        api_results_method = mock.patch.object(self.sut, 'get_api_results', return_value="apiResults").start()
        transform_method = mock.patch.object(self.sut, 'transform', return_value="transformed").start()
        filter_method = mock.patch.object(self.sut, 'filter_existing', return_value="filtered").start()
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
            self.MockResponse(200, 'urlWithEndpoint?keyID=123456&vCode=abc', 'api_payload')
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
             'url': 'https://api.eveonline.com/corp/IndustryJobsHistory.xml.aspx?keyID=123456&vCode=abc'},
            {'apiId': 321, 'url': 'https://api.eveonline.com/char/IndustryJobsHistory.xml.aspx?keyID=654321&vCode=cde'},
        ]
        apis = [{'_id': 123, 'key': 123456, 'vCode': 'abc', 'type': 'corp'},
                {'_id': 321, 'key': 654321, 'vCode': 'cde', 'type': 'char'}]

        result = self.sut.build_urls(apis)

        for expectation in expected:
            self.assertIn(expectation, result)

    def test_transform(self):
        api_payload = '<eveapi version="2"><currentTime>2017-01-16 15:12:59</currentTime><result>    <rowset name="jobs" key="jobID" columns="jobID,installerID,installerName,facilityID,solarSystemID,solarSystemName,stationID,activityID,blueprintID,blueprintTypeID,blueprintTypeName,blueprintLocationID,outputLocationID,runs,cost,teamID,licensedRuns,probability,productTypeID,productTypeName,status,timeInSeconds,startDate,endDate,pauseDate,completedDate,completedCharacterID,successfulRuns">        <row jobID="229136101" installerID="498338451" installerName="Qoi" facilityID="60006382" solarSystemID="30005194"              solarSystemName="Cleyd" stationID="60006382" activityID="1" blueprintID="1015116533326"             blueprintTypeID="2047" blueprintTypeName="Damage Control I Blueprint" blueprintLocationID="60006382"              outputLocationID="60006382" runs="1" cost="118.00" teamID="0" licensedRuns="200" probability="0"             productTypeID="0" productTypeName="" status="1" timeInSeconds="548"             startDate="2014-07-19 15:47:06" endDate="2014-07-19 15:56:14" pauseDate="0001-01-01 00:00:00"             completedDate="0001-01-01 00:00:00" completedCharacterID="0" successfulRuns="1"/>             </rowset></result><cachedUntil>2017-01-16 15:39:59</cachedUntil></eveapi>'
        api_results = [{'apiId': 123, 'text': api_payload}]

        expected = [{'apiId': 123, 'jobId': 229136101,
                     'endDate': "2014-07-19 15:56:14",
                     'blueprintTypeId': 2047,
                     'blueprintTypeName': "Damage Control I Blueprint",
                     'cost': 118.0,
                     'stationId': 60006382,
                     'successfulRuns': 1}
                    ]

        result = self.sut.transform(api_results)

        self.assertEqual(expected, result)

    def test_filter_existing_is_new(self):
        documents = [{'jobId': 1}]
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value=None).start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(result, documents)
        self.assertEqual(find_method.call_count, 1)

    def test_filter_existing_exists(self):
        documents = [{'jobId': 1}]
        find_method = mock.patch.object(MongoProvider, 'find_one', return_value="notNone").start()

        result = self.sut.filter_existing(documents)

        self.assertEqual(len(result), 0)
        self.assertEqual(find_method.call_count, 1)

    class MockedCursor:
        def insert_many(self, documents):
            pass

    def test_write(self):
        cursor_method = mock.patch.object(MongoProvider, 'cursor', return_value=self.MockedCursor()).start()

        self.sut.write([{'some': 'thing'}])

        cursor_method.assert_called_once_with('industryJobs')
