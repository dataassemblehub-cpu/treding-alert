# PRD.md

# Trading Alert & Long-Term Investment Intelligence System

**Version:** 3.0

------------------------------------------------------------------------

# 1. Product Summary

The product is an automated market intelligence platform for Indian
equities.

It monitors a defined stock universe, evaluates companies across
business quality, growth, valuation, market conditions, and risk, then
produces explainable investment research alerts.

The system communicates:

``` text
What is interesting?
Why is it interesting?
What action state is appropriate?
What is the intended investment horizon?
When should the thesis be reviewed?
What are the risks?
```

------------------------------------------------------------------------

# 2. Problem

Simple stock alerts are insufficient.

For example:

``` text
Stock is near 52-week low
```

does not answer:

-   Is the business healthy?
-   Is the stock cheap?
-   Is the decline justified?
-   Is the trend broken?
-   Is the company financially deteriorating?
-   Is this a short-term trade or long-term opportunity?
-   Should the investor buy all at once or accumulate gradually?
-   When should the thesis be reviewed?

The product must provide structured decision support rather than
isolated signals.

------------------------------------------------------------------------

# 3. Goals

## Primary Goals

1.  Identify high-quality investment candidates.
2.  Evaluate current entry conditions.
3.  Identify major risks and red flags.
4.  Rank opportunities consistently.
5.  Clearly communicate recommended action states.
6.  Communicate investment horizon.
7.  Communicate review period.
8.  Support multiple Telegram destinations.
9.  Preserve modularity for future strategies.
10. Enable historical backtesting.

------------------------------------------------------------------------

# 4. Non-Goals

The system must not:

-   Guarantee returns.
-   Guarantee that a stock will rise.
-   Claim a probability of profit without statistically valid
    calibration.
-   Replace professional financial advice.
-   Automatically trade real money in the initial version.
-   Use a single indicator as a complete investment decision.

------------------------------------------------------------------------

# 5. Users

## Primary User

A long-term investor who wants:

-   A systematic way to discover opportunities.
-   Reduced emotional decision-making.
-   Clear explanations.
-   Long-term investment horizons.
-   Risk warnings.
-   Portfolio diversification guidance.

------------------------------------------------------------------------

# 6. Core User Journey

``` text
User receives alert
      ↓
Reads recommendation
      ↓
Sees business quality
      ↓
Sees entry condition
      ↓
Sees risk
      ↓
Sees investment horizon
      ↓
Sees review period
      ↓
Decides whether to research or act
```

------------------------------------------------------------------------

# 7. Investment Decision Output

Every candidate must produce:

``` text
symbol
company
recommendation
business_score
entry_score
risk_score
overall_score
confidence
investment_horizon
review_period
thesis_validity
reasons
warnings
data_quality
```

------------------------------------------------------------------------

# 8. Recommendation States

## RESEARCH

Insufficient evidence for a stronger decision.

## WATCHLIST

Interesting business or setup, but timing or valuation is not yet
attractive.

## WAIT

The business may be strong, but current conditions are unfavorable.

## ACCUMULATE

A long-term thesis is attractive and phased entry may be appropriate.

## BUY_SMALL

The setup is attractive but uncertainty or risk remains elevated.

## BUY

Strong alignment across quality, valuation, trend, and risk.

## HOLD

Existing thesis remains valid.

## REDUCE

Risk or valuation has become materially less favorable.

## AVOID

Major risk, broken thesis, or insufficient data.

------------------------------------------------------------------------

# 9. Investment Horizon Requirements

The system must classify each recommendation.

Supported horizons:

``` text
SHORT_TERM: < 3 months
MEDIUM_TERM: 3-12 months
LONG_TERM: 1-3 years
VERY_LONG_TERM: 3-7+ years
```

The system must also provide:

``` text
review_period
```

Examples:

``` text
Monthly
Quarterly
After Earnings
Semi-annually
```

The system must distinguish:

``` text
Investment Horizon
```

from:

``` text
Review Period
```

A 5-year investment thesis may still require quarterly review.

------------------------------------------------------------------------

# 10. Analysis Requirements

## Quality

