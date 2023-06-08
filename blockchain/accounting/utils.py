import pandas as pd
from web3 import Web3
from config import threshold_price

def get_unique_token_addresses(txs):
    token_addresses = pd.DataFrame(txs)['contractAddress'].apply(lambda x: Web3.to_checksum_address(x)).unique()
    return token_addresses

def get_balance_summary(balance_obj, chain, address, txs):
    token_addresses = get_unique_token_addresses(txs)
    prices = balance_obj.get_token_prices(chain, token_addresses)
    balances = balance_obj.get_balances(chain, address, token_addresses)
    
    df_balances = pd.DataFrame(balances['result'])
    df_balances['price'] = df_balances['token_address'].apply(lambda x: x.lower()).apply(lambda x: prices[x]['usd'] if x in prices.keys() else 0)
    df_balances['value_usd'] = df_balances['value'] * df_balances['price']
    
    df_balances = filter_balances(df_balances)
    
    d = {"address":address, "result":df_balances.to_dict('records')}
    return d

def filter_balances(df_balances):
    return df_balances[(df_balances['value'] > 0) & (df_balances['value_usd'] > threshold_price)]