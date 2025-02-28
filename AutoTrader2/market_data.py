import sqlite3
import ccxt
import logging
from datetime import datetime
from config import API_KEY, API_SECRET

class MarketData:
    """
    initializes binance exchange with ccxt
    """ 
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            },
        })
        self.exchange.set_sandbox_mode(True)
        logging.info("Initialized exchange in sandbox mode")

    def fetch_data(self, limit=1):
        """
        gets price data from binance
        """
        logging.info("Fetching price data")
        ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', limit=limit)
        return ohlcv

    def save_to_db(self, ohlcv):
        """
        saves the retrieved data to a database
        """
        logging.info("Saving price data to database")
        conn = sqlite3.connect('app.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS btc_usdt_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL
                )
            """)
        for ohlcv in ohlcv:
            cursor.execute("""
                INSERT INTO btc_usdt_prices (timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.fromtimestamp(ohlcv[0] / 1000).isoformat(),
                    ohlcv[1],
                    ohlcv[2],
                    ohlcv[3],
                    ohlcv[4],
                    ohlcv[5]
                ))
        conn.commit()
        conn.close()

    def read_from_db(self):
        """
        reads the saved data in the database
        """
        conn = sqlite3.connect('app.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM btc_usdt_prices")
        rows = cursor.fetchall()
        conn.close()
        print(rows)        
        return rows


#market_data = MarketData()
#ohlcv = market_data.fetch_data()
#market_data.save_to_db(ohlcv)
#market_data.read_from_db()
