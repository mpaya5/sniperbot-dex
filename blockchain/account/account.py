from eth_keys import keys
import codecs
from web3.auto import w3

from blockchain.utils.web3_utils import format_address

class Account:
    def sign_transaction(self, tx):
        raise NotImplementedError

class CryptoAccount(Account):
    def __init__(self, address, sk):        
        self.address = format_address(address)
        self.sk = sk
    
    def sign_transaction(self, tx):
        return w3.eth.account.sign_transaction(tx, self.sk)

class CryptoAccountSk(Account):
    def __init__(self, sk):        
        decoder = codecs.getdecoder("hex_codec")
        private_key_bytes = decoder(sk)

        self.sk = keys.PrivateKey(private_key_bytes[0])
        self.pk = self.sk.public_key

        self.address = format_address(self.pk.to_checksum_address())
    
    def sign_transaction(self, tx):
        return w3.eth.account.sign_transaction(tx, self.sk)