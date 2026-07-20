# ARCHITECTURE.md

# Trading Alert & Long-Term Investment Intelligence System

**Version:** 3.0\
**Status:** Production Architecture\
**Primary Goal:** Identify high-quality long-term investment
opportunities, explain the decision clearly, recommend an appropriate
action window, and communicate alerts reliably across multiple Telegram
destinations.

------------------------------------------------------------------------

# 1. Product Vision

The system is not designed to predict the future or guarantee returns.

It is a decision-support system that answers:

1.  **Is this a high-quality business?**
2.  **Is the current valuation reasonable?**
3.  **Is the current market trend supportive?**
4.  **What are the major risks?**
5.  **Is this a suitable time to consider buying?**
6.  **What is the expected investment horizon?**
7.  **Should the user buy now, accumulate gradually, wait, hold, or
    avoid?**

The system must always communicate uncertainty and must never represent
a score as a guaranteed probability of profit.

------------------------------------------------------------------------

# 2. Core Decision Model

``` text
Master Universe
      │
      ▼
Eligibility & Data Quality
      │
      ▼
Business Analysis
      │
      ├── Quality
      ├── Growth
      ├── Financial Health
      └── Business Stability
      │
      ▼
Valuation Analysis
      │
      ├── Relative Valuation
      ├── Historical Valuation
      └── Growth-Adjusted Valuation
      │
      ▼
Market Analysis
      │
      ├── Trend
      ├── Momentum
      ├── Volatility
      └── Market Regime
      │
      ▼
Risk & Red Flag Engine
      │
      ▼
Decision Engine
      │
      ├── Business Score
      ├── Entry Score
      ├── Risk Score
      ├── Confidence Level
      ├── Recommendation
      └── Investment Horizon
      │
      ▼
Portfolio Ranking
      │
      ▼
Alert + Explanation
      │
      ▼
Telegram Router
```

------------------------------------------------------------------------

# 3. Separation of Business Quality and Entry Timing

This is a mandatory architectural principle.

A stock can be:

``` text
Excellent Business
+
Bad Entry Price
```

or:

``` text
Average Business
+
Temporarily Attractive Price
```

These must not receive the same recommendation.

The system therefore calculates independently:

``` text
BusinessScore
EntryScore
RiskScore
ConfidenceScore
```

The final recommendation is derived from all four.

------------------------------------------------------------------------

# 4. Recommendation Model

The system must not only send:

``` text
BUY
```

Instead, it must provide an action state.

Supported recommendation states:

``` text
RESEARCH
WATCHLIST
WAIT
ACCUMULATE
BUY_SMALL
BUY
HOLD
REDUCE
AVOID
```

The exact state must be determined by configurable rules.

Example:

``` text
Business Score: 91
Entry Score: 64
Risk Score: 88
Valuation: Expensive

Recommendation:
WAIT / WATCHLIST
```

Another example:

``` text
Business Score: 87
Entry Score: 86
Risk Score: 84
Valuation: Fair

Recommendation:
ACCUMULATE
```

The system must distinguish between:

-   **Business quality**
-   **Current opportunity**
-   **Risk**
-   **Action**

------------------------------------------------------------------------

# 5. Investment Horizon

Every recommendation must include an estimated investment horizon.

Supported horizon categories:

``` text
SHORT_TERM
    Less than 3 months

MEDIUM_TERM
    3–12 months

LONG_TERM
    1–3 years

VERY_LONG_TERM
    3–7+ years
```

The system must never imply that a stock will definitely reach a target
within the horizon.

The horizon is a classification of the underlying thesis.

Example:

``` text
Investment Horizon: LONG_TERM
Suggested Review Period: 6 months
Thesis Validity: 3–5 years
```

The system should use separate concepts:

### Investment Horizon

How long the thesis is intended to play out.

### Review Period

When the user should reassess the thesis.

### Thesis Validity

How long the fundamental reasoning may remain relevant.

Example:

``` text
Action: ACCUMULATE
Investment Horizon: 3–5 years
Review Period: Quarterly
```

