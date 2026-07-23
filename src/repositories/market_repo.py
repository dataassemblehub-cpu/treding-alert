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
        self._initialize_db()

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                company TEXT,
                sector TEXT,
                industry TEXT,
                market_cap REAL,
                average_volume INTEGER,
                last_updated TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS volatility (
                symbol TEXT PRIMARY KEY,
                atr REAL,
                threshold_pct REAL,
                atr_period INTEGER,
                updated_at TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                symbol TEXT,
                date TEXT,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (symbol, date)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_log (
                symbol TEXT,
                signal_type TEXT,
                date TEXT,
                PRIMARY KEY (symbol, signal_type, date)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_config (
                strategy_name TEXT,
                param_key TEXT,
                param_value TEXT,
                PRIMARY KEY (strategy_name, param_key)
            )
            ''')
            
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
                historical_fcf TEXT,
                provenance_source TEXT,
                provenance_timestamp TEXT,
                updated_at TEXT
            )
            ''')
            
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
            )
            ''')
            conn.commit()

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
            df_to_save.rename(columns={'Date': 'date', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            
        df_to_save['symbol'] = symbol
        
        try:
            df_to_save = df_to_save[['symbol', 'date', 'close', 'volume']]
            if pd.api.types.is_datetime64_any_dtype(df_to_save['date']):
                df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
            else:
                df_to_save['date'] = df_to_save['date'].astype(str)
                
            with self._get_connection() as conn:
                records = df_to_save.to_records(index=False)
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT OR IGNORE INTO price_history (symbol, date, close, volume)
                    VALUES (?, ?, ?, ?)
                ''', records)
                conn.commit()
        except Exception as e:
            pass

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
