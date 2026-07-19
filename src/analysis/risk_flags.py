from src.models.analysis import AnalysisResult

def analyze_risk(financials: dict) -> AnalysisResult:
    flags = []
    if not financials:
        return AnalysisResult("risk", {"error": "No financials"}, ["NO_DATA"])
        
    fcf = financials.get("free_cash_flow")
    dte = financials.get("debt_to_equity")
    
    if fcf is not None and fcf < 0:
        flags.append("NEGATIVE_FCF")
        
    if dte is not None and dte > 2.0:
        flags.append("HIGH_DEBT")
        
    return AnalysisResult("risk", {"free_cash_flow": fcf, "debt_to_equity": dte}, flags)
