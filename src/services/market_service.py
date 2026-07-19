import logging
from src.repositories.market_repo import MarketRepository
from src.models import Stock
from src.fetcher import backfill_history
from src.providers.base import FinancialDataProvider

class MarketService:
    def __init__(self, repo: MarketRepository, provider: FinancialDataProvider = None):
        self.repo = repo
        self.provider = provider

    def prepare_stock(self, symbol: str) -> Stock:
        """
        Fetches the domain Stock object from the repository,
        updates its price history via the fetcher, and saves any new prices.
        """
        stock = self.repo.get_stock(symbol)
        
        # If history is missing, backfill
        if stock.history.empty:
            logging.info(f"[{symbol}] History empty. Triggering backfill.")
            df = backfill_history(symbol)
            if not df.empty:
                self.repo.save_prices(symbol, df)
                stock = self.repo.get_stock(symbol) # Reload to get updated history
        else:
            # Update history with incremental fetch
            try:
                # The fetcher logic used to do incremental fetch if dates were missing.
                # Here we just fetch the latest price and append if it doesn't exist.
                # Actually, the original fetcher just used yfinance to fetch history.
                # We can call get_latest_price_data or a dedicated incremental fetcher.
                last_date = stock.history['date'].iloc[-1].date()
                logging.info(f"[{symbol}] Updating history since {last_date}")
                
                # We will import the logic from fetcher that downloads missing dates
                from src.fetcher import fetch_incremental_history
                new_df = fetch_incremental_history(symbol, last_date)
                
                if not new_df.empty:
                    self.repo.save_prices(symbol, new_df)
                    stock = self.repo.get_stock(symbol) # Reload
            except Exception as e:
                logging.error(f"[{symbol}] Error updating history: {e}")
                
        # Also fetch financials if provider is set
        if self.provider:
            # Basic caching logic: only fetch if not in DB or can force fetch. 
            # We'll just fetch once per run for now if missing.
            current_metrics = self.repo.get_financial_metrics(symbol)
            if not current_metrics:
                logging.info(f"[{symbol}] Fetching fundamental metrics via Provider")
                metrics = self.provider.get_financial_metrics(symbol)
                if metrics:
                    self.repo.save_financial_metrics(metrics)
                
        return stock
