from config import API_KEY, API_SECRET
import ccxt
import pandas as pd
import csv
import time
from apscheduler.schedulers.background import BackgroundScheduler

class MarketData():
    """
    Deals with data fetching and parsing from exchange
    """
    def __init__(self):
        self.api=API_KEY
        self.apis=API_SECRET
        self.exchange = ccxt.binance({
            'apiKey': self.api,
            'secret': self.apis,
        })
        self.exchange.enableRateLimit = True
        self.exchange.set_sandbox_mode(True)
        self.scheduler = BackgroundScheduler()

    def hist_data(self):
        """
        Fetchs historical data according to specified parameters
        """
        candles = self.exchange.fetch_ohlcv('RUNE/USDT', timeframe='15m',limit=1000)
        
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Convert the timestamp to a datetime object
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def balance(self):
        """
        Fetches usdt balance
        """
        balance = self.exchange.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        print(f"USDT Balance: {usdt_balance}")

    def live_prices(self):
        """
        gets current price data in ohlcv & convert to dataframe
        """
        live_candles = self.exchange.fetch_ohlcv('RUNE/USDT', timeframe='15m', limit=1)
        df = pd.DataFrame(live_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Convert the timestamp to a datetime object
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        print(df)
        return df
    
    def regprice_update(self):
        """
        func to fetch price data at regular intervals
        """
        self.scheduler.start()
        self.scheduler.add_job(self.live_prices, 'interval', seconds=5)

        # Keep the script running to allow the scheduler to run
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()


# Create an instance of MarketData
#market_data = MarketData()
#market_data.regprice_update()
#market_data.hist_data()