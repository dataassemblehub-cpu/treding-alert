from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

@dataclass
class InvestmentDecision:
    symbol: str
    investment_horizon: str
    review_period: str
    investment_score: float
    confidence: str
    scores: Dict[str, float]
    
    company_name: str = ""
    recommendation: str = "WAIT"   
    
    thesis: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    data_quality: str = "UNKNOWN"
    transition_alert: str = None
    
    data_snapshot_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_version: str = "phase_3.1_v1"
