from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
import uuid

@dataclass
class Alert:
    symbol: str
    strategy_name: str
    current_price: float
    reference_price: float
    distance_pct: float
    threshold_used: float
    sector: str = ""
    industry: str = ""
    trend: str = ""
    severity: str = "INFO"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
