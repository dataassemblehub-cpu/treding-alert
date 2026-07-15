"""
Verifies screen_symbol() against the real price history already fetched
into data/price_history.db. No network calls — pure regression check.
"""
import sqlite3
import pandas as pd
from src.screener import screen_symbol

conn = sqlite3.connect("data/price_history.db")

def load(symbol):
    return pd.read_sql_query(
        "SELECT date, close, volume FROM price_history WHERE symbol=? ORDER BY date ASC",
        conn, params=(symbol,)
    )

# --- Test 1: default 2% threshold -> nothing should match today ---
settings_default = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
for sym in ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"]:
    df = load(sym)
    last_close = df["close"].iloc[-1]
    result = screen_symbol(sym, last_close, df, settings_default)
    print(f"[2% threshold] {sym}: {'MATCH' if result else 'no match'}")
    assert result is None, f"{sym} unexpectedly matched at 2% threshold"

# --- Test 2: 3% threshold -> WIPRO.NS is price-near its 252d low (2.66% away) ---
# NOTE: today's volume (10.39M) is below 50% of its 20d avg (11.11M required),
# so the volume filter correctly SUPPRESSES this -- proving the filter works.
settings_wide = {"threshold_pct": 0.03, "min_volume_ratio": 0.5}
df = load("WIPRO.NS")
last_close = df["close"].iloc[-1]
result = screen_symbol("WIPRO.NS", last_close, df, settings_wide)
assert result is None, "expected volume filter to suppress this alert"
print("[3% threshold, default volume filter] WIPRO.NS: suppressed by volume filter (as expected)")

# --- Test 3: same price threshold, volume filter relaxed -> should now match ---
settings_relaxed_vol = {"threshold_pct": 0.03, "min_volume_ratio": 0.4}
result = screen_symbol("WIPRO.NS", last_close, df, settings_relaxed_vol)
assert result is not None, "WIPRO.NS should match once volume filter is relaxed"
# NOTE: using == not `is` here, because screener.py currently returns np.bool_,
# not Python bool -- `is True` fails on np.True_. See bug #4 in the review.
assert result["near_52w"] == True
assert result["near_atl"] == False
print(f"[3% threshold, relaxed volume] WIPRO.NS: MATCH -- {result['pct_from_52w_low']}% from {result['low_label_52w']}, trend={result['trend']}")

conn.close()
print("\nAll checks passed.")