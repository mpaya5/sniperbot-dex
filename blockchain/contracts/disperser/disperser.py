import json

from blockchain.contracts.smart_contract import SmartContract

class Disperser(SmartContract):
    def __init__(self, chain, address):
        abi = json.loads('[ {"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"recipients","type":"address[]"},{"name":"values","type":"uint256[]"}],"name":"disperseTokenSimple","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"recipients","type":"address[]"},{"name":"values","type":"uint256[]"}],"name":"disperseToken","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"recipients","type":"address[]"},{"name":"values","type":"uint256[]"}],"name":"disperseEther","outputs":[],"payable":true,"stateMutability":"payable","type":"function"}]')
        super().__init__(chain, address, abi)

    def disperse_token(self, token_address, crypto_account, recipients, values, **kwargs):
        function = self.contract.functions.disperseToken(token_address, recipients, values)
        return self.get_signed_function(crypto_account, function, **kwargs)

    def disperse_native(self, crypto_account, recipients, values, **kwargs):
        function = self.contract.functions.disperseEther(recipients, values)
        return self.get_signed_function(crypto_account, function, **kwargs) #wei_value=sum(values)

    ## dont forget to approve before the disperse, as well that balance is enough to do the dispersion