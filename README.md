# Trading Alert System

An explainable, deterministic, multi-factor long-term investment intelligence platform for Indian equities.

## Architecture

The system evaluates stocks through a multi-factor analysis engine, generating a clear `InvestmentDecision`.

### Core Layers
- **Domain Models (`src/models/`)**: Strongly typed data classes for `Stock`, `AnalysisResult`, `ComponentScores`, and `InvestmentDecision`.
- **Data Providers (`src/providers/`)**: Abstractions (like `YFinanceProvider`) to fetch historical financial metrics and fundamental data.
- **Analysis Modules (`src/analysis/`)**: Deterministic modules that evaluate Quality, Growth, Valuation, and Risk flags.
- **Scoring Engine (`src/strategies/scoring.py`)**: Configurable scoring mapped from `config/scoring.yaml`.
- **Decision Engine (`src/strategies/decision_engine.py`)**: Uses hard gates and multi-factor models to construct a comprehensive investment thesis (e.g. Horizons, Review Periods, Red Flags).
- **Portfolio Ranker (`src/strategies/portfolio_ranker.py`)**: Audits all historical decisions into `data/market_data.db` to prevent look-ahead bias and allow future backtesting.
- **Telegram Router (`src/services/telegram_router.py`)**: Handles multiple destinations, graceful failure, and rich HTML notifications.

## Usage

Run the daily/hourly screener:
```bash
python main.py
```

Update the universe and volatility baselines (usually run weekly via GitHub Actions):
```bash
python src/generators/universe.py
python src/generators/volatility.py
```

## Audit Trail

Every decision made by the system is permanently logged in the SQLite database under `investment_decisions`, capturing the exact `model_version` (e.g. `phase_3_v1`), data snapshot, and resulting scores for future historical analysis.
