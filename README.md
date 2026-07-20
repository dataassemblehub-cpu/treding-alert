# Investment Intelligence Platform 📈

An explainable, deterministic, multi-factor long-term investment intelligence platform for Indian equities. 

This is **not** a simple stock screener. This system evaluates the fundamental business quality, financial risks, growth metrics, and current valuations of companies, translating them into human-readable, thesis-driven investment decisions.

## 🧠 System Architecture

The pipeline processes stocks through a rigorous sequence of analytical gates:

1. **Data Ingestion (`YFinanceProvider`)**: Fetches trailing 1-year price history alongside multi-year fundamental metrics (ROE, P/E, Debt/Equity, Free Cash Flow).
2. **Data Quality Gate**: Automatically downgrades or rejects analysis (`RESEARCH` status) if the underlying financial data from Yahoo Finance is missing or corrupt.
3. **Analytical Modules**:
   - `Quality`: Assesses profitability (ROE, Operating Margins).
   - `Growth`: Assesses YoY revenue and earnings expansion.
   - `Valuation`: Assesses entry price multiples.
   - `Risk`: Evaluates debt burdens and consecutive years of negative free cash flow.
4. **Scoring Engine (`scoring.py`)**: Computes a dynamic 0-100 score based on configurable metric weights (`config/scoring.yaml`).
5. **Decision Engine (`decision_engine.py`)**: Applies Hard Gates (e.g., severe red flags force an `AVOID` regardless of score) and classifies the stock into one of 6 decisions: **BUY**, **ACCUMULATE**, **WATCHLIST**, **WAIT**, **RESEARCH**, **AVOID**.
6. **Decision Transition Tracker**: Compares today's decision against the historical database to detect upgrades (🟢) and downgrades (🔴).
7. **Telegram Router**: Drops the noise (ignoring WAIT/AVOID) and routes actionable, thesis-driven alerts directly to your phone.

## 🚀 Usage

### 1. Dry Run / Validation Mode
Test the logic without writing to the database or triggering Telegram alerts. It outputs a distribution summary report at the end.
```bash
python main.py --dry-run
```

### 2. Targeted Testing
Test specific symbols to audit the system's reasoning:
```bash
python main.py --test-symbols TCS.NS,HDFCBANK.NS --dry-run
```

### 3. Production Run
Run the full universe, save the decisions to SQLite, and dispatch alerts to Telegram:
```bash
python main.py
```

### 4. Background Generators
Update the stock universe and volatility baselines (automated weekly via GitHub Actions):
```bash
python src/generators/universe.py
python src/generators/volatility.py
```

## ⚙️ Configuration

- **Scoring Weights**: Adjust how much `Quality` vs `Valuation` matters in `config/scoring.yaml`.
- **Telegram Routes**: Define multiple chat destinations (e.g., personal vs group) and verbosity profiles in `config/telegram.yaml`. Map these routes to actual IDs via your `.env` file (e.g., `TELEGRAM_CHAT_ID_PERSONAL`).
- **Research Alerts**: Add `detailed_research_alerts: true` to a destination in `telegram.yaml` to receive alerts for *every* stock (including AVOID/WAIT) to audit the system's rejection reasoning.

## 🗄️ Audit Trail & Backtesting

Every decision made by the system is permanently logged in the local SQLite database (`data/market_data.db`) under the `investment_decisions` table. 

This captures the exact `model_version`, data snapshot, individual component scores, and the generated thesis bullet points, completely preventing look-ahead bias and enabling robust historical backtesting.
