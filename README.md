#   AUTOTRADER
Your gateway to stressfree trading(At least how i envision it)

The Data directory contains everything i've achieved so far. For now AutoTrader can fetch historical data in ohlcv format, stream live market data in ohlcv format and generate trading signals and run backtests, the backtest results are stored in the Performance_metrics file. The trading engine, telegram interface and SQlite storage are works in progress. 

#   OPERATION
Place your Binance API token and secret key in the config.py file

FETCHING CRYPTO PRICES: Uncomment the class functions at the bottom of the MarketData class and run, 