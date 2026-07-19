from src.models.analysis import AnalysisResult

def analyze_risk(financials) -> AnalysisResult:
    flags = []
    if not financials:
        return AnalysisResult("risk", {"error": "No financials"}, ["NO_DATA"])
        
    fcf = financials.free_cash_flow
    historical_fcf = financials.historical_fcf
    dte = financials.debt_to_equity
    
    if dte is not None:
        if dte > 3.0:
            flags.append("HIGH_DEBT_CRITICAL")
        elif dte > 2.0:
            flags.append("HIGH_DEBT_SEVERE")
        elif dte > 1.5:
            flags.append("HIGH_DEBT_WARNING")
            
    neg_count = 0
    if historical_fcf:
        for val in historical_fcf:
            if val < 0:
                neg_count += 1
            else:
                break
                
        if neg_count >= 4:
            flags.append("NEGATIVE_FCF_CRITICAL")
        elif neg_count >= 2:
            flags.append("NEGATIVE_FCF_SEVERE")
        elif neg_count == 1:
            flags.append("NEGATIVE_FCF_WARNING")
    
    return AnalysisResult("risk", {"free_cash_flow": fcf, "debt_to_equity": dte, "fcf_neg_years": neg_count}, flags)
