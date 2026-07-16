from dataclasses import dataclass, field
import pandas as pd

@dataclass
class Stock:
    symbol: str
    company: str = ""
    sector: str = ""
    industry: str = ""
    market_cap: float = 0.0
    avg_volume: int = 0
    threshold_pct: float = 0.02  # Default threshold if none is configured
    history: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
