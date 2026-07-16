from typing import Optional
from src.models import Stock, Alert
from .base import Strategy

class Near52WeekLowStrategy(Strategy):
    @property
    def name(self) -> str:
        return "Near 52W Low"

    def run(self, stock: Stock, current_price: float) -> Optional[Alert]:
        df = stock.history
        if df.empty or len(df) < 20:
            return None

        trailing_year = df.tail(252)
        low_52w = float(trailing_year["close"].min())
        
        distance_pct = (current_price / low_52w - 1) * 100 if low_52w else 0.0
        threshold = stock.threshold_pct
        
        is_near_52w = current_price <= low_52w * (1 + threshold)
        if not is_near_52w:
            return None
            
        ma_200 = df["close"].tail(200).mean()
        trend = "above 200DMA" if current_price > ma_200 else "below 200DMA"
        
        return Alert(
            symbol=stock.symbol,
            strategy_name=self.name,
            current_price=current_price,
            reference_price=low_52w,
            distance_pct=distance_pct,
            threshold_used=threshold,
            sector=stock.sector,
            industry=stock.industry,
            trend=trend
        )
