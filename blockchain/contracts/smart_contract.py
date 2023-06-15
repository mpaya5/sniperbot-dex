from blockchain.utils.web3_utils import format_address
from blockchain.utils.abi import get_events_from_abi, get_read_function_from_abi, get_write_function_from_abi, select_function, get_functions_by_name, format_fn
from blockchain.events.listener import listen_events
from blockchain.events.pooling import get_events

from blockchain.utils.lambaaws import LambdaSigner
from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')
class SmartContract:
    def __init__(self, chain, address, abi):
        self.chain = chain
        self.address = format_address(address)
        self.abi = abi
        self.contract = chain.w3.eth.contract(address=format_address(address), abi=abi)
        self.get_functions_and_events()
        # Creamos instancia de lambda para las firmas
        self.lambda_signer = LambdaSigner()

    def build_tx(self, function, _from,  **kwargs):
        base_tx = self.chain.build_transaction(_from, **kwargs)
        tx = function.build_transaction(base_tx)
        return tx

    def get_functions_and_events(self):
        self.events, self.formated_events = get_events_from_abi(self.abi)
        self.read_functions, self.formated_read_functions = get_read_function_from_abi(self.abi)
        self.write_functions, self.formated_write_functions = get_write_function_from_abi(self.abi)

    # {'code': -32000, 'message': 'gas required exceeds allowance (0)'} happens when _from does not have native token, hardcode gas there
    # args we can set on kwargs are (to, wei_value, gas, gwei, nonce)
    def get_signed_function(self, from_address, function, **kwargs):
        tx = self.get_raw_transaction(from_address.address, function, **kwargs)
        print(tx)
        # Utilizamos la función Lambda para firmar la transacción
        signed_tx = self.lambda_signer.sign_transaction(tx)
        #Vamos a comprobar diferencias
        return signed_tx

    def get_raw_transaction(self, from_address, function, **kwargs):
        return self.build_tx(function, _from=from_address, **kwargs)
        ############ READ FUNCTIONS ################

        # Passing string to eval as a func_call for instance 'balanceOf(format_address(hex(0xEB9...)))'

    def read_function(self, func_call_str):
        return eval('self.contract.functions.{}.call()'.format(func_call_str))

    def get_read_function_from_index(self, index):
        return select_function(self.read_functions, index)

    def get_read_function_from_name(self, fn_name):
        return get_functions_by_name(self.read_functions, fn_name)[0]  # return the first match

    def read_function_from_index(self, index, args):
        selected_fn = self.get_read_function_from_index(index)
        fn_string_formatted = format_fn(selected_fn, args)
        return self.read_function(fn_string_formatted)

    def read_function_from_name(self, fn_name, args):
        selected_fn = self.get_read_function_from_name(fn_name)
        fn_string_formatted = format_fn(selected_fn, args)
        return self.read_function(fn_string_formatted)

    ############ WRITE FUNCTIONS ################

    def write_function(self, from_address, func_call_str, **kwargs):
        function = eval('self.contract.functions.{}'.format(func_call_str))
        return self.get_raw_transaction(from_address, function, **kwargs)

    def get_write_function_from_index(self, index):
        return select_function(self.write_functions, index)

    def get_write_function_from_name(self, fn_name):
        return get_functions_by_name(self.write_functions, fn_name)[0]  # return the first match

    def write_function_from_index(self, from_address, index, args, **kwargs):
        selected_fn = self.get_write_function_from_index(index)
        fn_string_formatted = format_fn(selected_fn, args)
        return self.write_function(from_address, fn_string_formatted, **kwargs)

    def write_function_from_name(self, from_address, fn_name, args, **kwargs):
        selected_fn = self.get_write_function_from_name(fn_name)
        fn_string_formatted = format_fn(selected_fn, args)
        return self.write_function(from_address, fn_string_formatted, **kwargs)

    ############ EVENTS ################

    # event to listen via async
    def listen_event(self, event_name: str, interval_poll=0.2, handler_fn=None):
        return listen_events(self, event_name, interval_poll, handler_fn)

    def get_event(self, event_name: str, start_block: int, end_block: int = None, steps: int = 49999):
        return get_events(self, event_name, start_block, end_block, steps)
