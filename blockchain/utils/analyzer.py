import ccxt
import pandas as pd
from .logger import AppLogger
logger = AppLogger('my_app')

class CryptoAnalyzer:
    def __init__(self):
        # Establecer conexiones a las plataformas
        self.binance = ccxt.binance()
        self.gateio = ccxt.gateio()
        self.close_prices = {}
        self.change_percentages = {}

    def get_previous_close(self, exchange, pair):
        """Función para obtener los precios de cierre del día anterior y el actual"""
        ohlcv = exchange.fetch_ohlcv(pair, '1d', limit=2)  # Obtiene las dos últimas velas de 1 día
        current_close = ohlcv[-1][4]
        previous_close = ohlcv[-2][4]
        return current_close, previous_close

    def collect_close_prices(self):
        # Definir los pares de criptomonedas
        pairs_binance = ['BAKE/USDT', 'XTZ/USDT', 'AXS/USDT', 'ENJ/USDT', 'ALICE/USDT', 'THETA/USDT', 
                         'CHZ/USDT', 'SAND/USDT', 'MANA/USDT', 'APE/USDT', 'BTC/USDT', 'ETH/USDT']
        pairs_gateio = ['GMM/USDT']

        # Recoger los precios de cierre
        for pair in pairs_binance:
            self.close_prices[pair], self.close_prices[pair + '_previous'] = self.get_previous_close(self.binance, pair)
        for pair in pairs_gateio:
            self.close_prices[pair], self.close_prices[pair + '_previous'] = self.get_previous_close(self.gateio, pair)

    def calculate_percentages(self):
        # Calcular los porcentajes de cambio
        self.change_percentages = {pair: (self.close_prices[pair]/self.close_prices[pair+'_previous'])*100 - 100 for pair in self.close_prices if not pair.endswith('_previous')}

    def analyze(self):
        # Calcular valores
        AA2_BB2_CC2_DD2_FF2_II2_JJ2_KK2_LL2_OO2 = sum(self.change_percentages[pair] for pair in ['BAKE/USDT', 'XTZ/USDT', 'AXS/USDT', 'ENJ/USDT', 'ALICE/USDT', 'THETA/USDT', 
                    'CHZ/USDT', 'SAND/USDT', 'MANA/USDT', 'APE/USDT']) / 10

        PP2 = self.change_percentages['BTC/USDT'] * 3
        QQ2 = self.change_percentages['ETH/USDT']
        RR2 = self.change_percentages['GMM/USDT']

        W2 = (AA2_BB2_CC2_DD2_FF2_II2_JJ2_KK2_LL2_OO2 + PP2 + QQ2) / 5

        x = 2.5
        SS = (W2 + x)
        SS2 = (W2 - x)

        PRECIOventa = ((self.close_prices['GMM/USDT']/100)* SS) + self.close_prices['GMM/USDT']
        PRECIOcompra = ((self.close_prices['GMM/USDT']/100)* SS2) + self.close_prices['GMM/USDT']

        priceordersell = (RR2 - SS)

        # Imprimir resultados
        logger.info(f"Price Order Sell: {priceordersell}, Precio Venta: {PRECIOventa}, Precio Compra: {PRECIOcompra}")

        # Comparar RR2 y SS
        if RR2 > SS:
            logger.info(f"RR2 es mayor que SS | RR2: {RR2}, SS: {SS}")
            return [True, priceordersell/100]
        else:
            logger.info(f"RR2 NO es mayor que SS | RR2: {RR2}, SS: {SS}")
            return [False, priceordersell/100]
        

if __name__ == "__main__":
    analyzer = CryptoAnalyzer()
    analyzer.collect_close_prices()
    analyzer.calculate_percentages()
    result = analyzer.analyze()
    print(result)