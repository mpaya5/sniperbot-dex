import pandas as pd
import numpy as np
from web3 import Web3
import time

from blockchain.account.account import CryptoAccount
from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

from config import addresses, skeys, support, min_amount_sell, max_price_impact, volumen_percentage, times_current_exc, offset_blocks, query_time_seconds,deadline_sum 

from utils import get_unix_time_now, get_surplus_gmm, get_price_impact, get_sniping, approve_token

# accounts = []

# Crear objetos de cuentas criptográficas usando direcciones y claves privadas

# for i in range(len(addresses)):
#     pk = Web3.to_checksum_address(addresses[i])
#     sk = skeys[i] + support[i]
#     crypto_account = CryptoAccount(pk, sk)
#     accounts.append(crypto_account)

## approve token first to be able to sell GMM
# Aprobar el token para cada cuenta
""" for i in range(len(accounts)):
     sb, chain = get_sniping()
     approve_token(chain, accounts[i])
     time.sleep(5) """

def sell(sb, chain, accounts):
    """
    Dentro de la función sell(sb, chain), se llevan a cabo una serie de operaciones para realizar la venta de criptomonedas. A continuación, se detalla el flujo del código:

    - Se obtiene el número de bloque actual y se calcula un rango de bloques para realizar cálculos relacionados con el exceso de GMM.
    - Se llama a la función get_surplus_gmm para calcular el exceso de GMM entre los bloques especificados.
    - Se utiliza sb.get_current_exchange_rate() para obtener la tasa de cambio actual.
    - Se calcula la cantidad de GMM y BUSD a vender basándose en el exceso de GMM y la tasa de cambio.
    - Si la cantidad de BUSD a vender supera el umbral mínimo (min_amount_sell), se calcula el impacto de precio utilizando la función get_price_impact.
    - Si el impacto de precio está por debajo del umbral máximo (max_price_impact), se calcula una tasa de cambio mínima y se selecciona una cuenta criptográfica al azar.
    - Se configuran los parámetros de la transacción y se realiza la venta utilizando la función sb.buy.
    - El programa se ejecuta en un bucle infinito (while True) para realizar operaciones de venta de forma continua. En caso de que se produzca una excepción durante la ejecución, se captura el error, se muestra en la salida y se espera un tiempo antes de continuar con el ciclo.
    """
    # Obtener el número de bloque actual
    current_block = chain.w3.eth.block_number
    start_block = current_block - offset_blocks
    end_block = current_block

    # Calcular el exceso de GMM en un rango de bloques
    gmm_surplus, gmm_vol = get_surplus_gmm(start_block, end_block)

    exc_rate_now = sb.get_current_exchange_rate()

    vol_in_percentage = gmm_vol*volumen_percentage
    logger.info(f"GMM SURPLUS: {gmm_surplus}, GMM VOL: {gmm_vol}, VOL_IN_PERCENTAGE: {vol_in_percentage}")
    # Si la presión alcista  es mayor o igual a vol_in_percentage
    if gmm_surplus >= vol_in_percentage:
        # Calcular la cantidad de GMM y BUSD a vender
        # Crear random para buy_pressure_sell
        bps_csv = pd.read_csv('data/buy_pressure_sell.csv')
        buy_pressure_sell = bps_csv['pressure'].values[0]
        gmm_sell = int(buy_pressure_sell * gmm_surplus)
        busd_sell = exc_rate_now * gmm_sell
        
        logger.info("Current surplus: {}, Current exchange rate: {}, BUSD sell:{}, Buy pressure sell:{}".format(gmm_surplus, exc_rate_now, round(busd_sell,3)), buy_pressure_sell)
        
        if busd_sell > min_amount_sell:
            # Calcular el impacto de precio
            # price impact
            price_impact = get_price_impact(sb, gmm_sell)
            if price_impact < max_price_impact:
                # Calcular la tasa de cambio mínima
                exchange_rate_min = exc_rate_now * (1 - min(times_current_exc * price_impact, max_price_impact)) # Calculo para conocer cómo vamos a dejar el precio
                exchange_rate_min = round(exchange_rate_min, 7)
                logger.info("Quantity {}, Exec price {}, Expected BUSD: {}".format(gmm_sell, exchange_rate_min, busd_sell))

                # Seleccionar una cuenta criptográfica al azar
                index = np.random.choice(len(accounts))

                # Seleccionar una cuenta criptográfica al azar
                deadline = get_unix_time_now() + deadline_sum # 20 min from order creation
                ether_in = 0 # in ETH, not wei
                # Realizar la transacción de venta
                tx_receipt = sb.buy(accounts[index], chain, exchange_rate_min, gmm_sell, deadline, ether_in)

    else:
        logger.info(f"La presión alcista es menor que el vol_percentage")


def run_loop():
    logger.info('Iniciamos el servicio de marketmaking en DEX')
    accounts = []
    for i in range(len(addresses)):
        pk = Web3.to_checksum_address(addresses[i])
        sk = skeys[i] + support[i]
        crypto_account = CryptoAccount(pk, sk)
        accounts.append(crypto_account)

    try:
        sb, chain = get_sniping()
        sell(sb, chain, accounts)
    except Exception as e:
        logger.error(f"ERROR: {e}")