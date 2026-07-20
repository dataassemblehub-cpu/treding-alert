from dataclasses import dataclass

@dataclass
class ComponentScores:
    quality: float = 0.0
    growth: float = 0.0
    valuation: float = 0.0
    entry: float = 0.0
    risk: float = 0.0

@dataclass
class InvestmentScore:
    symbol: str
    overall: float
    components: ComponentScores
    confidence: str
