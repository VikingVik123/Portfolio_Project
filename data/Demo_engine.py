from Market_data import MarketData
from Supertrend_v2 import strategy

class DemoTrading(strategy):

    def __init__(self, strategy):
        self.strategy = strategy
        self.initial_balance = 100000  # Initial balance in USD
        self.balance = self.initial_balance
        self.position = 0
        self.position_value = 0
        self.trades = []
        self.current_price = 0
        self.df = self.strategy.df

    def run(self):
        for i in range(len(self.df)):
            self.current_price = self.df['close'].iloc[i]
            if self.df['enter_long'].iloc[i] == 1:
                self.enter_long(i)
            elif self.df['enter_short'].iloc[i] == 1:
                self.enter_short(i)
            elif self.df['exit_long'].iloc[i] == 1 and self.position > 0:
                self.exit_long(i)
            elif self.df['exit_short'].iloc[i] == 1 and self.position < 0:
                self.exit_short(i)

        # Finalize any open positions at the end of the data
        if self.position != 0:
            self.exit_position(len(self.df) - 1)

        return self.calculate_performance()