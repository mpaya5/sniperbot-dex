from blockchain.utils.web3_utils import format_address

def get_events_from_abi(abi):
    events = []
    formatted_events = []
    for abi_element in abi:
        if abi_element['type'] == "event": 
            events.append(abi_element)
            formatted_events.append(abi_element["name"])
    return events, formatted_events
    
def get_read_function_from_abi(abi):
    read_fns = []
    read_fns_formatted = []
    for abi_element in abi:
        if abi_element['type'] == "function" and abi_element['stateMutability'] == "view": 
            read_fns.append(abi_element)
            read_fns_formatted.append(get_function_info(abi_element))
    return read_fns, read_fns_formatted
    
def get_write_function_from_abi(abi):
    write_fns = []
    write_fns_formatted = []
    for abi_element in abi:
        if abi_element['type'] == "function" and abi_element['stateMutability'] != "view": 
            write_fns.append(abi_element)
            write_fns_formatted.append(get_function_info(abi_element))
    return write_fns, write_fns_formatted

def get_function_info(abi_element):
    name = abi_element["name"]
    input_type = [element["type"] for element in abi_element["inputs"]]
    input_name = [element["name"] for element in abi_element["inputs"]]
    
    args = ""
    for i in range(len(abi_element["inputs"])):
        args += input_type[i] + ': ' + input_name[i] + ', '
    args = args[:-2]
    fn_string = "{}({})".format(name, args)
    return fn_string
    
def get_functions_by_name(read_fns, fn_name):
    read_fns_name = []
    for function in read_fns:
        if function["name"] == fn_name:
            read_fns_name.append(function)
    return read_fns_name
    
def select_function(fns, index):
    selected_fn = fns[index]
    print(get_function_info(selected_fn))
    return selected_fn

def format_args_from_function(function, args):
    assert(len(function["inputs"]) == len(args)), 'Length mismatch between fn_args and args introduced'
    
    fn_args = "("
    for i in range(len(args)):
        if function["inputs"][i]["type"] == "address":
            fn_args += 'format_address("0x%0.40X" % {})'.format(args[i])
        elif function["inputs"][i]["type"] == "uint256":
            fn_args += 'int({})'.format(args[i])
        elif function["inputs"][i]["type"] == "bool":
            fn_args += '{}'.format(args[i])
        elif function["inputs"][i]["type"] == "address[]":
            fn_args += '[format_address("0x%0.40X" % eval(address)) for address in list({})]'.format(args[i])
        elif function["inputs"][i]["type"] == "uint256[]":
            fn_args += '[int(number) for number in list({})]'.format(args[i])
        fn_args += ', '
    fn_args = fn_args[:-2]
    fn_args += ")"
    return fn_args

def format_fn(function, args):
    return function["name"] + format_args_from_function(function, args)