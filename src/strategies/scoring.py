import yaml
import os
from src.models.scores import ComponentScores
from src.models.analysis import AnalysisResult
from typing import Dict

class ScoringEngine:
    def __init__(self):
        self.weights = self._load_weights()
        
    def _load_weights(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'scoring.yaml')
        try:
            with open(settings_path, 'r') as f:
                return yaml.safe_load(f).get('weights', {})
        except FileNotFoundError:
            return {'quality': 40, 'growth': 20, 'valuation': 20, 'entry': 10, 'risk': 10}

    def score(self, analysis_results: Dict[str, AnalysisResult], entry_score: float) -> ComponentScores:
        quality = 50.0
        growth = 50.0
        valuation = 50.0
        risk = 50.0
        
        q_res = analysis_results.get("quality")
        if q_res:
            if "HIGH_ROE" in q_res.flags: quality += 25
            if "HIGH_MARGIN" in q_res.flags: quality += 25
            if "NO_DATA" in q_res.flags: quality = 50.0
            
        g_res = analysis_results.get("growth")
        if g_res:
            if "HIGH_REVENUE_GROWTH" in g_res.flags: growth += 25
            if "NEGATIVE_EARNINGS_GROWTH" in g_res.flags: growth -= 25
            if "NO_DATA" in g_res.flags: growth = 50.0
            
        v_res = analysis_results.get("valuation")
        if v_res:
            if "UNDERVALUED" in v_res.flags: valuation += 30
            if "OVERVALUED" in v_res.flags: valuation -= 30
            if "NO_DATA" in v_res.flags: valuation = 50.0
            
        r_res = analysis_results.get("risk")
        if r_res:
            if "NEGATIVE_FCF" in r_res.flags: risk -= 30
            if "HIGH_DEBT" in r_res.flags: risk -= 30
            if "NO_DATA" in r_res.flags: risk = 50.0
            
        return ComponentScores(
            quality=max(0.0, min(100.0, quality)),
            growth=max(0.0, min(100.0, growth)),
            valuation=max(0.0, min(100.0, valuation)),
            entry=max(0.0, min(100.0, entry_score)),
            risk=max(0.0, min(100.0, risk))
        )
