import yfinance as yf
import pandas as pd
import logging
import datetime

def fetch_history(symbol: str, period: str = "max") -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            logging.error(f"{symbol}: No price data found.")
            return pd.DataFrame()
        
        df = df.reset_index()
        # Rename columns to standard lowercase
        df.rename(columns={"Date": "date", "Close": "close", "Volume": "volume"}, inplace=True)
        
        # Strip timezone if present
        if df['date'].dt.tz is not None:
            df['date'] = df['date'].dt.tz_localize(None)
            
        return df[['date', 'close', 'volume']]
    except Exception as e:
        logging.error(f"Failed to fetch {symbol}: {e}")
        return pd.DataFrame()

def backfill_history(symbol: str) -> pd.DataFrame:
    return fetch_history(symbol, period="max")

def fetch_incremental_history(symbol: str, last_date: datetime.date) -> pd.DataFrame:
    df = fetch_history(symbol, period="1mo")
    if df.empty:
        return df
    
    last_datetime = pd.to_datetime(last_date)
    return df[df['date'] > last_datetime].copy()
