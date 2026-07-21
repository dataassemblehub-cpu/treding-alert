from typing import List
from src.models.decision import InvestmentDecision

class NotificationProvider:
    """Base class for all notification providers (Telegram, Email, Discord, etc.)"""
    
    def __init__(self, config: dict):
        self.config = config
        
    def format_decision(self, decision: InvestmentDecision) -> str:
        """Format the decision into a string suitable for the provider."""
        raise NotImplementedError
        
    def send_batch(self, decisions: List[InvestmentDecision]) -> bool:
        """Send a batch of decisions to the provider's destinations."""
        raise NotImplementedError
