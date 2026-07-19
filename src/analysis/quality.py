from src.models.analysis import AnalysisResult

def analyze_quality(financials: dict) -> AnalysisResult:
    flags = []
    
    if not financials:
        return AnalysisResult("quality", {"error": "No financials"}, ["NO_DATA"])
        
    roe = financials.return_on_equity
    margin = financials.operating_margin
    
    if roe is not None and roe > 0.15:
        flags.append("HIGH_ROE")
    if margin is not None and margin > 0.20:
        flags.append("HIGH_MARGIN")
        
    return AnalysisResult(
        analysis_type="quality",
        raw_metrics={"roe": roe, "operating_margin": margin},
        flags=flags
    )
