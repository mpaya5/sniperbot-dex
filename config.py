# parameters
min_amount_sell = 5 # in BUSD
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