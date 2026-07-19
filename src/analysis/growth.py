from src.models.analysis import AnalysisResult

def analyze_growth(financials: dict) -> AnalysisResult:
    flags = []
    if not financials:
        return AnalysisResult("growth", {"error": "No financials"}, ["NO_DATA"])
        
    rev_growth = financials.revenue_growth
    earn_growth = financials.earnings_growth
    
    if rev_growth is not None and rev_growth > 0.10:
        flags.append("HIGH_REVENUE_GROWTH")
    if earn_growth is not None and earn_growth < 0:
        flags.append("NEGATIVE_EARNINGS_GROWTH")
        
    return AnalysisResult("growth", {"revenue_growth": rev_growth, "earnings_growth": earn_growth}, flags)
