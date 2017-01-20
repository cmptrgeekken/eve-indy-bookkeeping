
class Response:
    def __init__(self, status_code, url, text):
        self.status_code = status_code
        self.url = url
        self.text = text


class Mock:

    apis = [{'_id': 'id', 'type': 'corp', 'key': 123456, 'vCode': 'verificationCode'}]
    contract_response = Response(200, 'https://api.eveonline.com/corp/Contracts.xml.aspx?keyID=123456&vCode=verificationCode', '<eveapi version="2"><currentTime>2017-01-16 15:12:59</currentTime><result>    <rowset columns="contractID,issuerID,issuerCorpID,assigneeID,acceptorID,startStationID,endStationID,type,status,title,forCorp,availability,dateIssued,dateExpired,dateAccepted,numDays,dateCompleted,price,reward,collateral,buyout,volume" key="contractID" name="contractList">        <row title="MWD Scimitar + Kin Hardener - Rigs in cargo" volume="89000" buyout="0.00" collateral="0.00" reward="0.00" price="220000000.00" dateCompleted="2015-10-16 04:36:30" numDays="0" dateAccepted="2015-10-16 04:36:30" dateExpired="2015-10-23 15:32:31" dateIssued="2015-10-09 15:32:31" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="673319797" issuerID="91512526" contractID="97809127"/>        <row title="" volume="216000" buyout="0.00" collateral="0.00" reward="0.00" price="149000000.00" dateCompleted="2015-10-16 04:39:27" numDays="0" dateAccepted="2015-10-16 04:39:27" dateExpired="2015-10-26 03:31:21" dateIssued="2015-10-12 03:31:21" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="1941177176" issuerID="1524136743" contractID="97884327"/>        <row title="" volume="43000" buyout="0.00" collateral="0.00" reward="0.00" price="74000000.00" dateCompleted="2015-10-16 04:36:47" numDays="0" dateAccepted="2015-10-16 04:36:47" dateExpired="2015-10-28 05:30:02" dateIssued="2015-10-14 05:30:02" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="98254901" issuerID="1077170504" contractID="97937400"/>        <row title="" volume="47000" buyout="0.00" collateral="0.00" reward="0.00" price="70000000.00" dateCompleted="2015-10-16 04:37:09" numDays="0" dateAccepted="2015-10-16 04:37:09" dateExpired="2015-10-29 23:44:29" dateIssued="2015-10-15 23:44:29" availability="Private" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015108" startStationID="60015108" acceptorID="258695360" assigneeID="386292982" issuerCorpID="98416600" issuerID="92084830" contractID="97981024"/>        <row title="" volume="35900" buyout="0.00" collateral="0.00" reward="0.00" price="55000000.00" dateCompleted="2015-11-03 19:14:05" numDays="0" dateAccepted="2015-11-03 19:14:05" dateExpired="2015-11-07 22:22:47" dateIssued="2015-10-24 22:22:47" availability="Public" forCorp="0" status="Completed" type="ItemExchange" endStationID="60015106" startStationID="60015106" acceptorID="258695360" assigneeID="0" issuerCorpID="116777001" issuerID="337129922" contractID="98256398"/>    </rowset></result><cachedUntil>2017-01-16 15:39:59</cachedUntil></eveapi>')
    contract_items_response = Response(200, 'https://api.eveonline.com/corp/ContractItems.xml.aspx?keyID=123456&vCode=verificationCode&contractID=123', '<eveapi version="2"><currentTime>2017-01-16 15:12:59</currentTime><result>    <rowset columns="recordID,typeID,quantity,rawQuantity,singleton,included" key="recordID" name="itemList">        <row included="1" singleton="0" quantity="1" typeID="4310" recordID="1737516979"/>        <row included="1" singleton="0" quantity="1" typeID="35659" recordID="1737516980"/>        <row included="1" singleton="0" quantity="1" typeID="519" recordID="1737516981"/>        <row included="1" singleton="0" quantity="2" typeID="28999" recordID="1737516982"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516983"/>        <row included="1" singleton="0" quantity="1" typeID="2048" recordID="1737516984"/>        <row included="1" singleton="0" quantity="2" typeID="29001" recordID="1737516985"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516986"/>        <row included="1" singleton="0" quantity="2000" typeID="21894" recordID="1737516987"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516988"/>        <row included="1" singleton="0" quantity="1" typeID="1952" recordID="1737516989"/>        <row included="1" singleton="0" quantity="1" typeID="29009" recordID="1737516990"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516991"/>        <row included="1" singleton="0" quantity="1" typeID="1978" recordID="1737516992"/>        <row included="1" singleton="0" quantity="1" typeID="29011" recordID="1737516993"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516994"/>        <row included="1" singleton="0" quantity="1" typeID="1978" recordID="1737516995"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516996"/>        <row included="1" singleton="0" quantity="1" typeID="2605" recordID="1737516997"/>        <row included="1" singleton="0" quantity="1" typeID="2961" recordID="1737516998"/>        <row included="1" singleton="0" quantity="1" typeID="9491" recordID="1737516999"/>        <row included="1" singleton="0" quantity="1" typeID="31360" recordID="1737517000"/>        <row included="1" singleton="0" quantity="1" typeID="8529" recordID="1737517001"/>        <row included="1" singleton="0" quantity="1" typeID="519" recordID="1737517002"/>        <row included="1" singleton="0" quantity="1" typeID="31360" recordID="1737517003"/>        <row included="1" singleton="0" quantity="1" typeID="31113" recordID="1737517004"/>    </rowset></result><cachedUntil>2017-01-16 15:39:59</cachedUntil></eveapi>')
    expected_items = [
        {'typeId': 4310, 'quantity': 1},
        {'typeId': 35659, 'quantity': 1},
        {'typeId': 519, 'quantity': 2},
        {'typeId': 28999, 'quantity': 2},
        {'typeId': 2961, 'quantity': 5},
        {'typeId': 2048, 'quantity': 1},
        {'typeId': 29001, 'quantity': 2},
        {'typeId': 21894, 'quantity': 2000},
        {'typeId': 1952, 'quantity': 1},
        {'typeId': 29009, 'quantity': 1},
        {'typeId': 29011, 'quantity': 1},
        {'typeId': 9491, 'quantity': 3},
        {'typeId': 1978, 'quantity': 2},
        {'typeId': 2605, 'quantity': 1},
        {'typeId': 31360, 'quantity': 2},
        {'typeId': 8529, 'quantity': 1},
        {'typeId': 31113, 'quantity': 1},
    ]
    expected_result = [
        {
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
            'items': expected_items,
            'contractId': 97809127,
        },
        {
            'title': '',
            'volume': 216000.0,
            'reward': 0.0,
            'price': 149000000.0,
            'dateCompleted': "2015-10-16 04:39:27",
            'numDays': 0,
            'status': 'Completed',
            'type': 'ItemExchange',
            'endStationId': 60015108,
            'acceptorId': 258695360,
            'assigneeId': 386292982,
            'contractId': 97884327
        },
        {
            'title': '',
            'volume': 43000.0,
            'reward': 0.0,
            'price': 74000000.0,
            'dateCompleted': "2015-10-16 04:36:47",
            'numDays': 0,
            'status': 'Completed',
            'type': 'ItemExchange',
            'endStationId': 60015108,
            'acceptorId': 258695360,
            'assigneeId': 386292982,
            'contractId': 97937400
        },
        {
            'title': '',
            'volume': 47000.0,
            'reward': 0.0,
            'price': 70000000.0,
            'dateCompleted': "2015-10-16 04:37:09",
            'numDays': 0,
            'status': 'Completed',
            'type': 'ItemExchange',
            'endStationId': 60015108,
            'acceptorId': 258695360,
            'assigneeId': 386292982,
            'contractId': 97981024
        },
        {
            'title': '',
            'volume': 35900.0,
            'reward': 0.0,
            'price': 55000000.0,
            'dateCompleted': "2015-11-03 19:14:05",
            'numDays': 0,
            'status': 'Completed',
            'type': 'ItemExchange',
            'endStationId': 60015106,
            'acceptorId': 258695360,
            'assigneeId': 0,
            'contractId': 98256398
        }
    ]

    def expected_result_with_items(self):
        result = []
        for entry in self.expected_result:
            result.append(entry)
        for entry in result:
            entry['items'] = self.expected_items
        return result

    def expected_result_with_items_and_api_ids(self):
        result = []
        for entry in self.expected_result_with_items():
            result.append(entry)
        for entry in result:
            entry['apiId'] = 'id'
        return result

    def expected_result_without_items_and_api(self):
        result = []
        for entry in self.expected_result:
            result.append(entry)
        for entry in result:
            try:
                del entry['items']
                del entry['apiId']
            except KeyError:
                pass
        return result

    def get_apis(self):
        return self.apis

    def get_parallel_api_results(self, urls):
        result = []
        for url in urls:
            if self.is_authorized(url):
                if 'Contracts.xml.aspx' in url['url']:
                    response = Response(200, url['url'], self.contract_response.text)
                    result.append(response)
                elif 'ContractItems.xml.asp' in url['url']:
                    response = Response(200, url['url'], self.contract_items_response.text)
                    result.append(response)
                else:
                    result.append(Response(400, None, None))
            else:
                result.append(Response(400, None, None))
        return result

    def is_authorized(self, url):
        for api in self.apis:
            if str(api['key']) in url['url'] and api['vCode'] in url['url']:
                return 1
        return 0


