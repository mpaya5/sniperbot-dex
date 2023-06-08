import json

from blockchain.utils.chain_utils import get_scan
from blockchain.utils.chain_utils import get_chain
from blockchain.contracts.smart_contract import SmartContract

# This class instantiate any smart contract with verified contract in scanners with just 2 parameters, chain and contract_address


class SmartContractAuto(SmartContract):
    def __init__(self, chain_str, contract_address):
        chain = get_chain(chain_str)
        scanner = get_scan(chain_str)

        # get abi from contract_address
        abi = json.loads(scanner.get_abi(contract_address)['result'])

        super().__init__(chain, contract_address, abi)
