import json

from blockchain.contracts.smart_contract import SmartContract


class ERC20Contract(SmartContract):
    def __init__(self, chain, address, abi=None):
        if abi is None:
            abi = json.loads('[ { "constant": true, "inputs": [], "name": "name", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "approve", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_from", "type": "address" }, { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "name": "", "type": "uint8" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transfer", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" }, { "name": "_spender", "type": "address" } ], "name": "allowance", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "payable": true, "stateMutability": "payable", "type": "fallback" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "owner", "type": "address" }, { "indexed": true, "name": "spender", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "from", "type": "address" }, { "indexed": true, "name": "to", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event" } ]')
        super().__init__(chain, address, abi)
        #self.get_properties()

    ### READ FUNCTIONS ###

    def get_properties(self):
        self.decimals = self.contract.functions.decimals().call()  # decimals
        self.name = self.contract.functions.name().call()  # name
        self.symbol = self.contract.functions.symbol().call()  # symbol
        return self.name, self.symbol, self.decimals

    def get_balance(self, address_sender):
        return self.contract.functions.balanceOf(address_sender).call()

    # returns balance in tokens (not in wei)
    def get_balance_tokens(self, address_sender):
        return self.get_balance(address_sender) / 10**self.decimals

    def get_total_supply(self):
        return self.contract.functions.totalSupply().call()

    # returns total supply in tokens
    def get_total_supply_tokens(self):
        return self.contract.functions.totalSupply().call() / 10**self.decimals

    def get_approved_amount(self, address_sender, spender):
        return self.contract.functions.allowance(address_sender, spender).call()

    ### WRITE FUNCTIONS ###

    # put kwargs instead
    def approve(self, from_address, spender, amount, **kwargs):
        function = self.contract.functions.approve(spender, amount)
        print("Addresssssssssssssss: ",from_address.address)
        return self.get_signed_function(from_address, function, **kwargs)
        ##self.get_raw_transaction(from_address, function, **kwargs)

    def approve_if_not_approved(self, from_address, spender, amount):
        if self.get_approved_amount(from_address.address, spender) < amount:
            return self.approve(from_address, spender, amount)
        return None

    def transfer(self, from_address, to, amount, **kwargs):
        function = self.contract.functions.transfer(to, amount)
        return self.get_raw_transaction(from_address, function, **kwargs)

    def transfer_from(self, from_address, to, amount, **kwargs):
        function = self.contract.functions.transferFrom(from_address, to, amount)
        return self.get_raw_transaction(from_address, function, **kwargs)
