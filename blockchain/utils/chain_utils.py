from blockchain.chains.chains import BinanceSmartChain, EthereumChain, ArbitrumChain, BinanceSmartChainTestnet
from blockchain.api.scanners import Etherscan, Bscscan, Arbiscan, BscscanTestnet


class StoredChain:
    def __init__(self, chain_names):
        self.chains = {}
        for chain_name in chain_names:
            self.chains[chain_name] = get_chain(chain_name)

    def get_chain(self, chain_name):
        return self.chains[chain_name]


def get_all_chain_names():
    return ['ethereum', 'binance-smart-chain','arbitrum']


def get_chain(chain_name):
    if chain_name == 'ethereum':
        chain = EthereumChain()

    elif chain_name == 'binance-smart-chain':
        chain = BinanceSmartChain()

    elif chain_name == 'arbitrum':
        chain = ArbitrumChain()

    elif chain_name == 'binance-smart-chain-testnet':
        chain = BinanceSmartChainTestnet()

    else:
        raise Exception("Chain not implemented")
    return chain


def get_scan(chain_name):
    if chain_name == 'ethereum':
        scan = Etherscan()

    elif chain_name == 'binance-smart-chain':
        scan = Bscscan()

    elif chain_name == 'arbitrum':
        scan = Arbiscan()

    elif chain_name == 'binance-smart-chain-testnet':
        scan = BscscanTestnet()

    else:
        raise Exception("Scanner not implemented")
    return scan
