import logging
import pandas as pd
import sqlite3
import os
import datetime
import yaml

def calculate_atr(df: pd.DataFrame, period=14) -> float:
    # Since our DB only has close prices, we approximate ATR using standard deviation of returns
    if len(df) < period:
        return 0.0
    returns = df['close'].pct_change().tail(period)
    std = returns.std()
    last_close = df['close'].iloc[-1]
    return float(std * last_close) if pd.notna(std) else 0.0

def generate_volatility():
    logging.info("Calculating ATR and updating volatility table")
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'market_data.db')
    
    settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.yaml')
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f) or {}
    except FileNotFoundError:
        settings = {}
        
    multiplier = settings.get('atr_multiplier', 1.0)
    
    with sqlite3.connect(db_path) as conn:
        try:
            symbols = pd.read_sql_query("SELECT symbol FROM stocks", conn)['symbol'].tolist()
        except pd.errors.DatabaseError:
            logging.error("Stocks table not found. Run universe generator first.")
            return
            
        vol_data = []
        for sym in symbols:
            df = pd.read_sql_query("SELECT close FROM price_history WHERE symbol = ? ORDER BY date ASC", conn, params=(sym,))
            if df.empty:
                continue
                
            atr = calculate_atr(df)
            last_close = df['close'].iloc[-1]
            
            if last_close > 0 and atr > 0:
                threshold_pct = (atr / last_close) * multiplier
            else:
                threshold_pct = 0.02
                
            vol_data.append({
                'symbol': sym,
                'atr': atr,
                'threshold_pct': threshold_pct,
                'atr_period': 14,
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        if vol_data:
            vol_df = pd.DataFrame(vol_data)
            vol_df.to_sql('volatility', conn, if_exists='replace', index=False)
            logging.info(f"Updated volatility for {len(vol_data)} stocks")

if __name__ == "__main__":
    generate_volatility()
