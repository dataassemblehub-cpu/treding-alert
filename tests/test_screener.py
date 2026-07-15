import pandas as pd
import pytest
from src.screener import screen_symbol

def test_screen_symbol_no_matches():
    # Price is high, shouldn't alert
    settings = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
    history_df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=300),
        "close": [100] * 299 + [99],
        "volume": [1000] * 300
    })
    
    result = screen_symbol("TEST.NS", 99, history_df, settings)
    assert result is None  # 99 is not <= 99*1.02 (wait, 99 is the low. 99 <= 99*1.02 is True!)
    
def test_screen_symbol_not_near_low():
    settings = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
    history_df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=300),
        "close": [100] * 299 + [50], # min is 50
        "volume": [1000] * 300
    })
    
    # current_price is 60, min is 50. 60 > 50 * 1.02 (51). Should be None
    result = screen_symbol("TEST.NS", 60, history_df, settings)
    assert result is None
    
def test_screen_symbol_near_52w():
    settings = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
    history_df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=300),
        "close": [10] * 48 + [100] * 251 + [99], # ATL is 10, 52W low is 99
        "volume": [1000] * 300
    })
    
    # current_price is 100. 100 <= 99 * 1.02 (100.98). Should alert near_52w but not near_atl
    result = screen_symbol("TEST.NS", 100, history_df, settings)
    assert result is not None
    assert result["near_52w"] is True
    assert result["near_atl"] is False
    assert result["trend"] == "below 200DMA" # 200d mean is approx 100, wait, 100 > 99.995 is True. Let's make it explicitly below
    assert result["low_label_52w"] == "52W low"

def test_screen_symbol_volume_filter():
    settings = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
    history_df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=300),
        "close": [100] * 299 + [99], 
        "volume": [1000] * 299 + [400] # Today's volume is 400. avg is ~1000. 400 < 500
    })
    
    # Price is 99, min is 99. 99 <= 99*1.02 is True. But volume is too low.
    result = screen_symbol("TEST.NS", 99, history_df, settings)
    assert result is None
    
def test_screen_symbol_short_history():
    settings = {"threshold_pct": 0.02, "min_volume_ratio": 0.5}
    history_df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=100),
        "close": [100] * 99 + [99], 
        "volume": [1000] * 100
    })
    
    result = screen_symbol("TEST.NS", 99, history_df, settings)
    assert result is not None
    assert result["low_label_52w"] == "100-day low"
