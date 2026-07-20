import sqlite3
from typing import Optional
from src.models.decision import InvestmentDecision

RECOMMENDATION_RANKS = {
    "BUY": 6,
    "ACCUMULATE": 5,
    "WATCHLIST": 4,
    "WAIT": 3,
    "RESEARCH": 2,
    "AVOID": 1
}

class DecisionChangeDetector:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def detect_transition(self, new_decision: InvestmentDecision) -> Optional[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT recommendation FROM investment_decisions
                    WHERE symbol = ?
                    ORDER BY id DESC LIMIT 1
                ''', (new_decision.symbol,))
                row = cursor.fetchone()
                
                if row:
                    old_rec = row[0]
                    new_rec = new_decision.recommendation
                    
                    if old_rec != new_rec:
                        old_rank = RECOMMENDATION_RANKS.get(old_rec, 0)
                        new_rank = RECOMMENDATION_RANKS.get(new_rec, 0)
                        
                        if new_rank > old_rank:
                            return f"UPGRADE: {old_rec} → {new_rec}"
                        elif new_rank < old_rank:
                            return f"DOWNGRADE: {old_rec} → {new_rec}"
                        else:
                            return f"CHANGED: {old_rec} → {new_rec}"
                            
        except Exception:
            pass
            
        return None
