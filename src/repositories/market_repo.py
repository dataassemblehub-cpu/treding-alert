import sqlite3
import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
import os
from src.models import Stock, Alert
from src.models.analysis import FinancialMetrics, MetricProvenance

class MarketRepository:
    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'market_data.db')
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_symbols(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol FROM stocks")
            return [row[0] for row in cursor.fetchall()]

    def get_stock(self, symbol: str) -> Optional[Stock]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Fetch metadata
            cursor.execute('''
                SELECT s.company, s.sector, s.industry, s.market_cap, s.average_volume,
                       v.threshold_pct
                FROM stocks s
                LEFT JOIN volatility v ON s.symbol = v.symbol
                WHERE s.symbol = ?
            ''', (symbol,))
            
            row = cursor.fetchone()
            if not row:
                # Stock not explicitly in metadata, return default object
                return Stock(symbol=symbol)
                
            company, sector, industry, market_cap, avg_vol, threshold_pct = row
            
            # Fetch price history
            history_df = pd.read_sql_query(
                "SELECT date, close, volume FROM price_history WHERE symbol = ? ORDER BY date ASC",
                conn,
                params=(symbol,)
            )
            
            if not history_df.empty:
                # Convert date strings to datetime to keep dataframe types consistent
                history_df['date'] = pd.to_datetime(history_df['date'])
                
            return Stock(
                symbol=symbol,
                company=company or "",
                sector=sector or "",
                industry=industry or "",
                market_cap=market_cap or 0.0,
                avg_volume=avg_vol or 0,
                threshold_pct=threshold_pct or 0.02,
                history=history_df
            )

    def save_prices(self, symbol: str, history_df: pd.DataFrame):
        if history_df.empty:
            return
            
        # Ensure we have date, close, volume columns
        df_to_save = history_df.copy()
        if 'date' not in df_to_save.columns:
            df_to_save = df_to_save.reset_index()
            # If the index was DatetimeIndex, it's now a column named Date or date
            df_to_save.rename(columns={'Date': 'date', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            
        df_to_save['symbol'] = symbol
        
        # Keep only required columns and convert date to string
        df_to_save = df_to_save[['symbol', 'date', 'close', 'volume']]
        df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
        
        with self._get_connection() as conn:
            df_to_save.to_sql('price_history', conn, if_exists='append', index=False)
            
            # Pandas to_sql append with primary key constraint will throw an error if dupes exist
            # A more robust way is to use INSERT OR REPLACE, but to_sql doesn't support it natively easily.
            # So we use a temporary table approach or executemany.
            # For simplicity, we just delete existing records for these dates first, then insert.
            
            dates = df_to_save['date'].tolist()
            if dates:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(dates))
                cursor.execute(f"DELETE FROM price_history WHERE symbol = ? AND date IN ({placeholders})", [symbol] + dates)
                df_to_save.to_sql('price_history', conn, if_exists='append', index=False)

    def log_alert(self, alert: Alert):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = alert.timestamp.strftime('%Y-%m-%d')
            cursor.execute(
                "INSERT OR IGNORE INTO alert_log (symbol, signal_type, date) VALUES (?, ?, ?)",
                (alert.symbol, alert.strategy_name, date_str)
            )

    def has_alert_today(self, symbol: str, strategy: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT 1 FROM alert_log WHERE symbol = ? AND signal_type = ? AND date = ?",
                (symbol, strategy, date_str)
            )
            return cursor.fetchone() is not None

    def get_strategy_config(self, strategy: str) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT param_key, param_value FROM strategy_config WHERE strategy_name = ?", (strategy,))
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_financial_metrics(self, symbol: str) -> Optional[FinancialMetrics]:
        import json
        from src.models.analysis import FinancialMetrics, MetricProvenance
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pe_ratio, forward_pe, peg_ratio, debt_to_equity, 
                       return_on_equity, free_cash_flow, operating_margin, 
                       revenue_growth, earnings_growth, historical_fcf,
                       provenance_source, provenance_timestamp
                FROM financial_metrics WHERE symbol = ?
            ''', (symbol,))
            row = cursor.fetchone()
            if not row:
                return None
                
            try:
                hist_fcf = json.loads(row[9]) if row[9] else []
            except Exception:
                hist_fcf = []
                
            prov = MetricProvenance(source=row[10] or "unknown", timestamp=row[11] or "")
            
            return FinancialMetrics(
                symbol=symbol,
                pe_ratio=row[0],
                forward_pe=row[1],
                peg_ratio=row[2],
                debt_to_equity=row[3],
                return_on_equity=row[4],
                operating_margin=row[6],
                revenue_growth=row[7],
                earnings_growth=row[8],
                historical_fcf=hist_fcf,
                provenance=prov
            )

    def save_financial_metrics(self, metrics) -> None:
        import json
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            hist_fcf = json.dumps(metrics.historical_fcf) if metrics.historical_fcf else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO financial_metrics 
                (symbol, pe_ratio, forward_pe, peg_ratio, debt_to_equity, return_on_equity, 
                 free_cash_flow, operating_margin, revenue_growth, earnings_growth, updated_at,
                 historical_fcf, provenance_source, provenance_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.symbol, metrics.pe_ratio, metrics.forward_pe, metrics.peg_ratio,
                metrics.debt_to_equity, metrics.return_on_equity, metrics.free_cash_flow,
                metrics.operating_margin, metrics.revenue_growth, metrics.earnings_growth, now,
                hist_fcf, metrics.provenance.source, metrics.provenance.timestamp
            ))
