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
        self.trading_engine = TradingEngine()

    def run(self):
        while True:
            try:
                # Fetch and save the latest market data
                ohlcv = self.market_data.fetch_data()
                self.market_data.save_to_db(ohlcv)
                df = self.strategy.read_price()
                self.strategy.calc_indicators(df)
                self.strategy.entry_signals(df)
                self.strategy.exit_signals(df)
                # Execute the trading strategy
                self.trading_engine.execute_order()

            except Exception as e:
                print(f"An error occurred: {e}")

            # Wait for a minute before the next iteration
            time.sleep(60)

if __name__ == '__main__':
    trading_engine = TradingEngine()
    bot = TelegramBot(trading_engine)
    bot2 = TradingBot()
    bot2.run()