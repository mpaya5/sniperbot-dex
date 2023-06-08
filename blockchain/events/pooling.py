import time

from tqdm import tqdm
from web3._utils.events import get_event_data

def handle_event(event, event_template):
    try:
        result = get_event_data(event_template.web3.codec, event_template._get_event_abi(), event)
        return True, result
    except:
        return False, None

# event to listen via pooling, smart_contract has to be an instance of SmartContract class
def get_events(smart_contract, event_name: str, start_block: int, end_block:int=None, steps:int=49999):
    event_template = eval('smart_contract.contract.events.{}'.format(event_name))

    start_listen_block = start_block
    end_listen_block = smart_contract.chain.w3.eth.block_number if end_block is None else end_block
    block_diff = (end_listen_block - start_listen_block)
    iterations = int(block_diff / steps) + (block_diff % steps > 0) # higher int

    print("Start Block: {}, End Block: {}".format(start_listen_block, end_listen_block))
    print("Block Difference: {}".format(block_diff))
    print("Block Step: {}".format(steps))

    events_catched = []
    for i in tqdm(range(iterations)):
        start_block = start_listen_block + (i * steps)
        end_block = end_listen_block if start_block + steps > end_listen_block else start_block + steps

        if start_block >= end_listen_block:
            break

        events = smart_contract.chain.w3.eth.get_logs({'fromBlock':start_block, 'toBlock': end_block, 'address': smart_contract.address})

        for event in events: 
            suc, res = handle_event(event=event, event_template=event_template)   
            if suc:
                events_catched.append(dict(res))

        # sleeping for avoiding nodes blocking our requests. If using private nodes, then delete it.
        if (iterations % 30 == 0):
            print("Sleeping 5s to avoid node blocking requests")
            time.sleep(5)

    print("Total events catched: {}" .format(len(events_catched)))
    return events_catched