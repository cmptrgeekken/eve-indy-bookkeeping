from eveapimongo import MongoProvider
import evesde
import evelink.eve
import evelink.corp
import requests
import json


class BaseParser:
    sqlite_file = '../db/sqlite-latest.sqlite'
    citadel_lookup_endpoint = 'https://stop.hammerti.me.uk/api/citadel/%d'
    sde = evesde.StaticDataExport(sqlite_file)

    citadel_cursor = MongoProvider().cursor('citadels')
    char_cursor = MongoProvider().cursor('chars')
    corp_cursor = MongoProvider().cursor('corps')
    eve_api = evelink.eve.EVE()

    citadel_cache = {}

    def __init__(self):
        self.apis = []
        for api in MongoProvider().find('apis'):
            self.apis.append(api)

    def find_inv_flag(self, flag_id):
        return self.sde().invFlags(flagID=flag_id)

    def find_item(self, item_id):
        return self.sde().invTypes(typeID=item_id)

    def find_char_or_corp(self,id,eve_api):
        char = self.char_cursor.find_one({'id': id})
        if char is not None:
            return char['name']

        corp = self.corp_cursor.find_one({'id': id})
        if corp is not None:
            return corp['name']

        try:
            return self.find_char(id)
        except:
            return self.find_corp(id, eve_api)

    def find_char(self, char_id):
        char = self.char_cursor.find_one({'id': char_id})

        if char is None:
            char_result = self.eve_api.character_info_from_id(char_id=char_id)

            char = char_result.result
            self.char_cursor.insert(char)

        return char['name']

    def find_corp(self, corp_id, eve_api):
        corp = self.corp_cursor.find_one({'id': corp_id})

        if corp is None:
            corp_api = evelink.corp.Corp(eve_api)

            corp_result = corp_api.corporation_sheet(corp_id=corp_id)
            corp = corp_result.result

            self.corp_cursor.insert(corp)

        return corp['name']

    def find_location(self, location_id):
        loc = self.sde().staStations(stationID=location_id)

        if loc is None:
            return self.citadel_lookup(location_id)

        system = self.sde().mapSolarSystems(solarSystemID=loc.solarSystemID)
        region = self.sde().mapRegions(regionID=loc.regionID)

        return {
                'type': 'station',
                'station_name': loc.stationName,
                'region_id': loc.regionID,
                'region_name': region.regionName,
                'system_id': loc.solarSystemID,
                'system_name': system.solarSystemName,
            }

    def citadel_lookup(self, location_id):
        citadel = self.citadel_cursor.find_one({'location_id': location_id})

        if citadel is not None:
            return citadel

        url = self.citadel_lookup_endpoint % (location_id)
        rs = requests.get(url, timeout=10)

        data = json.loads(rs.text)

        if str(location_id) in data:
            loc = data[str(location_id)]
            citadel = {
                'type': 'citadel',
                'location_id': location_id,
                'station_name': loc['name'],
                'region_id': loc['regionId'],
                'region_name': loc['regionName'],
                'system_id': loc['systemId'],
                'system_name': loc['systemName'],
            }

            self.citadel_cursor.insert(citadel)

            return citadel

        return None