import os
import sqlite3
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_alert_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_log (
            symbol TEXT,
            signal_type TEXT,
            date TEXT,
            PRIMARY KEY (symbol, signal_type, date)
        )
    ''')
    conn.commit()
    conn.close()

def filter_already_sent(alerts, db_path, today_str):
    """
    alerts: list of dicts from screener
    Returns only alerts that haven't been sent today.
    """
    init_alert_db(db_path)
    filtered = []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for alert in alerts:
        symbol = alert['symbol']
        near_52w = alert['near_52w']
        near_atl = alert['near_atl']
        
        signals = []
        if near_atl: signals.append("ATL")
        if near_52w: signals.append("52W")
        
        new_signals = []
        for sig in signals:
            cursor.execute("SELECT 1 FROM alert_log WHERE symbol=? AND signal_type=? AND date=?", (symbol, sig, today_str))
            if not cursor.fetchone():
                new_signals.append(sig)
                
        if new_signals:
            alert['_new_signals'] = new_signals
            filtered.append(alert)
            
    conn.close()
    return filtered

def format_telegram_message(categorized_alerts):
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    lines = [f"📉 Trading Alert — {now_str}", ""]
    
    has_alerts = False
    for category, alerts in categorized_alerts.items():
        if not alerts:
            continue
        has_alerts = True
        lines.append(category)
        for a in alerts:
            sym = a['symbol']
            price = a['current_price']
            trend = a['trend']
            trend_warn = " ⚠️" if "below" in trend else ""
            
            if a['near_atl']:
                dist = a['pct_from_atl']
                reason = f"near ATL ₹{a['all_time_low']:.2f}, {dist}% away"
            else:
                dist = a['pct_from_52w_low']
                reason = f"{dist}% from {a['low_label_52w']} ₹{a['low_52w']:.2f}"
                
            line = f" • {sym} — ₹{price:.2f} ({reason}) — {trend}{trend_warn}"
            lines.append(line)
        lines.append("")
        
    if not has_alerts:
        return None
        
    return "\n".join(lines).strip()

def send_telegram_and_log(categorized_alerts, db_path):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logging.warning("Telegram credentials not found. Skipping alert.")
        return False
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    filtered_categorized = {}
    for cat, alerts in categorized_alerts.items():
        filtered = filter_already_sent(alerts, db_path, today_str)
        if filtered:
            filtered_categorized[cat] = filtered
            
    msg = format_telegram_message(filtered_categorized)
    if not msg:
        logging.info("No new alerts to send after filtering.")
        return True 
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logging.info("Telegram message sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False
        
    # Log sent alerts to DB ONLY on success
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    records = []
    for cat, alerts in filtered_categorized.items():
        for a in alerts:
            for sig in a['_new_signals']:
                records.append((a['symbol'], sig, today_str))
                
    if records:
        cursor.executemany("INSERT OR IGNORE INTO alert_log (symbol, signal_type, date) VALUES (?, ?, ?)", records)
        conn.commit()
    conn.close()
    
    return True
