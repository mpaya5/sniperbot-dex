import time

from blockchain.accounting.balances import get_balance_summary
from blockchain.utils.accounting import get_interface
from blockchain.utils.chain_utils import get_chain, get_scan
from blockchain.utils.logger import setup_custom_logger


class Aggregator:
    def __init__(self):
        self.logger = setup_custom_logger('Transactions')
        pass

    def configure(self, chains_names, interfaces):
        #self.chains = [get_chain(chain_name) for chain_name in chains_names]
        self.scans = [get_scan(chain_name) for chain_name in chains_names]
        self.interfaces = [get_interface(interface) for interface in interfaces]

    def get_erc20_transactions(
            self, addresses_dict, chains_names=['ethereum', 'binance-smart-chain'],
            interfaces=['ERC20'],
            page=1, offset=10000, sort='desc'):

        self.configure(chains_names, interfaces)

        d = {}
        for address_info in addresses_dict:
            address = address_info["address"]
            start_block = address_info["start_block"] if "start_block" in address_info else ''
            end_block = address_info["end_block"] if "end_block" in address_info else ''
            self.logger.info("Retrieving ERC20 {}".format(address_info))

            d[address] = {}
            d[address]["transactions"] = {}
            for interface in self.interfaces:
                d[address]["transactions"][interface.type] = {}
                for scan in self.scans:
                    d[address]["transactions"][
                        interface.type][
                        scan.chain] = scan.get_erc20_transactions(
                        address, start_block, end_block, page, offset, sort)
        return d

    def get_normal_transactions(
            self, addresses_dict, chains_names=['ethereum', 'binance-smart-chain'],
            interfaces=['ERC20'],
            page=1, offset=10000, sort='desc'):

        self.configure(chains_names, interfaces)

        d = {}
        for address_info in addresses_dict:
            address = address_info["address"]
            start_block = address_info["start_block"] if "start_block" in address_info else ''
            end_block = address_info["end_block"] if "end_block" in address_info else ''
            self.logger.info("Retrieving Normal {}".format(address_info))

            d[address] = {}
            d[address]["transactions"] = {}
            d[address]["transactions"]['normal'] = {}
            for scan in self.scans:
                d[address]["transactions"]["normal"][
                    scan.chain] = scan.get_normal_transactions(
                    address, start_block, end_block, page, offset, sort)
        return d

    def get_internal_transactions(
            self, addresses_dict, chains_names=['ethereum', 'binance-smart-chain'],
            interfaces=['ERC20'],
            start_block='', end_block='', page=1, offset=10000, sort='desc'):

        self.configure(chains_names, interfaces)

        d = {}
        for address_info in addresses_dict:
            address = address_info["address"]
            start_block = address_info["start_block"] if "start_block" in address_info else ''
            end_block = address_info["end_block"] if "end_block" in address_info else ''
            self.logger.info("Retrieving Internal {}".format(address_info))

            d[address] = {}
            d[address]["transactions"] = {}
            d[address]["transactions"]['internal'] = {}
            for scan in self.scans:
                d[address]["transactions"]["internal"][
                    scan.chain] = scan.get_internal_transactions(
                    address, start_block, end_block, page, offset, sort)
        return d

    def merge_txs(self, txs_users_normal__, txs_users_internal__, txs_users_erc20__):
        txs_user = txs_users_normal__.copy()
        for address in txs_user.keys():
            txs_user[address]['transactions']['internal'] = txs_users_internal__[address]['transactions']['internal']
            txs_user[address]['transactions']['normal'] = txs_users_normal__[address]['transactions']['normal']
            txs_user[address]['transactions']['ERC20'] = txs_users_erc20__[address]['transactions']['ERC20']
        return txs_user

    # addresses_dict has 3 keys, address, start_block, end_block
    def get_all_txs(self, addresses_dict, chains_names=['ethereum', 'binance-smart-chain'], interfaces=['ERC20'],
                    page=1, offset=10000, sort='desc'):

        txs_users_erc20 = self.get_erc20_transactions(
            addresses_dict, chains_names, interfaces, page, offset, sort)
        txs_users_normal = self.get_normal_transactions(
            addresses_dict, chains_names, interfaces, page, offset, sort)
        txs_users_internal = self.get_internal_transactions(
            addresses_dict, chains_names, interfaces, page, offset, sort)

        txs_user = self.merge_txs(txs_users_normal, txs_users_internal, txs_users_erc20)
        return txs_user

    def get_balances(self, d):
        for address in d.keys():
            time.sleep(5)  # sleep 5 seconds between accounts, because of the rate limit
            d[address]["balances"] = {}
            for interface_name in d[address]['transactions'].keys():
                interface = get_interface(interface_name)
                d[address]["balances"][interface.type] = {}
                for chain_name in d[address]['transactions'][interface_name].keys():
                    chain = get_chain(chain_name)
                    d[address]['balances'][interface.type][chain.name] = get_balance_summary(
                        interface, chain, address, d[address]['transactions'][interface.type][chain.name]['result'])
        return d
