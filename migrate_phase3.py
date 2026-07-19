import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'market_data.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fundamental Metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_metrics (
        symbol TEXT PRIMARY KEY,
        pe_ratio REAL,
        forward_pe REAL,
        peg_ratio REAL,
        debt_to_equity REAL,
        return_on_equity REAL,
        free_cash_flow REAL,
        operating_margin REAL,
        revenue_growth REAL,
        earnings_growth REAL,
        updated_at TEXT
    )''')
    
    # Structured Analysis Results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        symbol TEXT,
        analysis_type TEXT,
        result_json TEXT,
        updated_at TEXT,
        PRIMARY KEY (symbol, analysis_type)
    )''')
    
    # 0-100 Scores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        symbol TEXT PRIMARY KEY,
        quality REAL,
        growth REAL,
        valuation REAL,
        entry REAL,
        risk REAL,
        overall REAL,
        updated_at TEXT
    )''')
    
    # Audit Trail of Investment Decisions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investment_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        recommendation TEXT,
        investment_score REAL,
        quality_score REAL,
        growth_score REAL,
        valuation_score REAL,
        entry_score REAL,
        risk_score REAL,
        confidence TEXT,
        horizon TEXT,
        review_period TEXT,
        thesis TEXT,
        red_flags TEXT,
        data_snapshot_timestamp TEXT,
        model_version TEXT
    )''')
    
    # Notification delivery log for multi-destinations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notification_deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision_id INTEGER,
        destination_name TEXT,
        status TEXT,
        delivered_at TEXT,
        error_msg TEXT
    )''')
    
    conn.commit()
    conn.close()
    print("Phase 3 DB Migration complete.")

if __name__ == '__main__':
    migrate()