------------------------------------------------------------------------

# 6. Buy Timing Model

The system must clearly explain timing.

Recommended action categories:

## BUY_NOW

Conditions may include:

-   Strong business quality
-   Acceptable valuation
-   Positive or improving trend
-   No major red flags
-   Risk within acceptable limits

## ACCUMULATE

Conditions may include:

-   Strong business quality
-   Fair or attractive valuation
-   Acceptable long-term thesis
-   Entry timing is not perfect

The system may recommend phased accumulation rather than a single
full-size entry.

## WAIT

Conditions may include:

-   Strong business but excessive valuation
-   Weak market regime
-   Unfavorable technical setup
-   Temporary uncertainty

## WATCHLIST

Conditions may include:

-   Good business
-   Insufficient valuation margin
-   Incomplete data
-   Awaiting confirmation

## AVOID

Conditions may include:

-   Serious financial deterioration
-   Major red flags
-   Poor data quality
-   Extreme risk
-   Broken thesis

------------------------------------------------------------------------

# 7. Phased Entry Model

For long-term investing, the system should support staged entry.

Example:

``` text
Suggested Allocation

Initial Entry: 25%
Second Entry: 25%
Third Entry: 25%
Final Allocation: 25%
```

This should be presented as a configurable framework, not personalized
financial advice.

Possible triggers:

``` text
Entry 1:
High-quality opportunity identified

Entry 2:
Price reaches predefined valuation or technical zone

Entry 3:
Fundamental thesis remains valid after results

Entry 4:
Confirmation of trend or continued business execution
```

The system must never blindly average down.

A second or later entry must be conditional on the investment thesis
remaining valid.

------------------------------------------------------------------------

# 8. Scoring Architecture

## Business Score

Suggested components:

``` text
Quality              30%
Growth               20%
Financial Health     20%
Business Stability   15%
Competitive Strength 15%
```

## Entry Score

Suggested components:

``` text
Valuation            40%
Long-Term Trend      25%
Momentum             15%
Volatility           10%
Drawdown              10%
```

## Risk Score

Suggested components:

``` text
Balance Sheet Risk
Earnings Risk
Volatility
Drawdown
Sector Concentration
Data Quality
```

## Final Score

The final score must not hide the component scores.

Example:

``` text
Business Score: 91/100
Entry Score:     78/100
Risk Score:      86/100
Confidence:      HIGH

Overall Score:   86/100
```

------------------------------------------------------------------------

# 9. Confidence

Confidence is not the probability of profit.

Confidence represents:

``` text
Data Completeness
Signal Agreement
Historical Data Availability
Analysis Coverage
Model Consistency
```

Supported values:

``` text
HIGH
MEDIUM
LOW
INSUFFICIENT_DATA
```

Example:

``` text
Confidence: HIGH

Reason:
4 of 5 major factors are positive.
Financial data is complete.
No major red flags detected.
```

------------------------------------------------------------------------

# 10. Analysis Layers

``` text
src/analysis/

    quality/
        profitability.py
        balance_sheet.py
        cash_flow.py
        stability.py

    growth/
        revenue_growth.py
        earnings_growth.py
        cash_flow_growth.py

    valuation/
        relative_valuation.py
        historical_valuation.py
        growth_adjusted.py

    technical/
        trend.py
        momentum.py
        volatility.py
        drawdown.py

    risk/
        red_flags.py
        market_regime.py
        data_quality.py
```

Analysis modules calculate metrics only.

They must not:

-   Send Telegram messages
-   Write notifications
-   Make investment decisions
-   Execute raw SQL
-   Call unrelated APIs

------------------------------------------------------------------------

# 11. Decision Engine

``` text
src/decision/

    recommendation_engine.py
    horizon_engine.py
    entry_engine.py
    confidence_engine.py
```

The decision engine receives analysis results and produces:

``` text
InvestmentDecision
```

Example:

