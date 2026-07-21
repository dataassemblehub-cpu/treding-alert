# AGENT.md

# Trading Alert System - Coding Agent Contract

## Mission

You are working on a production-oriented Indian equity market
intelligence and long-term investment research system.

The system is designed to:

-   Analyze companies.
-   Evaluate quality.
-   Evaluate growth.
-   Evaluate valuation.
-   Evaluate market conditions.
-   Evaluate risk.
-   Rank opportunities.
-   Explain recommendations.
-   Communicate investment horizons and review periods.
-   Deliver notifications through multiple Telegram destinations.

The system is not a guaranteed-return engine.

Never describe a score as a probability of profit.

------------------------------------------------------------------------

# 1. Before You Code

Read these files first:

``` text
ARCHITECTURE.md
SKILLS.md
PRD.md
```

Then inspect:

``` text
src/
config/
database/
tests/
.github/
```

Understand the current implementation before making changes.

------------------------------------------------------------------------

# 2. Non-Negotiable Architecture

The following boundaries must be preserved:

``` text
Data Providers
      ↓
Repositories
      ↓
Analysis
      ↓
Scoring
      ↓
Decision Engine
      ↓
Portfolio Layer
      ↓
Alert Model
      ↓
Notification Service
      ↓
Telegram Router
```

Do not bypass layers.

------------------------------------------------------------------------

# 3. Decision Philosophy

The system must distinguish:

``` text
Good Business
```

from:

``` text
Good Investment Opportunity Right Now
```

Therefore the system must calculate independently:

``` text
Business Score
Entry Score
Risk Score
Confidence
```

Then produce:

``` text
Recommendation
Investment Horizon
Review Period
Thesis Validity
Reasons
Warnings
```

------------------------------------------------------------------------

# 4. Recommendation Safety

Never automatically convert:

``` text
High Score
```

into:

``` text
Guaranteed BUY
```

Recommendations must be explainable.

Possible outcomes:

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

The final decision must be deterministic based on documented rules.

------------------------------------------------------------------------

# 5. Investment Duration

Every recommendation must clearly communicate:

``` text
Investment Horizon
```

Examples:

``` text
3-6 months
6-12 months
1-3 years
3-5 years
5+ years
```

Also communicate:

``` text
Review Period
```

Examples:

``` text
Monthly
Quarterly
After Earnings
Semi-annually
```

The horizon is not a guarantee.

------------------------------------------------------------------------

# 6. Telegram Requirements

Telegram must support multiple destinations.

Example:

``` text
Personal Chat
Investment Group
Public Channel
Admin Chat
```

Use a router.

Do not put multiple chat IDs directly inside strategy code.

A failure in one destination must not prevent delivery to other
destinations.

------------------------------------------------------------------------

# 7. Data Integrity

Never silently:

``` text
missing value → 0
failed API call → valid metric
stale data → current data
```

Track data quality explicitly.

------------------------------------------------------------------------

# 8. Change Discipline

Prefer small, focused changes.

Do not:

-   Rewrite unrelated modules.
-   Rename files without a reason.
-   Change database schema casually.
-   Remove working strategies.
-   Introduce duplicate abstractions.

If a change requires architectural deviation, explain it before
implementation.

------------------------------------------------------------------------

# 9. Testing

Before declaring completion:

``` text
Run unit tests
Run integration tests
Test empty data
Test missing data
Test failed API responses
Test Telegram failure isolation
Test duplicate alert handling
```

------------------------------------------------------------------------

# 10. Final Response Requirements

After implementation, report:

``` text
1. Summary
2. Files changed
3. Database changes
4. Configuration changes
5. Tests executed
6. Known limitations
7. Recommended next steps
```

Do not claim success if tests were not actually executed.

------------------------------------------------------------------------

# 11. Priority Order

When tradeoffs exist, prioritize:

1.  Correctness
2.  Capital-risk awareness
3.  Data integrity
4.  Explainability
5.  Testability
6.  Maintainability
7.  Performance
8.  Feature breadth
