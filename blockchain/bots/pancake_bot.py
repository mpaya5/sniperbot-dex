from web3 import Web3

from blockchain.utils.utils import send_transaction
from utils.web3_utils import to_decimal, to_wei

from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

class SnipeBotPancake:
    def __init__(self, pancake_contract, token_contract_in, token_contract_out, path):
                
        # get token contract
        self.token_contract_in = token_contract_in
        self.token_symbol_in = self.token_contract_in.symbol
        self.decimals_in = 10**self.token_contract_in.decimals
        
        # get token contract
        self.token_contract_out = token_contract_out
        self.token_symbol_out = self.token_contract_out.symbol
        self.decimals_out = 10**self.token_contract_out.decimals
        
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
        print("Current exchange rate: {} {} per {}".format(current_exch_rate, self.token_symbol_out, self.token_symbol_in))
        return amounts[1] > amount_out_min

    def sign_buy(self, crypto_account, exchange_rate_min, amount_in, deadline, ether_in):
        wei_value = to_wei(to_decimal(str(ether_in)), magnitude='ether')
        amount_in_wei = int(self.decimals_in * amount_in)
        tokens_out =  exchange_rate_min * amount_in
        amount_out_min = int(tokens_out * self.decimals_out)

        signed_tx = self.smart_contract.swap_tokens_for_exact_tokens(crypto_account, amount_out_min, amount_in_wei, self.path, crypto_account.address, deadline, wei_value)
        return signed_tx

    def buy(self, crypto_account, chain, exchange_rate_min, amount_in, deadline, ether_in):
        wei_value = to_wei(to_decimal(str(ether_in)), magnitude='ether')
        amount_in_wei = int(self.decimals_in * amount_in)
        tokens_out =  exchange_rate_min * amount_in
        amount_out_min = int(tokens_out * self.decimals_out)

        # check if I have balance to do the operation
        if not self.is_balance_greater_than_amount_in(crypto_account, amount_in_wei):
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