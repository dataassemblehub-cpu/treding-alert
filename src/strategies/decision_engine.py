from typing import Dict, List
from src.models.decision import InvestmentDecision
from src.models.scores import ComponentScores
from src.models.analysis import AnalysisResult
from src.strategies.scoring import ScoringEngine

class DecisionEngine:
    def __init__(self, scoring_engine: ScoringEngine):
        self.scoring_engine = scoring_engine

    def evaluate(self, symbol: str, analysis_results: Dict[str, AnalysisResult], entry_score: float, data_quality: str = "INSUFFICIENT") -> InvestmentDecision:
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
        
        if data_quality == "INSUFFICIENT":
            return InvestmentDecision(
                symbol=symbol,
                recommendation="RESEARCH",
                investment_horizon="unknown",
                review_period="N/A",
                investment_score=round(overall_score, 1),
                confidence="LOW",
                scores={
                    "quality": scores.quality,
                    "growth": scores.growth,
                    "valuation": scores.valuation,
                    "entry": scores.entry,
                    "risk": scores.risk
                },
                thesis=["Insufficient financial data to make an automated decision."],
                red_flags=["INSUFFICIENT_DATA"],
                warnings=[],
                data_quality=data_quality
            )
            
        r_res = analysis_results.get("risk")
        if r_res:
            if "NEGATIVE_FCF_CRITICAL" in r_res.flags:
                red_flags.append("Persistent Negative Free Cash Flow (CRITICAL)")
            elif "NEGATIVE_FCF_SEVERE" in r_res.flags:
                red_flags.append("Multiple Years Negative Free Cash Flow (SEVERE)")
            elif "NEGATIVE_FCF_WARNING" in r_res.flags:
                warnings.append("Recent Negative Free Cash Flow (WARNING)")
                
            if "HIGH_DEBT_CRITICAL" in r_res.flags:
                red_flags.append("Debt to Equity > 3.0 (CRITICAL)")
            elif "HIGH_DEBT_SEVERE" in r_res.flags:
                red_flags.append("Debt to Equity > 2.0 (SEVERE)")
            elif "HIGH_DEBT_WARNING" in r_res.flags:
                warnings.append("Debt to Equity > 1.5 (WARNING)")
                
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

        confidence = "HIGH" if not red_flags else "LOW"
        if data_quality == "LOW":
            confidence = "LOW"
            if recommendation in ["BUY", "ACCUMULATE"]:
                recommendation = "WATCHLIST"
                warnings.append("Recommendation capped at WATCHLIST due to LOW data quality.")
        elif data_quality == "MEDIUM":
            confidence = "MEDIUM"
            if recommendation in ["BUY", "ACCUMULATE"]:
                warnings.append("Data quality is MEDIUM. Verify manually.")
                
        return InvestmentDecision(
            symbol=symbol,
            recommendation=recommendation,
            investment_horizon="3-5 years",
            review_period="quarterly",
            investment_score=round(overall_score, 1),
            confidence=confidence,
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
            data_quality=data_quality
        )
