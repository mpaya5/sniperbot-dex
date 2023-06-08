from blockchain.utils.chain_utils import get_chain, get_all_chain_names
from blockchain.contracts.smart_contract_auto import SmartContractAuto
from blockchain.accounting.transactions import get_addresses_txs_from_DDBB, get_monetary_txs
import pandas as pd
from web3 import Web3

from blockchain.contracts.interfaces.erc20 import ERC20Contract
from blockchain.api.coingecko import Coingecko

# price for considering trash tokens, if its below threshold_price then don't consider
# from config import threshold_price
threshold_price = 1  # 1 USD


def get_unique_token_addresses(txs):
    token_addresses = pd.DataFrame(txs)['contractAddress'].apply(lambda x: Web3.to_checksum_address(x)).unique()
    return token_addresses


def get_price(prices, x):
    price_token = 0
    if x in prices.keys():
        if 'usd' in prices[x].keys():
            price_token = prices[x]['usd']
    return price_token


def get_balance_summary(balance_obj, chain, address, txs):
    df_native_balance = pd.DataFrame([get_native_balance_summary(balance_obj, chain, address)])
    df_balances = pd.DataFrame(columns=df_native_balance.columns.values)

    if txs != []:

        token_addresses = get_unique_token_addresses(txs)
        prices = balance_obj.get_token_prices(chain, token_addresses)
        balances = balance_obj.get_balances(chain, address, token_addresses)

        df_balances = pd.DataFrame(balances['result'])
        #df_balances['price'] = df_balances['token_address'].apply(lambda x: x.lower()).apply(lambda x: prices[x]['usd'] if x in prices.keys() else 0)
        df_balances['price'] = df_balances['token_address'].apply(
            lambda x: x.lower()).apply(lambda x: get_price(prices, x))
        df_balances['value_usd'] = df_balances['value'] * df_balances['price']

    df_balances = pd.concat([df_native_balance, df_balances])

    df_balances = filter_balances(df_balances)
    d = {"address": address, "result": df_balances.to_dict('records')}
    return d


def filter_balances(df_balances):
    return df_balances[(df_balances['value'] > 0) & (df_balances['value_usd'] > threshold_price)]


def get_native_balance_summary(balance_obj, chain, address):
    balance_d = balance_obj.get_native_balance(chain, address)
    prices = balance_obj.cg.get_price_by_id(chain.cg_ticker)

    try:
        balance_d["price"] = prices[chain.cg_ticker]['usd']
    except:
        balance_d["price"] = 0
    balance_d["value_usd"] = balance_d["value"] * balance_d["price"]
    return balance_d


class Balance:
    def get_native_balance(self, chain, address):
        amount = chain.get_native_balance(address)
        d = {"chain": chain.name, "token_address": '0x0000000000000000000000000000000000000000',
             "type": 'native', "value": amount, "symbol": chain.coin}
        return d

    # balance in tokens, not in wei
    def get_balances(self, chain, address, token_addresses):
        balances = {"address": address, "result": []}
        for token_address in token_addresses:
            try:
                token = self.interface(chain, token_address)
                amount = token.get_balance_tokens(address)
                balances["result"].append({"chain": chain.name, "token_address": token_address,
                                          "type": self.type, "value": amount, "symbol": token.symbol})
            except Exception as e:
                print(e)
                pass
        return balances


class BalanceERC20(Balance):
    def __init__(self):
        self.interface = ERC20Contract
        self.type = 'ERC20'
        self.cg = Coingecko()

    def get_token_prices(self, chain, token_addresses):
        d = self.cg.get_price_by_contract_addresses(platform=chain.name, contract_addresses=token_addresses)
        return d


def get_unique_tokens(addresses, df_raw_transactions, df_formatted_txs):
    df_users = get_addresses_txs_from_DDBB(addresses, df_formatted_txs)
    df_users_money = get_monetary_txs(df_users).drop_duplicates().reset_index(drop=True)
    df_users_money.loc[df_users_money.index.values,
                       'hash'] = df_users_money['tx_hash_link'].apply(lambda x: x.split('/')[-1])

    df_users_raw = get_addresses_txs_from_DDBB(addresses, df_raw_transactions)

    df_users_tokens = df_users_raw[df_users_raw['hash'].isin(
        df_users_money['hash'])][['from', 'to', 'chain', 'contractAddress', 'tokenSymbol', 'tokenDecimal']]
    unique_tokens = df_users_tokens[~df_users_tokens.isna().any(axis=1)].drop_duplicates(
    )[['from', 'to', 'chain', 'contractAddress', 'tokenSymbol', 'tokenDecimal']].reset_index(drop=True)
    return unique_tokens


def get_balances_from_addresses(addresses, df_raw_transactions, df_formatted_txs):
    unique_tokens = get_unique_tokens(addresses, df_raw_transactions, df_formatted_txs)

    chains = {}
    for ch in get_all_chain_names():
        chains[ch] = get_chain(ch)

    balances = {}
    for address in addresses:
        print("\n\nGetting balance from: {}".format(address))
        balances[address] = {}
        for chain_key in chains.keys():
            balances[address][chain_key] = []

            try:
                # get native balance
                balance_token = chains[chain_key].get_native_balance(address)
                d = {'smart_contract_address': 'native',
                     'token_value': balance_token, 'symbol': chains[chain_key].coin}
                balances[address][chain_key].append(d)

            except Exception as e:
                print(e)

        # get token balances
        unique_tokens_red = unique_tokens[(unique_tokens['from'] == address) | (unique_tokens['to'] == address)]
        unique_tokens_red = unique_tokens_red[['chain', 'contractAddress',
                                               'tokenSymbol', 'tokenDecimal']].drop_duplicates()

        print("Tokens to inspect: {}".format(unique_tokens_red['tokenSymbol'].unique()))

        for index in unique_tokens_red.index.values:
            try:
                row = unique_tokens_red.loc[index]

                chain_key = row['chain']

                # smart contract has to be verified
                smart_contract = SmartContractAuto(chain_key, row['contractAddress'])

                # balance
                balance = smart_contract.read_function_from_name(fn_name="balanceOf", args=[address])
                balance_token = balance / (10**(int(row['tokenDecimal'])))

                d = {'smart_contract_address': row['contractAddress'],
                     'token_value': balance_token, 'symbol': row['tokenSymbol']}
                balances[address][chain_key].append(d)

            except Exception as e:
                print(e)
    return balances
