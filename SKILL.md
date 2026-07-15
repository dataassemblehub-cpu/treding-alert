---
name: stock-low-screener
description: Use this skill whenever working on the Trading Alert System's screening logic — computing 52-week lows, all-time lows, applying volume/trend filters, managing the stock universe config, or formatting Telegram alerts. Trigger for tasks involving price_history.db, universe.yaml, settings.yaml, screener.py, fetcher.py, or notifier.py in this repo. Also trigger when the user asks to add a new stock category, change alert thresholds, or debug why a stock was/wasn't flagged.
---

# Stock Low Screener Skill

Domain logic reference for the Trading Alert System. Follow this exactly when writing or
modifying screening code — the logic is deliberately conservative to avoid false signals.

## Core definitions

- **52-week low (`low_52w`)**: minimum daily close over the trailing 252 trading days
  (~1 calendar year). Recompute from stored history; don't trust an API's cached field
  without knowing its update lag.
- **All-time low (`all_time_low`)**: minimum daily close over the full stored price
  history for that symbol. Only as accurate as how far back the history goes — note the
  earliest available date whenever reporting an ATL, e.g. "ATL since 2010."
- **Near-low threshold (`threshold_pct`)**: a stock is "near" a low if
  `current_price <= reference_low * (1 + threshold_pct)`. Default `threshold_pct = 0.02`
  (2%). Keep this configurable — never hardcode it in `screener.py`.

## Step-by-step screening algorithm

```python
def screen_symbol(symbol, current_price, history_df, settings):
    """
    history_df: DataFrame with columns [date, close, volume], sorted ascending by date.
    settings: dict loaded from settings.yaml
    Returns: dict or None
    """
    threshold = settings["threshold_pct"]           # e.g. 0.02
    min_vol_ratio = settings["min_volume_ratio"]      # e.g. 0.5
    trailing_year = history_df.tail(252)

    low_52w = trailing_year["close"].min()
    all_time_low = history_df["close"].min()

    near_52w = current_price <= low_52w * (1 + threshold)
    near_atl = current_price <= all_time_low * (1 + threshold)

    if not (near_52w or near_atl):
        return None

    # Volume filter — skip low-conviction moves
    avg_vol_20d = history_df["volume"].tail(20).mean()
    today_vol = history_df["volume"].iloc[-1]
    if today_vol < avg_vol_20d * min_vol_ratio:
        return None  # likely illiquid/noise, don't alert

    # Trend label — informational, never filters the alert out
    ma_200 = history_df["close"].tail(200).mean()
    trend = "above 200DMA (possible value zone)" if current_price > ma_200 \
            else "below 200DMA (caution — possible downtrend)"

    return {
        "symbol": symbol,
        "current_price": current_price,
        "low_52w": low_52w,
        "all_time_low": all_time_low,
        "pct_from_52w_low": round((current_price / low_52w - 1) * 100, 2),
        "pct_from_atl": round((current_price / all_time_low - 1) * 100, 2),
        "near_52w": near_52w,
        "near_atl": near_atl,
        "trend": trend,
    }
```

## Rules the agent must follow

1. **Never filter out a flagged stock because of trend** — only volume can suppress an
   alert. Trend is informational so the user isn't blindsided, not a hard filter.
2. **Always recompute lows from stored history**, not from a single API field, so ATL is
   consistent even if the data source changes later.
3. **Symbol format**: NSE symbols must carry the `.NS` suffix, BSE `.BO`, when using
   yfinance. Don't assume bare tickers work.
4. **Category tagging lives only in `config/universe.yaml`** — never hardcode
   symbol-to-category mapping in Python.
5. **De-duplication**: before sending an alert, check `alert_log.db` for
   `(symbol, signal_type, date)` — skip if already alerted today.
6. **Message formatting** — group by category, one Telegram message per run:

```
📉 Trading Alert — 13 Jul 2026, 11:00 AM

IT
 • TCS.NS — ₹3,120 (0.8% from 52W low ₹3,095) — above 200DMA

Finance
 • HDFC.NS — ₹1,410 (near ATL ₹1,395, 1.1% away) — below 200DMA ⚠️

Gold
 • GOLDBEES.NS — ₹58.2 (1.5% from 52W low) — above 200DMA
```

7. **Adding a new category**: just add entries to `universe.yaml` under a new category
   key — no code change needed. Example:

```yaml
Sports:
  - JUBLFOOD.NS   # example, user should curate actual list
  - THOMASCOOK.NS
```

## Common pitfalls to avoid

- Computing 52W low from too little history (guard: if `len(history_df) < 252`, compute
  low over what's available and label it "N-day low" instead of "52W low" so it's not
  misleading).
- Re-downloading full history every run — only fetch incremental data after first backfill.
- Sending an alert per stock instead of batching — will spam the user and hit Telegram
  rate limits with a large universe.
- Comparing `current_price` to intraday high/low instead of daily close — keep it
  close-based for consistency, note this explicitly in code comments.
