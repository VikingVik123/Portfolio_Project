import ccxt

exchange = ccxt.binance()
market = exchange.load_markets()

ticker = exchange.fetch_ticker('RUNEUSDT')

for ticker in ticker:
    print(ticker)
