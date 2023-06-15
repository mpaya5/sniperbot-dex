import pandas as pd
from datetime import datetime

import boto3
import base64
import json

import os
from dotenv import load_dotenv
load_dotenv()

from web3 import Web3
import pandas as pd
from decimal import Decimal

from blockchain.chains.chains import BinanceSmartChain
from blockchain.contracts.interfaces.erc20 import ERC20Contract
from blockchain.contracts.dex.pancake_contract import PancakeContract
from blockchain.api.scanners import Bscscan

from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

from blockchain.utils.utils import send_transaction
from blockchain.utils.chain_utils import get_chain
from blockchain.utils.web3_utils import format_address

from blockchain.utils.kmsaws import AWSKMS
from blockchain.utils.lambaaws import LambdaSigner

def load_df(df_path):
    return pd.read_csv(df_path)

def add_row(df, tx_hash, from_, gmm_amount, busd_amount, exchange_rate_min):
    d = {}
    d['tx_hash'] = tx_hash
    d['from'] = from_
    d['gmm_amount'] = gmm_amount
    d['busd_amount'] = busd_amount
    d['exchange_rate_min'] = exchange_rate_min
    d['timestamp'] = str(datetime.now())[:10]
    return pd.concat([df, pd.DataFrame([d])])

def save_df(df, df_path):
    df.to_csv(df_path, index=False)

def get_unix_time_now():
    return int(datetime.timestamp(datetime.now()))

def get_last_block_number(chain):
    return chain.w3.eth.block_number

def get_connection():
    # connect to chain and set gwei
    max_gwei = 5
    fast_gwei = 1
    chain = BinanceSmartChain()
    chain.set_gwei_config(max_gwei, fast_gwei)
    return chain

def get_balances(chain, t_in, t_out, pk):
    print("Current balance: {}M GMM".format(t_in.get_balance(pk) / 1e18 / 1e6))
    print("Current balance: {} BUSD".format(t_out.get_balance(pk) / 1e18))
    print("BNB available : {}".format(chain.w3.eth.get_balance(pk) / 1e18))

def approve_token(chain, crypto_account):
    #approve token in
    approve_amount_in = 500000000
    address_pancake =  Web3.to_checksum_address('0x10ED43C718714eb63d5aA57B78B54704E256024E')#
    token_address_in = Web3.to_checksum_address('0x5B6bf0c7f989dE824677cFBD507D9635965e9cD3') #GMM
    t_in = ERC20Contract(chain, token_address_in)

    amount = int(approve_amount_in * 10**18)
    signed_tx = t_in.approve_if_not_approved(crypto_account, address_pancake, amount)
    if signed_tx is not None:
        tx_receipt = send_transaction(chain, signed_tx)
        print("Approve GMM: {}".format(tx_receipt))
        return

# get price impact on price
def get_price_impact(sb, amount_in_gmm):
    exc_now = sb.get_current_exchange_rate()
    exc_future = sb.get_affected_exchange_rate(amount_in=amount_in_gmm)
    price_impact = 1 - exc_future / exc_now
    return price_impact
    