``` python
InvestmentDecision(
    recommendation="ACCUMULATE",
    investment_horizon="3-5 years",
    review_period="Quarterly",
    business_score=91,
    entry_score=82,
    risk_score=87,
    confidence="HIGH",
    reasons=[...],
    warnings=[...],
)
```

The decision engine must be deterministic and testable.

------------------------------------------------------------------------

# 12. Portfolio Layer

``` text
src/portfolio/

    ranker.py
    exposure.py
    correlation.py
    allocator.py
```

Portfolio ranking must consider:

-   Overall score
-   Sector concentration
-   Industry concentration
-   Correlation
-   Position limits
-   Market regime

Example constraints:

``` text
Maximum single-stock exposure: configurable
Maximum sector exposure: configurable
Minimum number of sectors: configurable
```

A high-scoring stock must not automatically be added if it creates
excessive concentration.

------------------------------------------------------------------------

# 13. Telegram Architecture

``` text
Alert
  │
  ▼
NotificationService
  │
  ▼
TelegramRouter
  │
  ├── Personal Chat
  ├── Investment Group
  ├── Alert Channel
  └── Admin/Debug Chat
```

Configuration:

``` yaml
notifications:
  telegram:
    enabled: true
    destinations:
      - name: personal
        chat_id: "..."
        enabled: true
        message_profile: detailed

      - name: investment_group
        chat_id: "..."
        enabled: true
        message_profile: summary
```

One destination failure must not prevent delivery to other destinations.

------------------------------------------------------------------------

# 14. Telegram Message Contract

Every investment alert should clearly display:

``` text
📊 INVESTMENT OPPORTUNITY

Company: TCS
Symbol: TCS.NS

Recommendation: ACCUMULATE

Business Score: 91/100
Entry Score: 82/100
Risk Score: 87/100
Confidence: HIGH

Investment Horizon: 3–5 YEARS
Review Period: QUARTERLY

Why:
✓ Strong business quality
✓ Positive earnings growth
✓ Reasonable valuation
✓ Healthy long-term trend

Risks:
⚠ Valuation is not deeply discounted

Action Framework:
• Consider phased accumulation
• Do not invest full allocation at once
• Re-evaluate thesis quarterly

This is research information, not a guaranteed return.
```

The message must answer:

1.  What is this?
2.  Why is it interesting?
3.  What should the user consider doing?
4.  How long is the thesis?
5.  When should the user review it?
6.  What are the risks?

------------------------------------------------------------------------

# 15. Data Flow

``` text
Master Universe
      ↓
Market & Financial Data
      ↓
Data Validation
      ↓
Analysis Modules
      ↓
Score Aggregation
      ↓
Red Flag Engine
      ↓
Decision Engine
      ↓
Portfolio Constraints
      ↓
InvestmentDecision
      ↓
Alert
      ↓
Telegram Router
      ↓
Delivery Tracking
```

------------------------------------------------------------------------

# 16. Backtesting Requirement

Before relying on a strategy, evaluate:

``` text
CAGR
Maximum Drawdown
Volatility
Sharpe Ratio
Sortino Ratio
Worst Calendar Year
Recovery Time
Turnover
Number of Signals
```

The system must avoid survivorship bias and look-ahead bias.

Fundamental data must only be used from the date it was publicly
available.

------------------------------------------------------------------------

# 17. Core Design Principle

The platform must not promise:

``` text
This stock will go up.
```

It should communicate:

``` text
This stock currently satisfies the system's defined quality, valuation, trend, and risk criteria.

The thesis is intended for a defined horizon and should be reviewed periodically.
```

------------------------------------------------------------------------

# 18. Long-Term Evolution

``` text
Market Data
    ↓
Analysis
    ↓
Scoring
    ↓
Decision
    ↓
Portfolio Construction
    ↓
Notifications
    ↓
Dashboard
    ↓
Backtesting
    ↓
Personalized Research
```

The architecture should remain modular enough to support:

-   Portfolio tracking
-   Backtesting
-   REST API
-   Web dashboard
-   Custom user strategies
-   Multiple data providers
-   AI-generated research summaries
-   Email, Discord, Slack, and Telegram
