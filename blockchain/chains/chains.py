from blockchain.utils.web3_utils import format_address, get_http_provider
from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

class Chain:
    def __init__(self, web_url, name, coin, cg_ticker='', max_gwei=None, extra_gwei=None):
        self.web_url = web_url
        self.name = name
        self.coin = coin
        self.cg_ticker = cg_ticker

        self.w3 = get_http_provider(self.web_url)
        self.chain_id = self.w3.eth.chain_id

        # set gas prices configuration
        self.set_gwei_config(max_gwei, extra_gwei)
        self.get_chain_info()

    def get_chain_info(self):
        print("Connected: {}".format(self.w3.is_connected()))
        print("Chain name: {}".format(self.name))
        print("Chain id: {}".format(self.chain_id))
        print("Max gwei: {}".format(self.max_gwei))
        print("Extra gwei: {}\n".format(self.extra_gwei))

    def get_native_balance(self, account):
        return self.w3.eth.get_balance(format_address(account)) / 1e18

    def get_nonce(self, _from):
        return self.w3.eth.get_transaction_count(_from)

    def set_gwei_config(self, max_gwei, extra_gwei):
        self.max_gwei = max_gwei if max_gwei is not None else self.w3.eth.gas_price / 1e9 * 1.1
        self.extra_gwei = extra_gwei if extra_gwei is not None else 0

    def set_gwei(self):
        current_gwei = (self.w3.eth.gas_price / 1e9) + self.extra_gwei
        self.gwei = min([self.max_gwei, current_gwei])
        print("Tx gwei: ", self.gwei)

    def build_transaction(self, _from, **kwargs):
        # builting the transaction dict
        transaction = {
            'from': _from,
            'chainId': self.w3.eth.chain_id}

        if "to" in kwargs:
            transaction['to'] = format_address(kwargs["to"])

        # value is equal to 0 by default
        if "wei_value" in kwargs:
            transaction['value'] = kwargs["wei_value"]

        # gas is estimated automatically if not added
        if "gas" in kwargs:
            transaction['gas'] = kwargs["gas"]

        # if gwei is not specified, use the configured gwei
        if "gwei" in kwargs:
            transaction['gasPrice'] = self.w3.to_wei(kwargs["gwei"], 'gwei')

        else:
            self.set_gwei()
            transaction['gasPrice'] = self.w3.to_wei(self.gwei, 'gwei')

        # if nonce is not added, then it will be calculated automatically
        if "nonce" in kwargs:
            transaction['nonce'] = kwargs["nonce"]

        else:
            nonce = self.get_nonce(_from)
            transaction['nonce'] = nonce
            logger.info(f"Nonce: {nonce}")

        return transaction

    def send_transaction(self, signed_tx):
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(f"Transaction hash: {tx_hash.hex()}")
        logger.info(f"Transaction succesful: {bool(tx_receipt['status'])}")
        return tx_receipt['status'], tx_hash, tx_receipt


class EthereumChain(Chain):
    def __init__(self):
        super().__init__(web_url='https://mainnet.infura.io/v3/c1aae53026f649bcb00570de77648af8',
                         name='ethereum', coin='ETH', cg_ticker='ethereum')


class BinanceSmartChain(Chain):
    def __init__(self):
        #url = 'https://bsc-dataseed1.binance.org:443'
        url = 'https://bsc-dataseed1.ninicoin.io/'
        super().__init__(web_url=url,
                         name='binance-smart-chain', coin='BNB', cg_ticker='binancecoin')

class ArbitrumChain(Chain):
    def __init__(self):
        super().__init__(web_url='https://arb1.arbitrum.io/rpc',
                         name='arbitrum', coin='ETH', cg_ticker='ethereum')


class RopstenChain(Chain):
    def __init__(self):
        super().__init__(web_url='https://ropsten.infura.io/v3/c1aae53026f649bcb00570de77648af8',
                         name='ropsten', coin='ETH', cg_ticker='')


class RinkebyChain(Chain):
    def __init__(self):
        super().__init__(web_url='https://rinkeby.infura.io/v3/c1aae53026f649bcb00570de77648af8',
                         name='rinkeby', coin='ETH', cg_ticker='')


class BinanceSmartChainTestnet(Chain):
    def __init__(self):
        super().__init__(web_url='https://data-seed-prebsc-1-s1.binance.org:8545',
                         name='bsc-testnet', coin='BNB', cg_ticker='')


class ETHPOW(Chain):
    def __init__(self):
        super().__init__(web_url='https://mainnet.ethereumpow.org',
                         name='ethw-pow', coin='ETHW', cg_ticker='')
