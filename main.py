import os
import yaml
import logging
from dotenv import load_dotenv

from src.fetcher import fetch_and_store_history, get_latest_price_data
from src.screener import screen_symbol
from src.notifier import send_telegram_and_log

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def main():
    # 1. Load environment variables
    load_dotenv()
    
    # 2. Set up paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, 'config')
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    settings_path = os.path.join(config_dir, 'settings.yaml')
    universe_path = os.path.join(config_dir, 'universe.yaml')
    price_db_path = os.path.join(data_dir, 'price_history.db')
    alert_db_path = os.path.join(data_dir, 'alert_log.db')
    
    # 3. Load configurations
    settings = load_config(settings_path)
    universe = load_config(universe_path)
    
    categorized_alerts = {}
    
    # 4. Iterate over universe
    for category, symbols in universe.items():
        if not symbols:
            continue
            
        alerts_for_cat = []
        for symbol in symbols:
            try:
                logging.info(f"Processing {symbol}...")
                
                # Fetch latest price
                current_price, current_volume = get_latest_price_data(symbol)
                if current_price is None:
                    continue
                    
                # Fetch/update history
                history_df = fetch_and_store_history(symbol, price_db_path)
                if history_df.empty:
                    logging.warning(f"No history available for {symbol}")
                    continue
                    
                # Screen
                alert_data = screen_symbol(symbol, current_price, history_df, settings)
                if alert_data:
                    alerts_for_cat.append(alert_data)
                    logging.info(f"🚨 MATCH: {symbol}")
                else:
                    logging.info(f"No match for {symbol}")
                    
            except Exception as e:
                logging.error(f"Error processing {symbol}: {e}")
                
        if alerts_for_cat:
            categorized_alerts[category] = alerts_for_cat
            
    # 5. Send alerts (including empty notifications)
    logging.info("Attempting to send Telegram alerts...")
    success = send_telegram_and_log(categorized_alerts, alert_db_path)
    if success:
        logging.info("Run completed successfully with alerts sent.")
    else:
        logging.error("Run completed, but alert sending failed.")

if __name__ == "__main__":
    main()
