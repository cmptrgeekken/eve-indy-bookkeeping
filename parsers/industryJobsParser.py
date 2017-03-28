from eveapimongo import MongoProvider
from .baseParser import BaseParser

def lambda_handler(event, context):
    IndustryJobsParser().main()
    return "done"


# industry jobs include manufacturing, copying and invention
class IndustryJobsParser(BaseParser):
    def build_url_parts(self, api):
        url_parts = [
            {'path': "/%s/IndustryJobs.xml.aspx" % api['type']},
            {'path': "/%s/IndustryJobsHistory.xmls.aspx" % api['type']}
        ]

        return url_parts

    def transform_row(self, api_result, row):
        return {
            'apiId': api_result['apiId'],
            'jobId': int(row.get('jobID')),
            'endDate': row.get('endDate'),
            'blueprintTypeId': int(row.get('blueprintTypeID')),
            'blueprintTypeName': row.get('blueprintTypeName'),
            'cost': float(row.get('cost')),
            'stationId': int(row.get('stationID')),
            'successfulRuns': int(row.get('successfulRuns'))
        }

    def filter_existing(self, documents):
        result = []
        for document in documents:
            found = MongoProvider().find_one('industryJobs', {'jobId': document['jobId']})
            # if it doesn't exist
            if found is None:
                result.append(document)
        return result

    def write(self, documents):
        cursor = MongoProvider().cursor('industryJobs')
        cursor.insert_many(documents)

if __name__ == '__main__':
    IndustryJobsParser().main()