Evaluate where applicable:

-   ROE
-   ROCE
-   Profitability
-   Debt health
-   Interest coverage
-   Cash flow
-   Earnings stability
-   Margin stability

Metrics must be sector-aware.

------------------------------------------------------------------------

## Growth

Evaluate:

-   Revenue growth
-   Profit growth
-   EPS growth
-   Cash flow growth

Use multi-year data where available.

------------------------------------------------------------------------

## Valuation

Evaluate relative and historical valuation:

-   P/E
-   P/B
-   EV/EBITDA
-   FCF yield
-   Dividend yield
-   Industry-relative valuation

Absolute thresholds must not be blindly applied across all industries.

------------------------------------------------------------------------

## Market Conditions

Evaluate:

-   Long-term trend
-   Momentum
-   Relative strength
-   Volatility
-   Drawdown
-   Market regime

------------------------------------------------------------------------

## Risk

Detect:

-   Deteriorating earnings
-   Rising debt
-   Negative cash flow
-   Excessive valuation
-   Severe drawdown
-   Extreme volatility
-   Data staleness
-   Sector concentration

------------------------------------------------------------------------

# 11. Scoring Requirements

Scores must be:

``` text
0–100
```

Scores must:

-   Be deterministic.
-   Be explainable.
-   Handle missing data.
-   Avoid silently treating missing values as zero.

Initial conceptual weighting:

``` text
Business Quality: 40%
Growth: 20%
Valuation: 20%
Entry/Market Conditions: 10%
Risk: 10%
```

Weights must remain configurable and documented.

------------------------------------------------------------------------

# 12. Alert Requirements

Every alert must answer:

``` text
What?
Why?
When?
How long?
What risks?
When to review?
```

Example:

``` text
📊 INVESTMENT OPPORTUNITY

TCS

Recommendation: ACCUMULATE

Overall Score: 87/100
Business Score: 92/100
Entry Score: 81/100
Risk Score: 86/100
Confidence: HIGH

Investment Horizon: 3–5 YEARS
Review Period: QUARTERLY

Why:
✓ Strong profitability
✓ Stable earnings
✓ Positive long-term trend

Risks:
⚠ Valuation is not deeply discounted

Action Framework:
• Consider phased accumulation
• Reassess after quarterly results
• Do not blindly average down if the thesis deteriorates
```

------------------------------------------------------------------------

# 13. Multi-Telegram Requirements

The system must support:

``` text
Personal Chat
Investment Group
Public Channel
Admin/Debug Chat
```

Each destination may have:

``` text
enabled
message_profile
chat_id
```

Message profiles:

``` text
detailed
summary
admin
```

Delivery must be tracked independently.

------------------------------------------------------------------------

# 14. Database Requirements

The system should support data for:

``` text
stocks
price_history
financial_metrics
analysis_results
scores
investment_decisions
alerts
notification_deliveries
metadata
```

Schema changes must be versioned or migrated safely.

------------------------------------------------------------------------

# 15. Backtesting Requirements

The system must eventually evaluate:

``` text
CAGR
Maximum Drawdown
Sharpe Ratio
Sortino Ratio
Volatility
Worst Year
Recovery Time
Turnover
```

The backtesting system must avoid:

-   Look-ahead bias
-   Survivorship bias
-   Future financial data leakage

------------------------------------------------------------------------

# 16. Success Metrics

The product is successful when:

1.  Every alert is explainable.
2.  Every recommendation has a time horizon.
3.  Every recommendation has a review period.
4.  Risks are displayed.
5.  Data quality is visible.
6.  Multiple Telegram destinations work independently.
7.  The strategy can be backtested.
8.  New strategies can be added without modifying unrelated strategies.
9.  Existing Phase 1 functionality continues to work.

------------------------------------------------------------------------

# 17. Future Features

-   Portfolio tracking
-   Position sizing
-   Correlation analysis
-   Sector exposure
-   Backtesting UI
-   Web dashboard
-   REST API
-   Multiple market data providers
-   AI-generated research summaries
-   Custom user strategies
-   Paper trading
-   Broker integration after extensive validation
