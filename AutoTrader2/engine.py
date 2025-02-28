import logging
import sqlite3
from market_data import MarketData
from strategy import Strategy
from config import API_KEY, API_SECRET
from datetime import datetime
import time

class TradingEngine(MarketData):
    def __init__(self):
        super().__init__()
        self.symbol = 'BTC/USDT'
        self.strategy = Strategy()

    def log_closed_trade(self, order, current_price):
        order_price = float(order['price'])
        amount = float(order['amount'])
        profit = (current_price - order_price) * amount if order['side'] == 'buy' else (order_price - current_price) * amount
        
        try:
            conn = sqlite3.connect('app.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO closed_trades (timestamp, symbol, side, amount, price, profit) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                datetime.fromtimestamp(order['timestamp'] / 1000).isoformat(),
                self.symbol,
                order['side'],
                amount,
                order_price,
                profit
            ))
            conn.commit()
        except Exception as e:
            logging.error(f"Error logging closed trade: {e}")
        finally:
            conn.close()

    def show_trade_stats(self):
        try:
            conn = sqlite3.connect('app.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM closed_trades")
            trades = cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching trade stats: {e}")
            return "Error fetching trade stats"
        finally:
            conn.close()

        total_profit = sum(trade[6] for trade in trades)
        total_trades = len(trades)
        wins = [trade for trade in trades if trade[6] > 0]
        losses = [trade for trade in trades if trade[6] <= 0]
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        average_win = sum(trade[6] for trade in wins) / len(wins) if wins else 0
        average_loss = sum(trade[6] for trade in losses) / len(losses) if losses else 0
        profit_factor = sum(trade[6] for trade in wins) / abs(sum(trade[6] for trade in losses)) if losses else float('inf')
        stats = f"""
        Total Trades: {total_trades}
        Total Profit: {total_profit}
        Win Rate: {win_rate * 100:.2f}%
        Average Win: {average_win}
        Average Loss: {average_loss}
        Profit Factor: {profit_factor}
        """
        return stats

    def get_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total']['USDT']
            logging.info(f"Fetched balance: {usdt_balance}")
            return usdt_balance
        except Exception as e:
            logging.error(f"An error occurred while fetching balance: {e}")
            return None
    
    def calc_order(self, usdt_balance, current_price, risk_percentage=100):
        risk_amount = usdt_balance * (risk_percentage / 100)
        order_size = risk_amount / current_price
        logging.info(f"Calculated order size: {order_size}")
        return order_size

    def place_order(self, side, amount):
        try:
            order = self.exchange.create_market_order(self.symbol, side, amount)
            logging.info(f"Placed {side} order for {amount} {self.symbol}. Order ID: {order['id']}")
        except Exception as e:
            logging.error(f"An error occurred while placing order: {e}")

    def close_orders(self, side):
        try:
            open_orders = self.exchange.fetch_open_orders(self.symbol)
            for order in open_orders:
                if order['side'] == side:
                    self.exchange.cancel_order(order['id'], self.symbol)
                    logging.info(f"Closed {side} order ID: {order['id']} for {self.symbol}")
                    self.log_closed_trade(order, float(order['price']))
        except Exception as e:
            logging.error(f"An error occurred while closing order: {e}")

    def show_open_positions(self):
        try:
            open_orders = self.exchange.fetch_open_orders(self.symbol)
            positions = "Open Positions:\n"
            for order in open_orders:
                positions += f"ID: {order['id']}, Symbol: {order['symbol']}, Side: {order['side']}, Amount: {order['amount']}, Price: {order['price']}, Status: {order['status']}\n"
            return positions if open_orders else "No open positions."
        except Exception as e:
            logging.error(f"An error occurred while fetching open positions: {e}")
            return "An error occurred while fetching open positions."
        
    def execute_order(self):
        ohlcv = self.fetch_data()
        logging.info(f"Fetched market data: {ohlcv}")
        self.save_to_db(ohlcv)

        df = self.strategy.read_price()
        df = self.strategy.calc_indicators(df)
        df = self.strategy.entry_signals(df)
        df = self.strategy.exit_signals(df)

        latest = df.iloc[-1]
        logging.info(f"Latest data for decision making: {latest}")

        balance = self.get_balance()
        if balance is None:
            logging.error("Failed to fetch balance, skipping order execution.")
            return

        current_price = latest['close']
        order_amount = self.calc_order(balance, current_price)

        if latest.get('enter_long') == 1:
            logging.info(f"Entering long position with amount: {order_amount}")
            self.place_order('buy', order_amount)
        elif latest.get('enter_short') == 1:
            logging.info(f"Entering short position with amount: {order_amount}")
            self.place_order('sell', order_amount)

        if latest.get('exit_long') == 1:
            logging.info("Exiting long positions.")
            self.close_orders('buy')
        elif latest.get('exit_short') == 1:
            logging.info("Exiting short positions.")
            self.close_orders('sell')

# Add a method or loop to trigger execute_order regularly
"""
if __name__ == "__main__":
    engine = TradingEngine()
    # For example, using threading to execute order every minute
    def run_trading_engine():
        while True:
            engine.execute_order()
            time.sleep(60)  # Sleep for 1 minute

"""