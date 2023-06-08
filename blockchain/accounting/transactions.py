import pandas as pd
import numpy as np

from web3 import Web3
from blockchain.api.coingecko import Coingecko
from blockchain.utils.web3_utils import format_address, is_valid_address


def check_for_exceptions(d):
    if len(d['result']) == 0:
        raise Exception('No transactions found')


def get_txs_filtered(d, address, value):
    check_for_exceptions(d)

    df_txs = pd.DataFrame(d['result'])

    df_txs['value'] = df_txs['value'].astype(float)
    df_txs['from'] = df_txs['from'].apply(lambda x: Web3.to_checksum_address(x))
    df_txs['to'] = df_txs['to'].apply(lambda x: Web3.to_checksum_address(x))
    df_txs['contractAddress'] = df_txs['contractAddress'].apply(
        lambda x: Web3.to_checksum_address(x) if x != '' or x is None else x)

    df_txs = df_txs[df_txs[value] == address]

    result = {'status': d['status'], 'message': d['message'], 'result': df_txs.to_dict('records')}
    return result


def get_transactions_in_df(txs_dict):
    txs = []
    for address in txs_dict.keys():
        for tx_type in txs_dict[address]['transactions'].keys():
            for chain in txs_dict[address]['transactions'][tx_type].keys():
                for tx in txs_dict[address]['transactions'][tx_type][chain]['result']:
                    d = tx
                    d['address'] = address
                    d['chain'] = chain
                    d['tx_type'] = tx_type
                    txs.append(d)
    return pd.DataFrame(txs)


def filter_normal_tx(txs_df):
    txs_df = filter_txs(txs_df)
    filtered = txs_df[txs_df['value'].astype(float) > 0].copy()
    filtered.loc[filtered.index.values, 'value'] = filtered['value'].astype(float).copy() / 1e18
    return filtered


def filter_txs(txs_df):
    filtered = txs_df[txs_df['isError'] == '0']
    return filtered


def get_withdraws(txs_df):
    return txs_df[txs_df['address'].apply(lambda x: x.lower()) == txs_df['from'].apply(lambda x: x.lower())]


def get_deposits(txs_df):
    return txs_df[txs_df['address'].apply(lambda x: x.lower()) == txs_df['to'].apply(lambda x: x.lower())]


def get_historical_prices_erc20(df_erc20, time_between_requests=2):
    cg = Coingecko(time_between_requests)

    historical_prices = {}
    unique_addresses = df_erc20['contractAddress'].unique()
    unique_addresses
    for address in unique_addresses:
        rows = df_erc20[df_erc20['contractAddress'] == address]['timeStamp']

        from_timestamp = int(rows.min() - 3600)
        to_timestamp = int(rows.max())
        platform = df_erc20[df_erc20['contractAddress'] == address]['chain'].values[0]

        prices = cg.get_price_by_contract_address_timestamp(platform, address, from_timestamp, to_timestamp)
        historical_prices[address] = prices
    return historical_prices


def get_token_price_tx_value(df_erc20, time_between_requests=2):
    historical_prices = get_historical_prices_erc20(df_erc20, time_between_requests)

    prices_tokens = {}
    for key in historical_prices:
        if 'prices' in list(historical_prices[key].keys()):
            prices_token = historical_prices[key]['prices']

            times = np.array([p[0] for p in prices_token]) // 1000
            pric = np.array([p[1] for p in prices_token])

            prices_tokens[key] = {'times': times, 'prices': pric}

    prices_df_erc20 = []
    for index in df_erc20.index.values:
        row = df_erc20.loc[index]

        if row.contractAddress in list(prices_tokens.keys()):
            timestamp = row['timeStamp']
            times = prices_tokens[row.contractAddress]['times']
            prices = prices_tokens[row.contractAddress]['prices']

            index = np.argmin(np.abs(timestamp - times))

            prices_df_erc20.append(prices[index])
        else:
            prices_df_erc20.append(0)

    df_erc20['price_token'] = prices_df_erc20
    df_erc20['tx_value_usd'] = df_erc20['price_token'] * df_erc20['value']
    return df_erc20


def get_historical_prices_normal(df_normal, time_between_requests=2):
    id_coingecko = {'binance-smart-chain': 'binancecoin',
                    'ethereum': 'ethereum'}

    cg = Coingecko(time_between_requests)

    historical_prices = {}
    unique_chains = df_normal['chain'].unique()

    for chain in unique_chains:
        rows = df_normal[df_normal['chain'] == chain]['timeStamp']

        from_timestamp = int(rows.min() - 3600)
        to_timestamp = int(rows.max())
        id_coin = id_coingecko[chain]

        prices = cg.get_price_by_id_timestamp(id_coin, from_timestamp, to_timestamp)
        historical_prices[chain] = prices
    return historical_prices


def get_token_price_tx_value_normal(df_normal, time_between_requests=2):
    historical_prices = get_historical_prices_normal(df_normal, time_between_requests)

    prices_tokens = {}
    for key in historical_prices:
        if 'prices' in list(historical_prices[key].keys()):
            prices_token = historical_prices[key]['prices']

            times = np.array([p[0] for p in prices_token]) // 1000
            pric = np.array([p[1] for p in prices_token])

            prices_tokens[key] = {'times': times, 'prices': pric}

    prices_df_erc20 = []
    for index_ in df_normal.index.values:
        row = df_normal.loc[index_]

        if row.chain in list(prices_tokens.keys()):
            timestamp = row['timeStamp']
            times = prices_tokens[row.chain]['times']
            prices = prices_tokens[row.chain]['prices']

            index = np.argmin(np.abs(timestamp - times))
            prices_df_erc20.append(prices[index])
        else:
            prices_df_erc20.append(0)

    df_normal['price_token'] = prices_df_erc20
    df_normal['tx_value_usd'] = df_normal['price_token'] * df_normal['value']
    return df_normal


def get_addresses_txs_from_DDBB(addresses, df_transactions):
    addresses = [format_address(address) for address in addresses]

    df_transactions['from'] = df_transactions['from'].apply(
        lambda address: format_address(address) if is_valid_address(address) else address)
    df_transactions['to'] = df_transactions['to'].apply(
        lambda address: format_address(address) if is_valid_address(address) else address)

    return df_transactions[(df_transactions['from'].isin(addresses)) |
                           (df_transactions['to'].isin(addresses))]


def get_monetary_txs(df_users):
    return df_users[(df_users['value_in_USD'].astype(str) != 'nan') & (df_users['value_in_USD'] > 0)]
