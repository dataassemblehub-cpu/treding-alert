from src.models.analysis import AnalysisResult

def analyze_valuation(financials: dict) -> AnalysisResult:
    flags = []
    if not financials:
        return AnalysisResult("valuation", {"error": "No financials"}, ["NO_DATA"])
        
    pe = financials.pe_ratio
    if pe is not None:
        if pe < 15:
            flags.append("UNDERVALUED")
        elif pe > 40:
            flags.append("OVERVALUED")
            
    return AnalysisResult("valuation", {"pe_ratio": pe}, flags)
