from eveapimongo import MongoProvider
import evelink.api
import evelink.char
import evelink.eve
from .baseParser import BaseParser


class AssetsParser(BaseParser):
    def main(self):
        for api in self.apis:
            eve_api = evelink.api.API(api_key=(int(api['key']), api['vCode']))
            corp = evelink.corp.Corp(api=eve_api)
            assets = corp.assets(flat=1)

            all_assets = self.import_assets(assets, api['_id'])

            self.write(all_assets, api['_id'])

    def import_assets(self, assets_list, api_id):
        assets = []
        for location_id in assets_list.result:
            location = self.find_location(location_id)
            for location_asset in assets_list.result[location_id]['contents']:
                item = self.find_item(location_asset['item_type_id'])
                flag = self.find_inv_flag(location_asset['location_flag'])
                location_asset['item_type_name'] = item.typeName
                location_asset['location_id'] = location_id
                location_asset['api_id'] = api_id

                if flag is not None:
                    location_asset['flag_name'] = flag.flagName

                if location is not None:
                    location_asset['location'] = location
                else:
                    location_asset['location'] = {
                        'station_name': "[Unknown: %d]" % (location_id)
                    }

                assets.append(location_asset)
        return assets

    def write(self, assets, api_id):
        cursor = MongoProvider().cursor('assetList')

        cursor.delete_many({'api_id': api_id})
        cursor.insert_many(assets)

        return

if __name__ == '__main__':
    AssetsParser().main()
