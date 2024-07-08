import time
from market_data import MarketData
from strategy import Strategy
from engine import TradingEngine
from config import API_KEY, API_SECRET
from tt2 import TelegramBot

class TradingBot:
    def __init__(self):
        self.market_data = MarketData()
        self.strategy = Strategy()
        self.trading_engine = TradingEngine(API_KEY, API_SECRET)

    def run(self):
        while True:
            try:
                # Fetch and save the latest market data
                ohlcv = self.market_data.fetch_data()
                self.market_data.save_to_db(ohlcv)
                
                # Execute the trading strategy
                self.trading_engine.execute_order()

            except Exception as e:
                print(f"An error occurred: {e}")

            # Wait for a minute before the next iteration
            time.sleep(60)

if __name__ == '__main__':
    trading_engine = TradingEngine()
    bot = TelegramBot(trading_engine)
    bot.run()
