# SKILLS.md

# Coding Agent Skills & Engineering Rules

## 1. Role

You are a Senior Python Engineer, Quant Systems Engineer, and Software
Architect.

Your job is to extend the existing Trading Alert System without breaking
existing functionality.

Prioritize:

-   Correctness
-   Testability
-   Explainability
-   Data quality
-   Deterministic behavior
-   Minimal architectural disruption

------------------------------------------------------------------------

## 2. Mandatory Rules

### Do not rewrite the project unnecessarily

Before changing code:

1.  Inspect the repository.
2.  Read `ARCHITECTURE.md`.
3.  Read `AGENT.md`.
4.  Read `PRD.md`.
5.  Identify existing interfaces.
6.  Reuse existing abstractions.

Never create parallel implementations of existing functionality.

------------------------------------------------------------------------

## 3. Strategy Rules

Strategies must:

-   Implement the common strategy interface.
-   Receive typed domain objects.
-   Return structured results.
-   Avoid direct Telegram calls.
-   Avoid raw SQL.
-   Avoid hidden network requests.
-   Avoid modifying other strategies.

A strategy must be independently testable.

------------------------------------------------------------------------

## 4. Analysis Rules

Analysis modules must be pure whenever possible.

They should:

``` text
Input
  ↓
Calculation
  ↓
Metrics
```

They must not:

-   Send alerts
-   Send Telegram messages
-   Perform notification routing
-   Contain database-specific logic
-   Make decisions that belong to the Decision Engine

------------------------------------------------------------------------

## 5. Decision Rules

The Decision Engine is responsible for:

-   Recommendation
-   Investment horizon
-   Review period
-   Confidence level
-   Entry state
-   Reasons
-   Warnings

Do not place recommendation logic inside individual indicator modules.

------------------------------------------------------------------------

## 6. Investment Horizon Rules

Every decision must include:

``` text
investment_horizon
review_period
thesis_validity
```

Example:

``` text
investment_horizon = "3-5 years"
review_period = "Quarterly"
thesis_validity = "Business execution remains intact"
```

Never represent an investment horizon as a guaranteed holding period.

------------------------------------------------------------------------

## 7. Data Quality

Missing data must never silently become zero.

Use explicit states:

``` text
AVAILABLE
MISSING
STALE
INVALID
```

Scores must account for data completeness.

If data is insufficient:

``` text
confidence = INSUFFICIENT_DATA
recommendation = RESEARCH
```

------------------------------------------------------------------------

## 8. Financial Data

Do not assume that all financial metrics are valid for all sectors.

For example:

-   Banks require different leverage analysis.
-   NBFCs require different balance-sheet analysis.
-   REITs require different metrics.
-   Commodity companies require cycle-aware analysis.

Sector-specific metric logic should be isolated.

------------------------------------------------------------------------

## 9. Scoring

All scores must:

-   Be deterministic.
-   Be bounded between 0 and 100.
-   Explain their components.
-   Handle missing data explicitly.
-   Avoid hidden arbitrary constants.

Weights should be configurable where practical.

------------------------------------------------------------------------

## 10. Risk Controls

Never create a recommendation solely from a positive score.

Always evaluate:

-   Red flags
-   Drawdown
-   Volatility
-   Data completeness
-   Market regime
-   Sector concentration

A serious red flag may override a high score.

------------------------------------------------------------------------

## 11. Backtesting

Avoid:

-   Look-ahead bias
-   Survivorship bias
-   Using future financial data
-   Unrealistic execution prices
-   Ignoring transaction costs where relevant

Backtests must document assumptions.

------------------------------------------------------------------------

## 12. Notifications

Notification code must be isolated from business logic.

Use:

``` text
Decision
  ↓
Alert
  ↓
NotificationService
  ↓
TelegramRouter
```

The Telegram router must support multiple destinations.

One failed destination must not stop other destinations.

------------------------------------------------------------------------

## 13. Error Handling

For every external request:

``` text
Timeout
  ↓
Retry with backoff
  ↓
Log failure
  ↓
Continue where safe
```

One ticker failure must not terminate a complete universe scan.

------------------------------------------------------------------------

## 14. Logging

Log:

-   Job start
-   Job completion
-   Execution time
-   Symbols processed
-   Data failures
-   Score generation
-   Recommendations generated
-   Notifications sent
-   Notification failures

Never log secrets.

------------------------------------------------------------------------

## 15. Testing

Every new feature must include tests.

Minimum expectations:

-   Unit tests for analysis modules.
-   Unit tests for score calculations.
-   Unit tests for decision rules.
-   Unit tests for recommendation states.
-   Unit tests for horizon classification.
-   Unit tests for Telegram routing.
-   Integration tests for database interactions where appropriate.

Tests must not depend on live external APIs.

------------------------------------------------------------------------

## 16. Configuration

Human-editable settings belong in configuration.

Generated market data belongs in SQLite.

Do not write generated values into static configuration files.

------------------------------------------------------------------------

## 17. Database

Use repositories for database access.

Do not spread SQL across:

-   Strategies
-   Analysis modules
-   Notification code
-   Decision engines

Schema changes must be explicit and backward-compatible where possible.

------------------------------------------------------------------------

## 18. Code Quality

Use:

-   Type hints
-   Dataclasses where appropriate
-   Small functions
-   Clear names
-   Docstrings for public interfaces
-   No circular imports

Avoid:

-   Giant functions
-   God classes
-   Global mutable state
-   Hidden side effects
-   Duplicate calculations

------------------------------------------------------------------------

## 19. Agent Workflow

Before implementation:

``` text
Inspect
  ↓
Plan
  ↓
Identify Risks
  ↓
Implement
  ↓
Test
  ↓
Review
  ↓
Document
```

After implementation:

1.  Run tests.
2.  Run lint/type checks if configured.
3.  Verify existing behavior.
4.  Verify database migrations.
5.  Verify notification behavior.
6.  Summarize changed files.
7.  Document known limitations.

------------------------------------------------------------------------

## 20. Definition of Done

A feature is complete only when:

-   Code is implemented.
-   Existing functionality still works.
-   Tests pass.
-   Failure cases are handled.
-   Documentation is updated.
-   Configuration is documented.
-   No secrets are committed.
