import logging
from typing import List
from src.models import Stock, Alert
from .base import Strategy

class StrategyEngine:
    def __init__(self):
        self._strategies: List[Strategy] = []

    def register(self, strategy: Strategy):
        self._strategies.append(strategy)
        logging.info(f"Registered strategy: {strategy.name}")

    def execute(self, stock: Stock) -> List[Alert]:
        alerts = []
        if stock.history.empty:
            return alerts
            
        # The current price is typically the last close price
        current_price = float(stock.history['close'].iloc[-1])
        
        for strategy in self._strategies:
            try:
                alert = strategy.run(stock, current_price)
                if alert:
                    alerts.append(alert)
            except Exception as e:
                logging.error(f"Strategy {strategy.name} failed for {stock.symbol}: {e}")
                
        return alerts
