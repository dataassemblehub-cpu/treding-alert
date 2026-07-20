# CODING AGENT IMPLEMENTATION PROMPT

You are a Senior Python Engineer, Quant Systems Architect, and
Production Software Engineer.

You are working on an existing Trading Alert System for Indian equities.

Before writing code, read:

1.  `ARCHITECTURE.md`
2.  `SKILLS.md`
3.  `AGENT.md`
4.  `PRD.md`

Then inspect the entire repository and understand the existing Phase
1/Phase 2 implementation.

------------------------------------------------------------------------

## PRIMARY OBJECTIVE

Upgrade the existing stock alert system into an explainable long-term
investment intelligence system.

The system must answer:

1.  Is this a good business?
2.  Is the valuation reasonable?
3.  Is the current entry condition acceptable?
4.  What are the risks?
5.  What should the user do: research, watch, wait, accumulate, buy
    small, buy, hold, reduce, or avoid?
6.  What is the intended investment horizon?
7.  When should the user review the thesis?

Do not promise returns.

Do not describe confidence as a probability of profit.

Do not automatically turn a high score into a guaranteed BUY.

------------------------------------------------------------------------

# IMPORTANT IMPLEMENTATION RULES

## 1. Preserve Existing Architecture

Do not rewrite the project unnecessarily.

Reuse existing:

-   Database layer
-   Market data layer
-   Strategy interface
-   Alert model
-   Telegram service
-   GitHub Actions
-   Existing 52-week-low strategy

Make focused changes.

------------------------------------------------------------------------

## 2. Implement the New Analysis Layers

Create modular analysis components for:

``` text
Quality
Growth
Valuation
Trend
Momentum
Volatility
Drawdown
Risk Flags
Data Quality
Market Regime
```

Each analysis module should:

-   Be independently testable.
-   Avoid Telegram.
-   Avoid direct database access.
-   Avoid making final recommendations.
-   Return typed metrics or analysis results.

------------------------------------------------------------------------

## 3. Add Score Models

Create typed domain models for:

``` text
QualityScore
GrowthScore
ValuationScore
EntryScore
RiskScore
ConfidenceScore
InvestmentScore
```

All scores must:

-   Be between 0 and 100.
-   Be deterministic.
-   Be explainable.
-   Handle missing data explicitly.

Do not silently convert missing values to zero.

------------------------------------------------------------------------

## 4. Add the Decision Engine

Create a deterministic Decision Engine.

It must combine analysis results and produce:

``` text
InvestmentDecision
```

The decision must include:

``` text
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

Supported recommendations:

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

The decision logic must be documented and covered by unit tests.

------------------------------------------------------------------------

## 5. Investment Horizon

Every investment decision must include:

``` text
investment_horizon
review_period
thesis_validity
```

Examples:

``` text
Investment Horizon: 3–5 years
Review Period: Quarterly
Thesis Validity: Business execution and financial quality remain intact
```

The system must clearly distinguish:

-   Investment horizon
-   Review period
-   Thesis validity

Never present the horizon as a guaranteed holding period.

------------------------------------------------------------------------

## 6. Add Red Flag Overrides

Create a Red Flag Engine.

Potential flags:

``` text
Deteriorating earnings
Rapid debt increase
Negative cash flow
Extreme valuation
Severe drawdown
Extreme volatility
Stale data
Missing critical financial data
```

A serious red flag may prevent a stock from receiving a strong
recommendation even if its raw score is high.

This behavior must be explicit and tested.

------------------------------------------------------------------------

## 7. Add Multi-Factor Scoring

Implement an initial configurable scoring framework.

Suggested starting weights:

``` text
Business Quality: 40%
Growth: 20%
Valuation: 20%
Entry/Market Conditions: 10%
Risk: 10%
```

Do not hardcode weights in multiple places.

Store them in one configuration location.

------------------------------------------------------------------------

## 8. Add Portfolio Ranking

Create a portfolio ranking layer that:

-   Ranks candidates by score.
-   Applies sector concentration checks.
-   Applies position limits where configured.
-   Does not blindly select the top N stocks if they are all from one
    sector.

The ranking layer should be independent from individual stock
strategies.

------------------------------------------------------------------------

## 9. Upgrade Telegram Notifications

Implement a `TelegramRouter`.

It must support multiple destinations:

``` text
Personal Chat
Investment Group
Public Channel
Admin/Debug Chat
```

Configuration should support:

``` yaml
notifications:
  telegram:
    enabled: true
    destinations:
      - name: personal
        chat_id: "..."
        enabled: true
        message_profile: detailed

      - name: group
        chat_id: "..."
        enabled: true
        message_profile: summary
