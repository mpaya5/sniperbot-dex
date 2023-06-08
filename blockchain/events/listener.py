import asyncio

def handle_event(event):
    try:
        event_d = dict(event)
        print(event_d)
    except Exception as e: print(e)

async def log_loop(event_filter, poll_interval, handler_fn_call):
    while True:
        for event in event_filter.get_new_entries():
            handler_fn_call(event)
        await asyncio.sleep(poll_interval)

# event to listen via async, smart_contract has to be an instance of SmartContract class
def listen_events(smart_contract, event_name: str, interval_poll=0.2, handler_fn=None):
    handler_fn_call = handle_event if handler_fn is None else handler_fn

    event_filter = eval('smart_contract.contract.events.{}.createFilter(fromBlock="latest")'.format(event_name))
   
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(log_loop(event_filter, interval_poll, handler_fn_call)))
    finally:
        loop.close()
    return