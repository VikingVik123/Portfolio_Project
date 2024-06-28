import signal

from sqlalchemy import Null
from zmq import NULL
from Market_data import MarketData
import pandas_ta as pta
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def hvi(dataframe,period=10):
        """
        Highest Volume Index by Paratica; a custom indicator from tradingview
        """
        HV = dataframe['volume'].rolling(window=period).max()
        HVI = dataframe['volume'] * 100 / HV.shift(1)
        return HVI

class strategy(MarketData):
    """
    Trading strategy to generate signals
    """
    def __init__(self):
        super().__init__()
        self.df = self.hist_data()

    def apply_indicators(self):
        self.df['sma100'] = pta.sma(self.df['close'], length=100)
        self.df['sma20'] = pta.sma(self.df['close'], length=20)
        self.df['hvi'] = hvi(self.df, period=10)

        # Supertrend
        periodo = 7
        atr_multiplicador = 4.0
        
        supertrend_df = pta.supertrend(self.df['high'], self.df['low'], self.df['close'], length=periodo, multiplier=atr_multiplicador)
        
        if supertrend_df is not None and not supertrend_df.empty:
            self.df['ST_long'] = supertrend_df[f'SUPERTl_{periodo}_{atr_multiplicador}']
            self.df['ST_short'] = supertrend_df[f'SUPERTs_{periodo}_{atr_multiplicador}']
        else:
            self.df['ST_long'] = pd.NA
            self.df['ST_short'] = pd.NA
            print("Supertrend calculation failed, columns set to NA")

    def generate_signals(self):
        self.df['enter_long'] = 0
        self.df['enter_short'] = 0
        self.df.loc[
            (self.df['close'] > self.df['sma100']) &
            (self.df['close'] > self.df['sma20']) &
            (self.df['close'] > self.df['ST_long']) &
            (self.df['hvi'] > 100) &
            (self.df['volume'] > 0),

            'enter_long'
        ] = 1
        self.df.loc[
            (self.df['close'] < self.df['ST_short']) &
            (self.df['close'] < self.df['sma100']) &
            (self.df['close'] > self.df['sma20']) &
            (self.df['hvi'] > 100) &
            (self.df['volume'] > 0),
            'enter_short'
        ] = 1
        print(self.df)
        return self.df
    

    def generate_exitsig(self):
        self.df['exit_long'] = 0
        self.df['exit_short'] = 0
        previous_long = False  # Track previous state of ST_long
        for i in range(1, len(self.df)):
            # Check for ST_long to ST_short transition
            if previous_long and not pd.isna(self.df['ST_short'].iloc[i]) and (self.df['ST_long'].iloc[i] != self.df['ST_long'].iloc[i-1]):
                self.df.loc[i, 'exit_long'] = 1
                previous_long = False  # Reset previous state flag

            # Check for ST_short to ST_long transition
            if not previous_long and not pd.isna(self.df['ST_long'].iloc[i]) and (self.df['ST_short'].iloc[i] != self.df['ST_short'].iloc[i-1]):
                self.df.loc[i, 'exit_short'] = 1
                previous_long = True  # Set previous state flag

        return self.df
    
    """
    def visualize(self):
        fig = go.Figure()

        # Add close price line
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['close'], mode='lines', name='Close Price'))
        
        # Add SMA line
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['sma'], mode='lines', name='SMA'))

        # Add Supertrend lines
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['ST_long'], mode='lines', name='Supertrend Long', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['ST_short'], mode='lines', name='Supertrend Short', line=dict(color='red')))

        # Add entry and exit points
        fig.add_trace(go.Scatter(x=self.df[self.df['enter_long'] == 1].index, y=self.df['close'][self.df['enter_long'] == 1], mode='markers', name='Enter Long', marker=dict(color='green', symbol='triangle-up', size=10)))
        fig.add_trace(go.Scatter(x=self.df[self.df['enter_short'] == 1].index, y=self.df['close'][self.df['enter_short'] == 1], mode='markers', name='Enter Short', marker=dict(color='red', symbol='triangle-down', size=10)))
        fig.add_trace(go.Scatter(x=self.df[self.df['exit_long'] == 1].index, y=self.df['close'][self.df['exit_long'] == 1], mode='markers', name='Exit Long', marker=dict(color='purple', symbol='circle', size=10)))
        fig.add_trace(go.Scatter(x=self.df[self.df['exit_short'] == 1].index, y=self.df['close'][self.df['exit_short'] == 1], mode='markers', name='Exit Short', marker=dict(color='brown', symbol='circle', size=10)))

        fig.update_layout(title='Trading Strategy Visualization', xaxis_title='Date', yaxis_title='Price')
        fig.show()
    
    """
    def save(self):
         self.df.to_csv('Trading_signals.csv', index=False)
            
#strat = strategy()
#strat.apply_indicators()
#signals = strat.generate_signals()
#exit_signals = strat.generate_exitsig()
#print(exit_signals)
#strat.save()
#strat.visualize()