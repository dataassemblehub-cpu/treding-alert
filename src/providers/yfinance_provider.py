import yfinance as yf
import logging
from typing import Optional
from .base import FinancialDataProvider
from src.models.analysis import FinancialMetrics

class YFinanceProvider(FinancialDataProvider):
    def get_financial_metrics(self, symbol: str) -> Optional[FinancialMetrics]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
                
            return FinancialMetrics(
                symbol=symbol,
                pe_ratio=info.get("trailingPE"),
                forward_pe=info.get("forwardPE"),
                peg_ratio=info.get("pegRatio"),
                debt_to_equity=info.get("debtToEquity"),
                return_on_equity=info.get("returnOnEquity"),
                free_cash_flow=info.get("freeCashflow"),
                operating_margin=info.get("operatingMargins"),
                revenue_growth=info.get("revenueGrowth"),
                earnings_growth=info.get("earningsGrowth")
            )
        except Exception as e:
            logging.error(f"Error fetching financial metrics for {symbol}: {e}")
            return None
