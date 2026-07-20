from abc import ABC, abstractmethod
from typing import Optional
from src.models.analysis import FinancialMetrics

class FinancialDataProvider(ABC):
    @abstractmethod
    def get_financial_metrics(self, symbol: str) -> Optional[FinancialMetrics]:
        """Fetch fundamental financial metrics for a given symbol."""
        pass
