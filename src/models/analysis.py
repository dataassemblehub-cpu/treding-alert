from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class FinancialMetrics:
    symbol: str
    pe_ratio: float = None
    forward_pe: float = None
    peg_ratio: float = None
    debt_to_equity: float = None
    return_on_equity: float = None
    free_cash_flow: float = None
    operating_margin: float = None
    revenue_growth: float = None
    earnings_growth: float = None

@dataclass
class AnalysisResult:
    analysis_type: str # 'quality', 'growth', 'valuation', 'trend'
    raw_metrics: Dict[str, Any] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
