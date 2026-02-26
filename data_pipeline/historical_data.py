import yfinance as yf
import pandas as pd

def fetch_historical(symbol, period="5y", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            print(f"No historical data found for {symbol}")
            return None
        hist.reset_index(inplace=True)
        return hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"Error fetching historical for {symbol}: {e}")
        return None
