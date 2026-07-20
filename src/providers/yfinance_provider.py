import yfinance as yf
import logging
from typing import Optional
from .base import FinancialDataProvider
from src.models.analysis import FinancialMetrics, MetricProvenance

class YFinanceProvider(FinancialDataProvider):
    def get_financial_metrics(self, symbol: str) -> Optional[FinancialMetrics]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
                
            historical_fcf = []
            try:
                cf = ticker.cashflow
                if not cf.empty and "Free Cash Flow" in cf.index:
                    fcf_series = cf.loc["Free Cash Flow"].dropna()
                    historical_fcf = [float(x) for x in fcf_series.values]
            except Exception as cf_e:
                logging.warning(f"Could not fetch historical cashflow for {symbol}: {cf_e}")
                
            prov = MetricProvenance(source="yfinance")
                
            return FinancialMetrics(
                symbol=symbol,
                pe_ratio=info.get("trailingPE"),
                forward_pe=info.get("forwardPE"),
                peg_ratio=info.get("pegRatio"),
                debt_to_equity=info.get("debtToEquity"),
                return_on_equity=info.get("returnOnEquity"),
                historical_fcf=historical_fcf,
                operating_margin=info.get("operatingMargins"),
                revenue_growth=info.get("revenueGrowth"),
                earnings_growth=info.get("earningsGrowth"),
                provenance=prov
            )
        except Exception as e:
            logging.error(f"Error fetching financial metrics for {symbol}: {e}")
            return None
