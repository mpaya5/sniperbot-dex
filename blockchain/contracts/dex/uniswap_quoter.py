import json

from blockchain.contracts.smart_contract import SmartContract

"""
Check Uniswap Prices
"""
class UniswapQuoter(SmartContract):
    def __init__(self, chain, address):
        abi = json.loads('[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH9","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH9","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"path","type":"bytes"},{"internalType":"uint256","name":"amountIn","type":"uint256"}],"name":"quoteExactInput","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"name":"quoteExactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"path","type":"bytes"},{"internalType":"uint256","name":"amountOut","type":"uint256"}],"name":"quoteExactOutput","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"name":"quoteExactOutputSingle","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"path","type":"bytes"}],"name":"uniswapV3SwapCallback","outputs":[],"stateMutability":"view","type":"function"}]')
        super().__init__(chain, address, abi)

    """
    How many tokenIn do I need to buy tokenAmount of tokenOut
    """
    def quote_exact_output_single(self, tokenIn, tokenOut, fee, tokenAmount, sqrtPriceLimitX96):
        return self.contract.functions.quoteExactOutputSingle(tokenIn, tokenOut, fee, tokenAmount, sqrtPriceLimitX96).call()

    """
    How many tokenOut I can buy with tokenAmount of tokenIn
    """
    def quote_exact_input_single(self, tokenIn, tokenOut, fee, tokenAmount, sqrtPriceLimitX96):
        return self.contract.functions.quoteExactInputSingle(tokenIn, tokenOut, fee, tokenAmount, sqrtPriceLimitX96).call()

    def get_exact_input_single_params(self, tokenIn, tokenOut, amountIn, recipient, fee = 3000, slippage = 0.01, sqrtPriceLimitX96 = 0):
        exact_input_single = self.quote_exact_input_single(tokenIn, tokenOut, fee, amountIn, sqrtPriceLimitX96)
        amountOutMinimum = int((1 - slippage) * exact_input_single)
        return tokenIn, tokenOut, fee, recipient, amountIn, amountOutMinimum, sqrtPriceLimitX96