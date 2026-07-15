# Trading Alert System

## Mission

Build a production-quality automated trading alert platform for Indian equities.

The system should be:

- Reliable
- Deterministic
- Modular
- Extensible
- Low maintenance
- Cost efficient
- Easy to run on GitHub Actions

The long-term vision is to evolve from a simple 52-week low screener into a multi-strategy market screening platform.

---

# Guiding Principles

## Architecture

Always prioritize

- Separation of concerns
- SOLID principles
- Composition over inheritance
- Small modules
- Reusable components

Avoid large monolithic files.

Every module should have one responsibility.

---

## Configuration

Human editable values belong inside

config/

Examples

- Telegram
- Scheduler
- Feature flags
- ATR multiplier
- Default thresholds

Generated data must NEVER overwrite configuration files.

---

## Generated Data

Market metadata belongs in

- SQLite
or

- data/

Never inside config/.

Examples

- ATR
- Sector
- Industry
- Market Cap
- Universe rankings

---

## Database

SQLite is the single source of truth.

Prefer SQLite over JSON.

Avoid duplicate storage.

Database should contain

- stock metadata
- volatility metrics
- cached history
- alert history
- strategy metadata

---

## Strategies

Strategies must be independent modules.

Current

- Near52WeekLow

Future

- NearATH
- Breakout
- RSI
- EMA Cross
- Gap Down
- High Volume
- Moving Average Reversal

Adding a strategy should require minimal changes.

Never hardcode strategy logic into main.py.

---

## GitHub Actions

Separate

Metadata generation

from

Screening.

Heavy calculations must never run every two hours.

---

## Performance

Minimize

- API requests
- history downloads
- repeated calculations

Always reuse cached data.

Only fetch incremental updates.

---

## Logging

Every workflow should produce structured logs.

Log

- start
- finish
- execution time
- failures
- skipped symbols

Never silently ignore exceptions.

---

## Error Handling

External APIs are unreliable.

Always

- retry
- continue processing remaining symbols
- log failures

One bad ticker should never stop the workflow.

---

## Alerting

Telegram alerts should be concise but informative.

Include

- symbol
- company
- sector
- strategy
- trigger reason
- threshold
- current price

Avoid duplicate alerts.

---

## Code Quality

Every new module must include

- type hints
- docstrings
- logging
- unit-testable functions

Prefer dataclasses.

Avoid global variables.

Avoid magic numbers.

---

## Documentation

Whenever architecture changes

Update

- README
- schema documentation
- workflow documentation

Documentation is part of the implementation.

---

## AI Implementation Rules

Before implementing any feature

1. Analyze existing architecture.
2. Identify affected modules.
3. Produce an implementation plan.
4. Wait for approval.
5. Implement incrementally.
6. Validate.
7. Update documentation.

Never rewrite the project without justification.

Always preserve backward compatibility unless instructed otherwise.

---

## Future Vision

The architecture should support

- Portfolio watchlists
- Multiple exchanges
- Backtesting
- AI ranking
- ML scoring
- Web dashboard
- REST API
- Mobile notifications
- Discord
- Email
- Slack