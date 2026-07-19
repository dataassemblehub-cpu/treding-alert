from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class InvestmentDecision:
    symbol: str
    recommendation: str
    
    investment_horizon: str
    review_period: str
    
    investment_score: float
    confidence: str
    
    scores: Dict[str, float]
    
    thesis: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    data_quality: str = "UNKNOWN"
    
    data_snapshot_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_version: str = "phase_3_v1"
