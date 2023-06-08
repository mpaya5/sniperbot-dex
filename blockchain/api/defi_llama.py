import requests
# import time #if too many request then we have to limit the request function
import time

# I do not achieve to extract more than 10,000 for a address, page and offset not working as expected


class DefiLlama:
    def __init__(self):
        self.base_url = 'https://coins.llama.fi/'

    def request(self, query, time_sleep=None):
        url = self.base_url + query
        response = requests.get(url).json()
        #if response['message'] == "NOTOK": raise Exception("{}".format(response['result']))
        if time_sleep is not None:
            time.sleep(0.05)
        return response

    def get_historical_prices(self, coins_formatted, timestamp):
        query = 'prices/historical/{}/{}'.format(timestamp, coins_formatted)
        return self.request(query)

    def get_current_prices(self, coins_formatted):
        query = 'prices/current/{}'.format(coins_formatted)
        return self.request(query)
