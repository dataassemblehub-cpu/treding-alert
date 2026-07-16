import pandas as pd
import pytest
from src.models import Stock
from src.strategies.near_52w_low import Near52WeekLowStrategy

def test_strategy_no_matches():
    strategy = Near52WeekLowStrategy()
    history_df = pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.today().date(), periods=300),
        "close": [100.0] * 299 + [99.0],
        "volume": [1000] * 300
    })
    
    stock = Stock(symbol="TEST.NS", threshold_pct=0.02, history=history_df)
    
    # 105 is not <= 99 * 1.02 (100.98), should return None
    result = strategy.run(stock, 105.0)
    assert result is None
    
def test_strategy_not_near_low():
    strategy = Near52WeekLowStrategy()
    history_df = pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.today().date(), periods=300),
        "close": [100.0] * 299 + [50.0], # min is 50
        "volume": [1000] * 300
    })
    
    stock = Stock(symbol="TEST.NS", threshold_pct=0.02, history=history_df)
    result = strategy.run(stock, 60.0)
    assert result is None
    
def test_strategy_near_52w():
    strategy = Near52WeekLowStrategy()
    history_df = pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.today().date(), periods=300),
        "close": [10.0] * 48 + [100.0] * 251 + [99.0], # ATL is 10, 52W low is 99
        "volume": [1000] * 300
    })
    
    stock = Stock(symbol="TEST.NS", threshold_pct=0.02, history=history_df)
    result = strategy.run(stock, 100.0)
    
    assert result is not None
    assert result.strategy_name == "Near 52W Low"
    assert result.trend == "above 200DMA" 
    
def test_strategy_short_history():
    strategy = Near52WeekLowStrategy()
    history_df = pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.today().date(), periods=15), # Too short
        "close": [100.0] * 14 + [99.0], 
        "volume": [1000] * 15
    })
    
    stock = Stock(symbol="TEST.NS", threshold_pct=0.02, history=history_df)
    result = strategy.run(stock, 99.0)
    assert result is None
