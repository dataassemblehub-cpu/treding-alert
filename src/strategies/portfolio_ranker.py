import sqlite3
import os
from typing import List
from src.models.decision import InvestmentDecision

class PortfolioRanker:
    def __init__(self, db_path=None):
        if not db_path:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'market_data.db')
        self.db_path = db_path
        
    def rank_and_filter(self, decisions: List[InvestmentDecision]) -> List[InvestmentDecision]:
        ranked = sorted(decisions, key=lambda d: d.investment_score, reverse=True)
        # Apply sector concentration checks here if configured
        return ranked

    def audit_decision(self, decision: InvestmentDecision):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO investment_decisions 
                (symbol, recommendation, investment_score, quality_score, growth_score, valuation_score,
                 entry_score, risk_score, confidence, horizon, review_period, thesis, red_flags,
                 data_snapshot_timestamp, model_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.symbol, decision.recommendation, decision.investment_score,
                decision.scores.get('quality', 0), decision.scores.get('growth', 0),
                decision.scores.get('valuation', 0), decision.scores.get('entry', 0),
                decision.scores.get('risk', 0), decision.confidence, decision.investment_horizon,
                decision.review_period, "|".join(decision.thesis), "|".join(decision.red_flags),
                decision.data_snapshot_timestamp, decision.model_version
            ))
