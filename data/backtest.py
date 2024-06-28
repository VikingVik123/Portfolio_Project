from Supertrend_v2 import strategy
import vectorbt as vbt
import optuna

class BacktestStrategy:
    def __init__(self):
        self.strategy = strategy()
        self.strategy.apply_indicators()
        self.strategy.generate_signals()
        self.strategy.generate_exitsig()
        self.df = self.strategy.df
        self.initial_capital = 5000

    def run_backtest(self):
        # Extract signals
        entries_long = self.df['enter_long'] == 1
        exits_long = self.df['exit_long'] == 1
        entries_short = self.df['enter_short'] == 1
        exits_short = self.df['exit_short'] == 1
        
        # Run backtest
        pf = vbt.Portfolio.from_signals(
            close=self.df['close'],
            entries=entries_long,
            exits=exits_long,
            short_entries=entries_short,
            short_exits=exits_short,
            init_cash=self.initial_capital,
            fees=0.001,   #Example commission fees
            slippage=0.001,  # Example slippage
            freq='15m'  # Set the frequency to daily
        )
        
        return pf

    def performance_metrics(self):
        pf = self.run_backtest()
        stats = pf.stats()
        return stats
    
    def save_performance_metrics(self, filename='Performance_metrics.txt'):
        stats = self.performance_metrics()
        if stats is not None:
            with open(filename, 'a') as f:  # Open the file in append mode
                f.write("Performance Metrics\n")
                f.write("===================\n")
                f.write(stats.to_string())
                f.write('\n\n')  # Add a newline for separation between different metrics
            print(f"Performance metrics appended to {filename}")
        else:
            print("Failed to retrieve performance metrics")

backtest = BacktestStrategy()
performance = backtest.performance_metrics()

print(performance)
#backtest.save_performance_metrics()