```

One failed destination must not prevent delivery to other destinations.

Add retry and failure logging.

Do not log bot tokens or secrets.

------------------------------------------------------------------------

## 10. Improve Alert Content

The Telegram message must clearly display:

``` text
Company
Symbol
Recommendation
Overall Score
Business Score
Entry Score
Risk Score
Confidence
Investment Horizon
Review Period
Reasons
Warnings
Action Framework
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

Keep message length appropriate for Telegram.

Different message profiles may be used for different destinations.

------------------------------------------------------------------------

## 11. Database Changes

Inspect the existing schema first.

Do not destroy existing data.

Add only necessary tables/columns.

Potential entities:

``` text
financial_metrics
analysis_results
scores
investment_decisions
notification_deliveries
```

Use migrations or safe schema initialization.

Keep SQLite as the source of truth.

------------------------------------------------------------------------

## 12. Testing

Add tests for:

### Analysis

-   Valid data
-   Missing data
-   Invalid data
-   Sector-specific behavior where applicable

### Scoring

-   Boundary values
-   Missing metrics
-   Weight calculations
-   Score bounds

### Decision Engine

-   Strong business + attractive entry
-   Strong business + expensive valuation
-   Weak business + cheap valuation
-   Serious red flag override
-   Insufficient data
-   Horizon classification
-   Review period generation

### Telegram

-   Multiple destinations
-   One destination failure
-   Retry behavior
-   Duplicate alert handling

No tests should depend on live external APIs.

------------------------------------------------------------------------

## 13. Backtesting Preparation

Do not implement a full backtesting engine unless the repository already
supports it.

However, design the analysis and decision models so that historical data
can be passed into them later.

Avoid:

-   Look-ahead bias
-   Future financial data leakage
-   Survivorship bias

Document assumptions.

------------------------------------------------------------------------

## 14. Execution Plan

Work in this order:

### Step 1

Inspect the repository and current architecture.

### Step 2

Create an implementation plan based on the actual codebase.

### Step 3

Identify compatibility risks.

### Step 4

Implement domain models.

### Step 5

Implement analysis modules.

### Step 6

Implement scoring.

### Step 7

Implement Decision Engine.

### Step 8

Implement Portfolio Ranking.

### Step 9

Implement TelegramRouter.

### Step 10

Update workflows/configuration.

### Step 11

Add tests.

### Step 12

Run tests and validation.

### Step 13

Update documentation.

------------------------------------------------------------------------

## 15. Definition of Done

The implementation is complete only when:

-   Existing 52-week-low alerts still work.
-   New analysis modules are modular.
-   Scores are explainable.
-   Recommendations are deterministic.
-   Investment horizon is shown.
-   Review period is shown.
-   Risks are shown.
-   Missing data is handled safely.
-   Multiple Telegram chats are supported.
-   One Telegram destination failure does not stop others.
-   Tests pass.
-   Database changes are safe.
-   Documentation is updated.

At the end, report:

``` text
1. Summary
2. Architecture changes
3. Files created
4. Files modified
5. Database changes
6. Configuration changes
7. Tests executed
8. Known limitations
9. Recommended next steps
```

Do not claim that a strategy is profitable or guarantees positive
returns.

The objective is to build a robust, transparent, explainable investment
research system.
