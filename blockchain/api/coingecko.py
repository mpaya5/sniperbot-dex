import requests
import time


def format_addresses(contract_addresses):
    h = ''
    for address in contract_addresses:
        h += address + '%2C'
    return h[:-3]


class Coingecko:
    def __init__(self, time_between_requests=1):
        self.base_url = 'https://api.coingecko.com/api/v3/'
        # because of the limit of the free API, we need to wait between requests
        self.time_between_requests = time_between_requests

    def request(self, query):
        time.sleep(self.time_between_requests)
        url = self.base_url + query
        response = requests.get(url)
        return response.json()

    def get_price_by_id(self, id):
        query = 'simple/price?ids={}&vs_currencies=usd'.format(id)
        return self.request(query)

    def get_price_by_contract_addresses(self, platform, contract_addresses):
        addresses = format_addresses(contract_addresses)
        query = 'simple/token_price/{}?contract_addresses={}&vs_currencies=USD'.format(platform, addresses)
        return self.request(query)

    def get_price_by_contract_address_timestamp(self, platform, contract_address, from_timestamp, to_timestamp):
        query = 'coins/{}/contract/{}/market_chart/range?vs_currency=USD&from={}&to={}'.format(
            platform, contract_address, from_timestamp, to_timestamp)
        return self.request(query)

    def get_price_by_id_timestamp(self, id, from_timestamp, to_timestamp):
        query = 'coins/{}/market_chart/range?vs_currency=USD&from={}&to={}'.format(id, from_timestamp, to_timestamp)
        return self.request(query)

    def get_coin_info(self, coin_id):
        query = 'coins/{}?tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false'.format(coin_id)
        return self.request(query)

    def get_coin_list(self):
        query = 'coins/list'
        return self.request(query)

    def get_coingecko_prices(self, page_number):
        query = 'coins/markets?vs_currency=USD&order=market_cap_desc&per_page=250&page={}&sparkline=false'.format(
            page_number)
        return self.request(query)

    def get_all_coingecko_prices(self, pages=10):
        prices = [self.get_coingecko_prices(i) for i in range(1, pages+1)]
        price_flatten = [price_asset for price_list in prices for price_asset in price_list]
        return price_flatten
