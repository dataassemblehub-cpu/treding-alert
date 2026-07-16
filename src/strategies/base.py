from abc import ABC, abstractmethod
from typing import Optional
from src.models import Stock, Alert

class Strategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def run(self, stock: Stock, current_price: float) -> Optional[Alert]:
        """
        Executes the strategy logic on the given stock.
        Returns an Alert object if the criteria are met, otherwise None.
        """
        pass
