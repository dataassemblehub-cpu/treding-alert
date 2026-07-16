import logging
import pandas as pd
import sqlite3
import os
import datetime

def generate_universe():
    """
    Reads the master_universe.csv and populates the stocks table.
    """
    logging.info("Generating universe from master_universe.csv")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'master_universe.csv')
    if not os.path.exists(csv_path):
        logging.error("master_universe.csv not found")
        return
        
    df = pd.read_csv(csv_path)
    df['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # In a full implementation, this might fetch market_cap from yfinance
    # For now, we seed with basic info
    if 'market_cap' not in df.columns:
        df['market_cap'] = 0.0
    if 'average_volume' not in df.columns:
        df['average_volume'] = 0
        
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'market_data.db')
    with sqlite3.connect(db_path) as conn:
        df.to_sql('stocks', conn, if_exists='replace', index=False)
        logging.info(f"Saved {len(df)} stocks to database.")

if __name__ == "__main__":
    generate_universe()
