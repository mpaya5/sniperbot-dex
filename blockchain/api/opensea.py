import requests

from config import OPENSEA_API_KEY

get_floor = lambda response: response['collection']['stats']['floor_price']
get_smart_contract = lambda response : response['collection']['primary_asset_contracts'][0]['address']

get_cost = lambda asset : float(asset['last_sale']['total_price']) / 1e18 if asset['last_sale'] is not None else 0
get_slug = lambda asset : asset['collection']['slug']
get_traits = lambda asset : asset['traits']
get_id = lambda asset : asset['token_id']

class OpenSeaAPI:
    def __init__(self):
        self.base_url = 'https://api.opensea.io/api/v1/'
        
    def request(self, query):
        url = self.base_url + query
        try:
            response = requests.get(url).json()
        except:
            raise Exception("Invalid query: {}".format(url))
        return response
        
    def get_collection_info(self, collection_id):
        query = "collection/{}".format(collection_id)
        return self.request(query)

    def get_collections_info(self, slugs):
        responses = [self.get_collection_info(slug) for slug in slugs]
        floors = [get_floor(response) for response in responses]
        contract_address = [get_smart_contract(response) for response in responses]

        info_dict = {}
        for i in range(len(slugs)):
            info_dict[slugs[i]] = {}
            info_dict[slugs[i]]["floor"] = floors[i]
            info_dict[slugs[i]]["address"] = contract_address[i]
        return info_dict