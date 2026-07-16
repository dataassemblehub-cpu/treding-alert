import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'market_data.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        symbol TEXT PRIMARY KEY,
        company TEXT,
        sector TEXT,
        industry TEXT,
        market_cap REAL,
        average_volume INTEGER,
        last_updated TEXT
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volatility (
        symbol TEXT PRIMARY KEY,
        atr REAL,
        threshold_pct REAL,
        atr_period INTEGER,
        updated_at TEXT
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        symbol TEXT,
        date TEXT,
        close REAL,
        volume INTEGER,
        PRIMARY KEY (symbol, date)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alert_log (
        symbol TEXT,
        signal_type TEXT,
        date TEXT,
        PRIMARY KEY (symbol, signal_type, date)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS strategy_config (
        strategy_name TEXT,
        param_key TEXT,
        param_value TEXT,
        PRIMARY KEY (strategy_name, param_key)
    )''')
    
    conn.commit()
    
    # Try to migrate data from old DBs if they exist
    old_alert_db = os.path.join(os.path.dirname(__file__), 'data', 'alert_log.db')
    if os.path.exists(old_alert_db):
        try:
            cursor.execute(f"ATTACH DATABASE '{old_alert_db}' AS old_alert")
            cursor.execute("INSERT OR IGNORE INTO alert_log (symbol, signal_type, date) SELECT symbol, signal, date FROM old_alert.alert_log")
            cursor.execute("DETACH DATABASE old_alert")
            print("Migrated alert_log.db")
        except Exception as e:
            print(f"Failed to migrate alert_log.db: {e}")
            
    old_history_db = os.path.join(os.path.dirname(__file__), 'data', 'price_history.db')
    if os.path.exists(old_history_db):
        try:
            cursor.execute(f"ATTACH DATABASE '{old_history_db}' AS old_history")
            cursor.execute("INSERT OR IGNORE INTO price_history (symbol, date, close, volume) SELECT symbol, date, close, volume FROM old_history.price_history")
            cursor.execute("DETACH DATABASE old_history")
            print("Migrated price_history.db")
        except Exception as e:
            print(f"Failed to migrate price_history.db: {e}")

    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
