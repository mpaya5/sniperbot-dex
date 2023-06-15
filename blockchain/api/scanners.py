import requests
# import time #if too many request then we have to limit the request function
import os
from dotenv import load_dotenv
load_dotenv()

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')

# I do not achieve to extract more than 10,000 for a address, page and offset not working as expected

class Scanner:
    def request(self, query):
        url = self.base_url + query
        try:
            response = requests.get(url).json()
            if response['message'] == "NOTOK":
                raise Exception("{}\n{}".format(response['result'], query))
        except:
            raise Exception("Invalid query: {}".format(url))
        return response

    def get_normal_transactions(self, address, start_block='', end_block='',
                                page=1, offset=10000, sort='desc'):
        query = 'api?module=account&action=txlist&address={}&page={}&offset={}&startblock={}&endblock={}&sort={}&apikey={}'.format(
            address, page, offset, start_block, end_block, sort, self.api_key)
        return self.request(query)

    def get_erc20_transactions(self, address, start_block='', end_block='',
                               page=1, offset=10000, sort='desc'):
        query = 'api?module=account&action=tokentx&address={}&page={}&offset={}&startblock={}&endblock={}&sort={}&apikey={}'.format(
            address, page, offset, start_block, end_block, sort, self.api_key)
        return self.request(query)

    def get_internal_transactions(self, address, start_block='', end_block='',
                                  page=1, offset=10000, sort='desc'):
        query = 'api?module=account&action=txlistinternal&address={}&page={}&offset={}&startblock={}&endblock={}&sort={}&apikey={}'.format(
            address, page, offset, start_block, end_block, sort, self.api_key)
        return self.request(query)

    def get_erc721_transactions(self, address, start_block='', end_block='',
                                page=1, offset=10000, sort='desc'):
        query = 'api?module=account&action=tokennfttx&address={}&page={}&offset={}&startblock={}&endblock={}&sort={}&apikey={}'.format(
            address, page, offset, start_block, end_block, sort, self.api_key)
        return self.request(query)

    def get_erc1155_transactions(self, address, start_block='', end_block='',
                                 page=1, offset=10000, sort='desc'):
        query = 'api?module=account&action=token1155tx&address={}&page={}&offset={}&startblock={}&endblock={}&sort={}&apikey={}'.format(
            address, page, offset, start_block, end_block, sort, self.api_key)
        return self.request(query)

    def get_abi(self, contract_address):
        query = 'api?module=contract&action=getabi&address={}&apikey={}'.format(contract_address, self.api_key)
        return self.request(query)


class Etherscan(Scanner):
    def __init__(self):
        self.base_url = 'https://api.etherscan.io/'
        self.api_key = ETHERSCAN_API_KEY
        self.chain = 'ethereum'


class Bscscan(Scanner):
    def __init__(self):
        self.base_url = 'https://api.bscscan.com/'
        self.api_key = BSCSCAN_API_KEY
        self.chain = 'binance-smart-chain'

class Arbiscan(Scanner):
    def __init__(self):
        self.base_url = 'https://api.arbiscan.io/'
        self.api_key = ARBISCAN_API_KEY
        self.chain = 'arbitrum'

class BscscanTestnet(Scanner):
    def __init__(self):
        self.base_url = 'https://api-testnet.bscscan.com/'
        self.api_key = BSCSCAN_API_KEY
        self.chain = 'binance-smart-chain-testnet'
