import pytest
from src.models.analysis import AnalysisResult
from src.strategies.scoring import ScoringEngine
from src.strategies.decision_engine import DecisionEngine

@pytest.fixture
def engine():
    return DecisionEngine(ScoringEngine())

def test_insufficient_data(engine):
    decision = engine.evaluate("TEST.NS", {}, 50.0, data_quality="INSUFFICIENT")
    assert decision.recommendation == "RESEARCH"
    assert "INSUFFICIENT_DATA" in decision.red_flags

def test_case_a_strong_company_one_bad_fcf(engine):
    analysis_results = {
        "quality": AnalysisResult("quality", flags=["HIGH_ROE", "HIGH_MARGIN"]),
        "valuation": AnalysisResult("valuation", flags=["UNDERVALUED"]),
        "risk": AnalysisResult("risk", flags=["NEGATIVE_FCF_WARNING"]) 
    }
    decision = engine.evaluate("TEST.NS", analysis_results, 90.0, data_quality="HIGH")
    assert decision.recommendation in ["BUY", "ACCUMULATE"]
    assert any("Recent Negative" in w for w in decision.warnings)

def test_case_b_strong_company_persistent_bad_fcf(engine):
    analysis_results = {
        "quality": AnalysisResult("quality", flags=["HIGH_ROE", "HIGH_MARGIN"]),
        "risk": AnalysisResult("risk", flags=["NEGATIVE_FCF_CRITICAL"]) 
    }
    decision = engine.evaluate("TEST.NS", analysis_results, 90.0, data_quality="HIGH")
    assert decision.recommendation == "AVOID"
    assert any("CRITICAL" in r for r in decision.red_flags)

def test_case_c_strong_company_temp_debt(engine):
    analysis_results = {
        "quality": AnalysisResult("quality", flags=["HIGH_ROE", "HIGH_MARGIN"]),
        "risk": AnalysisResult("risk", flags=["HIGH_DEBT_WARNING"])
    }
    decision = engine.evaluate("TEST.NS", analysis_results, 90.0, data_quality="HIGH")
    assert decision.recommendation in ["BUY", "ACCUMULATE"]
    assert any("Debt to Equity > 1.5 (WARNING)" in w for w in decision.warnings)

def test_case_d_weak_company_increasing_debt(engine):
    analysis_results = {
        "quality": AnalysisResult("quality", flags=[]),
        "risk": AnalysisResult("risk", flags=["HIGH_DEBT_SEVERE"])
    }
    decision = engine.evaluate("TEST.NS", analysis_results, 20.0, data_quality="HIGH")
    assert decision.recommendation == "AVOID"
