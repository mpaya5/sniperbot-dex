OPENSEA_API_KEY = 'YOUR_API_KEY'
ETHERSCAN_API_KEY = 'YOUR_API_KEY'
BSCSCAN_API_KEY = '9K484KMM7B9ZY6I9HJKHU51X7QTWGAQFAM'
ARBISCAN_API_KEY = 'YOUR_API_KEY'

addresses = ['0xe0E15b263Ed1826D7AdC79A85C572274092AC996']
skeys = ['922c0a2a5668b758612fd5b3a885f171b03a93576963933d700680013a173f9c']
support = ['']

# token Bot
token_telegram_bot = '6037793943:AAHTTYIeUkOfRb6_SUpqtN2GdfTdbSbuz50'

# parameters
min_amount_sell = 20 # in BUSD
max_price_impact = 0.002 # 0.2% max of price impact
volumen_percentage = 0.003
times_current_exc = 8
buy_pressure_sell = 0.1 #RECOGIDO POR CSV# sell 10% of buy pressure, (better random normal)
offset_blocks = 500 # 150 minutes, normalmente poner 100
query_time_seconds = 60 # each 60 minutes execute, better random normal

deadline_sum = 120 # 2 min in seconds

# threshold sell script
addresses_thres = []
skeys_thres = []
support_thres = []

min_price_admissible_sell = 0.002
mean_sell_gmm = 210000
std_sell_gmm = 21443
query_time_seconds_threshold = 600 # each 10 minutes execute aprox