class SnipeBotPancake:
    def __init__(self, pancake_contract, token_contract_in, token_contract_out, path):
                
        # get token contract
        self.token_contract_in = token_contract_in
        self.token_symbol_in = self.token_contract_in.contract.functions.symbol().call()
        self.decimals_in = 10**self.token_contract_in.contract.functions.decimals().call()
        
        # get token contract
        self.token_contract_out = token_contract_out
        self.token_symbol_out = self.token_contract_out.contract.functions.symbol().call()
        self.decimals_out = 10**self.token_contract_out.contract.functions.decimals().call()
        
        # token path
        self.path = path
        
        # get contract pancake
        self.smart_contract = pancake_contract
        
    def is_balance_greater_than_amount_in(self, crypto_account, amount_in):
        return self.token_contract_in.get_balance(crypto_account.address) >= amount_in
        
    def get_amounts_out(self, amount_in):
        return self.smart_contract.get_amounts_out(amount_in, self.path)
    
    def amount_out_min_is_greater_than_amounts_out(self, amount_out_min, amount_in):
        amounts = self.get_amounts_out(amount_in)
        current_exch_rate = amounts[1]/amount_in
        logger.info("Current exchange rate: {} {} per {}".format(current_exch_rate, self.token_symbol_out, self.token_symbol_in))
        return amounts[1] > amount_out_min

    def sign_buy(self, crypto_account, exchange_rate_min, amount_in, deadline, ether_in):
        wei_value = Web3.to_wei(Decimal(str(ether_in)), 'ether')
        amount_in_wei = int(self.decimals_in * amount_in)
        tokens_out =  exchange_rate_min * amount_in
        amount_out_min = int(tokens_out * self.decimals_out)

        signed_tx = self.smart_contract.swap_tokens_for_exact_tokens(crypto_account, amount_out_min, amount_in_wei, 
                                        self.path, crypto_account.address, deadline, wei_value)
        return signed_tx

    def buy(self, crypto_account, chain, exchange_rate_min, amount_in, deadline, ether_in):
        wei_value = Web3.to_wei(Decimal(str(ether_in)), 'ether')
        amount_in_wei = int(self.decimals_in * amount_in)
        tokens_out =  exchange_rate_min * amount_in
        amount_out_min = int(tokens_out * self.decimals_out)

        # check if I have balance to do the operation
        if not self.is_balance_greater_than_amount_in(crypto_account, amount_in_wei):
            logger.error("Not enough balance to do the transaction")
            raise Exception("Not enough balance to do the transaction")

        tx_receipt = None
        try:
            # check if amount_out is greater than we amount_out_min
            if self.amount_out_min_is_greater_than_amounts_out(amount_out_min, amount_in_wei):
                signed_tx = self.smart_contract.swap_tokens_for_exact_tokens(crypto_account, amount_out_min, amount_in_wei, 
                                    self.path, crypto_account.address, deadline, wei_value=0)
                tx_receipt = send_transaction(chain, signed_tx)
            else:
                logger.error("Exchange rate below minimum acceptable")
        except Exception as e:
            logger.error(f"ERROR: {e}")
        return tx_receipt

    def get_current_exchange_rate(self):
        amounts = self.get_amounts_out(int(1e18))
        current_exch_rate = amounts[1]/amounts[0]
        return current_exch_rate

    def get_affected_exchange_rate(self, amount_in):
        # amount_in not in gwei
        amounts = self.get_amounts_out(int(amount_in*1e18))
        current_exch_rate = amounts[1]/amounts[0]
        return current_exch_rate
    
def get_sniping():
    chain = get_chain('binance-smart-chain')
    print("NOPE")
    address_pancake = format_address('0x10ED43C718714eb63d5aA57B78B54704E256024E')
    pc = PancakeContract(chain, address_pancake)

    token_address_in = format_address('0x5B6bf0c7f989dE824677cFBD507D9635965e9cD3') #GMM
    t_in = ERC20Contract(chain, token_address_in)

    token_address_out = format_address('0xe9e7cea3dedca5984780bafc599bd69add087d56') #BUSD
    t_out = ERC20Contract(chain, token_address_out)
    print(f"Chain: {chain}, pc: {pc}")
    path = [token_address_in, token_address_out]
    sb = SnipeBotPancake(pc, token_contract_in=t_in, token_contract_out=t_out, path=path)
    return sb, chain

def get_surplus_gmm(start_block, end_block):
    pair_address = '0xedeec0ed10abee9b5616be220540cab40c9d991e'
    address_gmm_busd = format_address(pair_address) #GMM-BUSD pancake address

    scanner = Bscscan()
    txs = scanner.get_erc20_transactions(address_gmm_busd, start_block, end_block, page=1, offset=10000, sort='desc')
    # print(txs)

    df_transfers = pd.DataFrame(txs['result'])
    surplus_gmm = 0
    vol_gmm = 0

    if len(df_transfers) > 0:
        columns=['from','to','value','contractAddress','hash']
        df_transfers = df_transfers[columns]

        df_transfers = df_transfers[df_transfers['contractAddress'] == '0x5b6bf0c7f989de824677cfbd507d9635965e9cd3']
        df_transfers['value'] = df_transfers['value'].astype(float) / 1e18

        buy = df_transfers[(df_transfers['from'] == pair_address) & (df_transfers['to'] != pair_address)]
        sold = df_transfers[(df_transfers['from'] != pair_address) & (df_transfers['to'] == pair_address)]
    
        vol_gmm = buy['value'].sum() + sold['value'].sum()
        surplus_gmm = buy['value'].sum() - sold['value'].sum()
    return [surplus_gmm, vol_gmm]