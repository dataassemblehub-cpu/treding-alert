import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'market_data.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add historical_fcf and provenance columns
    try:
        cursor.execute("ALTER TABLE financial_metrics ADD COLUMN historical_fcf TEXT")
    except sqlite3.OperationalError:
        pass # Column might already exist
        
    try:
        cursor.execute("ALTER TABLE financial_metrics ADD COLUMN provenance_source TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE financial_metrics ADD COLUMN provenance_timestamp TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("Phase 3.1 DB Migration complete.")

if __name__ == '__main__':
    migrate()
