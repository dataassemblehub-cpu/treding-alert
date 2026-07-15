import yfinance as yf
import pandas as pd
import sqlite3
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            symbol TEXT,
            date TEXT,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')
    conn.commit()
    conn.close()

def get_latest_price_data(symbol):
    """Fetches the latest available price and volume data for a symbol."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='1d')
        if df.empty:
            logging.error(f"No recent data for {symbol}.")
            return None, None
        latest = df.iloc[-1]
        return float(latest['Close']), int(latest['Volume'])
    except Exception as e:
        logging.error(f"Failed to fetch latest data for {symbol}: {e}")
        return None, None

def fetch_and_store_history(symbol, db_path):
    """
    Decides whether to backfill or just update history for a given symbol.
    Backfills max available if no history exists.
    Updates only new data if history exists.
    Returns the full history as a DataFrame (columns: date, close, volume, sorted ascending).
    """
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if we have data for this symbol
    query = "SELECT MAX(date) FROM price_history WHERE symbol = ?"
    cursor.execute(query, (symbol,))
    result = cursor.fetchone()
    
    try:
        ticker = yf.Ticker(symbol)
        if result and result[0]:
            last_date_str = result[0]
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            # Fetch with a small overlap to ensure no gaps, INSERT OR IGNORE will handle duplicates
            start_date = last_date - datetime.timedelta(days=5)
            logging.info(f"[{symbol}] Updating history since {start_date}")
            df = ticker.history(start=start_date.strftime('%Y-%m-%d'))
        else:
            logging.info(f"[{symbol}] Backfilling max history")
            df = ticker.history(period="max")
            
        if not df.empty:
            df = df.reset_index()
            date_col = 'Date' if 'Date' in df.columns else 'Datetime'
            
            # yfinance returns timezone-aware dates usually, convert to naive YYYY-MM-DD strings
            df['date_str'] = pd.to_datetime(df[date_col]).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
            
            records = []
            for _, row in df.iterrows():
                # Some APIs might return NaN for volume or close if trading was halted, skip those
                if pd.isna(row['Close']) or pd.isna(row['Volume']):
                    continue
                records.append((symbol, row['date_str'], float(row['Close']), int(row['Volume'])))
                
            cursor.executemany('''
                INSERT OR IGNORE INTO price_history (symbol, date, close, volume)
                VALUES (?, ?, ?, ?)
            ''', records)
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to fetch/store history for {symbol}: {e}")
    finally:
        # Always return whatever history we have
        df_full = pd.read_sql_query(
            "SELECT date, close, volume FROM price_history WHERE symbol = ? ORDER BY date ASC",
            conn,
            params=(symbol,)
        )
        conn.close()
        
    return df_full
