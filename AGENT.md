# AGENT.md — Trading Alert System

This file gives any AI coding agent (Claude Code, Cursor, Copilot Workspace, etc.) the
context needed to work on this repository correctly. Read this before making changes.

## 1. What this project does

A personal, automated screener that runs several times a day and tells the user, via
Telegram, which stocks (across categories like IT, Finance, Gold, Sports/Consumer, etc.)
are currently trading near their **52-week low** or **all-time low (ATL)** — so the user
can consider them for regular (DCA-style) investing.

This is a **screening/alerting tool**, not a trading bot. It never places orders. It only
reads data and sends notifications.

## 2. Non-negotiable design principles

- **No execution, ever.** This system only reads market data and sends alerts. Do not add
  order placement, even if a broker API is later integrated.
- **Idempotent runs.** Each run should be safe to re-run without side effects other than
  possibly sending a duplicate-suppressed alert.
- **Fail loud, not silent.** If a data fetch fails for a symbol, log it and skip that
  symbol — never crash the whole run or silently report stale data as fresh.
- **No hardcoded secrets.** Telegram bot token and chat ID come from environment
  variables / GitHub Actions secrets, never committed to the repo.
- **Cheap to run.** Prefer free-tier infra (GitHub Actions cron + SQLite) until the user
  explicitly asks to scale to a paid broker API or a server.

## 3. Architecture

```
config/
  universe.yaml         # symbol -> category mapping (user-curated watchlist)
  settings.yaml          # thresholds, run frequency, filters
data/
  price_history.db       # SQLite — daily closes, used to compute all-time-low
  alert_log.db            # SQLite — history of alerts already sent (for de-duplication)
src/
  fetcher.py              # pulls current price + 52W low + history via yfinance
  screener.py              # applies near-52W-low / near-ATL logic + filters
  notifier.py               # formats and sends Telegram messages
  main.py                    # orchestrates: fetch -> update history -> screen -> notify
.github/workflows/
  run_screener.yml            # cron schedule, runs main.py n times/day during market hours
```

Data flow per run:
`main.py` → `fetcher.py` (get today's price + historical closes for each symbol in
`universe.yaml`) → update `price_history.db` → `screener.py` (compute 52W low/ATL from
DB + apply filters from `settings.yaml`) → `notifier.py` (send Telegram message for any
new matches not already in `alert_log.db` today).

## 4. Screening logic (must be preserved unless user asks to change it)

For each symbol:

1. `current_price` = latest close from fetcher
2. `low_52w` = min(close) over trailing 252 trading days
3. `all_time_low` = min(close) over full stored history in `price_history.db`
4. Flag **"near 52W low"** if `current_price <= low_52w * (1 + threshold_pct)`
5. Flag **"near ATL"** if `current_price <= all_time_low * (1 + threshold_pct)`
6. `threshold_pct` default = 2%, configurable in `settings.yaml` (suggested range 2–5%)
7. **Volume filter**: skip flagging if today's volume < `min_volume_ratio` × 20-day
   average volume (default 0.5) — avoids flagging illiquid/false signals
8. **Trend sanity filter (optional, default ON)**: additionally tag whether price is
   above or below its 200-day moving average, so alerts distinguish "possible value buy"
   from "possible falling knife." Do not silently filter these out — always show both,
   just label them differently.
9. Do not add fundamental/balance-sheet filters unless the user explicitly asks — keep
   MVP purely price/volume based.

## 5. Data source conventions

- MVP uses `yfinance` (Python). NSE symbols need `.NS` suffix (e.g. `TCS.NS`), BSE uses
  `.BO`. Gold can be tracked via ETFs (e.g. `GOLDBEES.NS`) since there's no single "gold
  sector" ticker.
- `fetcher.py` should be written with a thin abstraction (`get_price_data(symbol)`) so the
  data source can be swapped later (e.g. Kite Connect) without touching `screener.py` or
  `notifier.py`.
- All-time-low needs full history, not just 52 weeks — fetch max available history once,
  then only fetch incremental daily data on subsequent runs (don't re-download full
  history every run; it's wasteful and yfinance may rate-limit).

## 6. Scheduling

- Runs via GitHub Actions cron (`.github/workflows/run_screener.yml`), not a self-hosted
  server.
- Only run during NSE market hours (9:15 AM–3:30 PM IST, Mon–Fri). Cron is in UTC — IST is
  UTC+5:30, so schedule accordingly and note this clearly in the workflow file comments.
- Default frequency: every 2 hours during market hours (adjustable by user).

## 7. Alerting conventions

- Telegram only for MVP (via bot token + chat ID stored as GitHub Actions secrets:
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
- One message per run, grouped by category, not one message per stock (avoid spam).
- De-duplicate: don't re-alert on the same symbol+signal on the same day. Use
  `alert_log.db` to check before sending.
- Message must include: symbol, category, current price, 52W low, ATL (if near),
  % from low, volume signal, trend signal (above/below 200DMA).

## 8. What NOT to do (guardrails for the agent)

- Do not add auto-execution/order placement.
- Do not remove the volume filter or trend label to "simplify" — they exist to reduce
  false positives.
- Do not commit `.env` files, API keys, or the Telegram token.
- Do not replace SQLite with a hosted DB unless the user asks — keep infra free/simple.
- Do not silently change the alert threshold — it must stay in `settings.yaml`, editable
  without touching code.

## 9. Suggested build order (for a fresh implementation)

1. `config/universe.yaml` with 5–10 stocks in just ONE category (e.g. IT) to validate the
   pipeline end-to-end.
2. `fetcher.py` — fetch + store price history in SQLite.
3. `screener.py` — implement 52W/ATL logic against the stored data, unit-testable without
   network calls.
4. `notifier.py` — Telegram send function, testable with a dummy message.
5. `main.py` — wire it together, run locally first.
6. `.github/workflows/run_screener.yml` — automate once step 5 works locally.
7. Expand `universe.yaml` to more categories only after the above is stable.

See `SKILL.md` for the reusable domain-logic reference and `PROMPT.md` for the exact
implementation prompt to hand to a coding agent.
