from typing import Dict, List
from src.models.decision import InvestmentDecision
from src.models.scores import ComponentScores
from src.models.analysis import AnalysisResult
from src.strategies.scoring import ScoringEngine

class DecisionEngine:
    def __init__(self, scoring_engine: ScoringEngine):
        self.scoring_engine = scoring_engine

    def evaluate(self, symbol: str, analysis_results: Dict[str, AnalysisResult], entry_score: float) -> InvestmentDecision:
        scores = self.scoring_engine.score(analysis_results, entry_score)
        
        weights = self.scoring_engine.weights
        overall_score = (
            scores.quality * (weights.get('quality', 40) / 100) +
            scores.growth * (weights.get('growth', 20) / 100) +
            scores.valuation * (weights.get('valuation', 20) / 100) +
            scores.entry * (weights.get('entry', 10) / 100) +
            scores.risk * (weights.get('risk', 10) / 100)
        )
        
        red_flags = []
        warnings = []
        thesis = []
        
        r_res = analysis_results.get("risk")
        if r_res:
            if "NEGATIVE_FCF" in r_res.flags:
                red_flags.append("Negative Free Cash Flow")
            if "HIGH_DEBT" in r_res.flags:
                red_flags.append("Debt to Equity > 2.0")
                
        if scores.quality > 70:
            thesis.append("Strong and consistent profitability")
        if scores.valuation > 70:
            thesis.append("Valuation is attractive")
        elif scores.valuation < 40:
            warnings.append("Valuation is not deeply discounted")
            
        if scores.entry > 70:
            thesis.append("Current entry conditions are favorable")
            
        if red_flags:
            recommendation = "AVOID"
            thesis = ["Critical red flags detected. Avoid for now."]
        elif overall_score > 80:
            recommendation = "BUY"
        elif overall_score > 65:
            recommendation = "ACCUMULATE"
        elif overall_score > 50:
            recommendation = "WATCHLIST"
        else:
            recommendation = "WAIT"

        return InvestmentDecision(
            symbol=symbol,
            recommendation=recommendation,
            investment_horizon="3-5 years",
            review_period="quarterly",
            investment_score=round(overall_score, 1),
            confidence="HIGH" if not red_flags else "LOW",
            scores={
                "quality": scores.quality,
                "growth": scores.growth,
                "valuation": scores.valuation,
                "entry": scores.entry,
                "risk": scores.risk
            },
            thesis=thesis,
            red_flags=red_flags,
            warnings=warnings,
            data_quality="HIGH"
        )
