from web3 import Web3
from decimal import Decimal


def format_address(address):
    try:
        formatted_address = Web3.to_checksum_address(address)
        return formatted_address
    except:
        raise Exception("Invalid address format: {}".format(address))


def is_valid_address(address):
    return Web3.isAddress(address)


def get_http_provider(web_url):
    return Web3(Web3.HTTPProvider(web_url))


def to_decimal(value):
    return Decimal(str(value))


def to_wei(value, magnitude='ether'):
    return Web3.to_wei(to_decimal(str(value)), magnitude)
