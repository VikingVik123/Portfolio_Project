import pandas as pd
import numpy as np
import pandas_ta as pta
import sqlite3
import logging

def hvi(dataframe, period=10):
    """
    Highest Volume Index by Paratica; a custom indicator from tradingview
    """
    HV = dataframe['volume'].rolling(window=period).max()
    HVI = dataframe['volume'] * 100 / HV.shift(1)
    return HVI

class Strategy:
    def __init__(self):
        self.conn = sqlite3.connect('app.db')

    def read_price(self):
        logging.info("Reading price data")
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM btc_usdt_prices""")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['id', 'timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    
    def calc_indicators(self, df):
        logging.info("calculating indicators")
        df['sma20'] = pta.sma(df['close'], timeperiod=20)
        df['sma100'] = pta.sma(df['close'], timeperiod=100)
        df['hvi'] = hvi(df, period=10)

        # Supertrend
        periodo = 7
        atr_multiplicador = 4.0
        df['ST_long'] = pta.supertrend(df['high'], df['low'], df['close'], length=periodo, multiplier=atr_multiplicador)[f'SUPERTl_{periodo}_{atr_multiplicador}']
        df['ST_short'] = pta.supertrend(df['high'], df['low'], df['close'], length=periodo, multiplier=atr_multiplicador)[f'SUPERTs_{periodo}_{atr_multiplicador}']     
        
        return df
    
    def entry_signals(self, df):
        df.loc[
            (
                (df['close'] > df['sma20']) &
                (df['close'] > df['sma100']) &
                (df['hvi'] > 100) &
                (df['close'] > df['ST_long']) &
                (df['volume'] > 0) 
            ),
            'enter_long'] = 1
        df.loc[
            (
                (df['close'] < df['sma20']) &
                (df['close'] < df['sma100']) &
                (df['hvi'] > 100) &
                (df['close'] < df['ST_short']) &
                (df['volume'] > 0)
            ),
            'enter_short'] = 1
        return df
    
    def exit_signals(self, df):
        df.loc[
            (df['close'] < df['ST_long']),
            'exit_long'] = 1
        df.loc[
            (df['close'] > df['ST_short']),
            'exit_short'] = 1
        
        return df
