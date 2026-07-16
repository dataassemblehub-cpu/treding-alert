import logging
import os
from src.repositories.market_repo import MarketRepository
from src.services.market_service import MarketService
from src.services.notification_service import NotificationService
from src.strategies.engine import StrategyEngine
from src.strategies.near_52w_low import Near52WeekLowStrategy

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logging.info("Starting Phase 2 Trading Alert Screener...")

    # Initialize dependencies
    repo = MarketRepository()
    market_service = MarketService(repo)
    notification_service = NotificationService(repo)
    
    # Initialize Strategy Engine
    engine = StrategyEngine()
    engine.register(Near52WeekLowStrategy())
    
    symbols = repo.get_all_symbols()
    if not symbols:
        logging.error("No symbols found in the universe. Run generators first.")
        return

    all_alerts = []

    for symbol in symbols:
        logging.info(f"Processing {symbol}...")
        try:
            # 1. Fetch domain object populated with DB data & latest prices
            stock = market_service.prepare_stock(symbol)
            
            # 2. Run through registered strategies
            alerts = engine.execute(stock)
            
            if alerts:
                all_alerts.extend(alerts)
            else:
                logging.info(f"No match for {symbol}")
                
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")

    # 3. Handle Notifications
    logging.info("Attempting to send Telegram alerts...")
    success = notification_service.send_alerts(all_alerts)
    if success:
        logging.info("Run completed successfully with alerts sent (or skipped if empty/duplicate).")
    else:
        logging.error("Run completed, but alert sending failed.")

if __name__ == "__main__":
    # Ensure working directory is the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
