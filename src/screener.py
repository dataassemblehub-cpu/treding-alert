def screen_symbol(symbol, current_price, history_df, settings):
    """
    history_df: DataFrame with columns [date, close, volume], sorted ascending by date.
    settings: dict loaded from settings.yaml
    Returns: dict or None
    """
    threshold = settings.get("threshold_pct", 0.02)
    min_vol_ratio = settings.get("min_volume_ratio", 0.5)
    
    if history_df.empty:
        return None

    # Determine 52-week equivalent (252 trading days)
    trailing_year = history_df.tail(252)
    
    low_52w = trailing_year["close"].min()
    all_time_low = history_df["close"].min()
    
    # Label correctly if less than 252 days
    is_full_52w = len(trailing_year) == 252
    low_label_52w = "52W low" if is_full_52w else f"{len(trailing_year)}-day low"

    near_52w = current_price <= low_52w * (1 + threshold)
    near_atl = current_price <= all_time_low * (1 + threshold)

    if not (near_52w or near_atl):
        return None

    # Volume filter — skip low-conviction moves
    # Requires at least 20 days for a true 20d avg, if less, use what we have
    vol_history = history_df["volume"].tail(20)
    if vol_history.empty:
        return None
        
    avg_vol_20d = vol_history.mean()
    today_vol = history_df["volume"].iloc[-1]
    
    if today_vol < avg_vol_20d * min_vol_ratio:
        return None  # likely illiquid/noise, don't alert

    # Trend label — informational, never filters the alert out
    ma_200 = history_df["close"].tail(200).mean()
    trend_desc = "above 200DMA" if current_price > ma_200 else "below 200DMA"

    return {
        "symbol": symbol,
        "current_price": current_price,
        "low_52w": low_52w,
        "low_label_52w": low_label_52w,
        "all_time_low": all_time_low,
        "pct_from_52w_low": round((current_price / low_52w - 1) * 100, 2) if low_52w else 0,
        "pct_from_atl": round((current_price / all_time_low - 1) * 100, 2) if all_time_low else 0,
        "near_52w": near_52w,
        "near_atl": near_atl,
        "trend": trend_desc,
    }
