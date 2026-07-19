from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class MetricProvenance:
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class FinancialMetrics:
    symbol: str
    
    # Required metrics
    pe_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    
    # Historical Arrays (Newest to oldest)
    historical_fcf: List[float] = field(default_factory=list) 
    
    # Optional metrics
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    operating_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    
    provenance: MetricProvenance = field(default_factory=MetricProvenance)
    
    @property
    def free_cash_flow(self) -> Optional[float]:
        if self.historical_fcf:
            return self.historical_fcf[0]
        return None

    @property
    def data_quality(self) -> str:
        required = [self.pe_ratio, self.debt_to_equity, self.return_on_equity]
        provided_req = sum(1 for x in required if x is not None)
        
        provided_fcf = 1 if len(self.historical_fcf) > 0 else 0
        
        optionals = [self.forward_pe, self.peg_ratio, self.operating_margin, self.revenue_growth, self.earnings_growth]
        provided_opt = sum(1 for x in optionals if x is not None)
        
        total_metrics = len(required) + 1 + len(optionals)
        total_provided = provided_req + provided_fcf + provided_opt
        
        if provided_req + provided_fcf < 2:
            return "INSUFFICIENT"
            
        ratio = total_provided / total_metrics
        if ratio >= 0.8:
            return "HIGH"
        elif ratio >= 0.6:
            return "MEDIUM"
        elif ratio >= 0.4:
            return "LOW"
        else:
            return "INSUFFICIENT"

@dataclass
class AnalysisResult:
    analysis_type: str 
    raw_metrics: Dict[str, Any] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
