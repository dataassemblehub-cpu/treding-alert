# ARCHITECTURE.md

# Trading Alert System Architecture

Version: 2.0

Status: Production Design

---

# Overview

The Trading Alert System is an automated market screening platform that continuously monitors Indian equities for predefined trading opportunities and sends notifications through Telegram.

The architecture is designed to be:

- Modular
- Event-driven
- Data-driven
- Extensible
- Low-cost
- GitHub Actions friendly

The long-term vision is to evolve into a professional multi-strategy market intelligence platform.

---

# High-Level Architecture

                    GitHub Actions
                         │
        ┌────────────────┴────────────────┐
        │                                 │
 Weekly Metadata Job              2-Hour Screening Job
        │                                 │
        ▼                                 ▼
 Metadata Generator                 Price Downloader
        │                                 │
        ▼                                 ▼
 ATR Calculator                 Strategy Engine
        │                                 │
        ▼                                 ▼
 SQLite Database             Alert Generator
        │                                 │
        └──────────────┬──────────────────┘
                       ▼
                 Telegram Bot

---

# Core Principles

The architecture follows five principles.

1. Configuration is static.

2. Market data is dynamic.

3. SQLite is the source of truth.

4. Strategies are independent.

5. Heavy computation happens only once per week.

---

# Directory Structure

project/

```
config/
    settings.yaml
    logging.yaml

data/
    master_universe.csv

database/
    trading.db

src/

    core/
        database.py
        cache.py
        logger.py

    generators/
        metadata_generator.py
        atr_generator.py

    screeners/
        screener.py

    strategies/
        base.py
        near_52w_low.py

    services/
        market_data.py
        telegram.py

    models/
        stock.py
        alert.py

    utils/

main.py

.github/
    workflows/

tests/

README.md
AGENT.md
SKILLS.md
ARCHITECTURE.md
```

---

# Layered Architecture

Presentation Layer

↓

Telegram Notifications

↓

Business Layer

↓

Strategy Engine

↓

Data Layer

↓

SQLite

↓

Infrastructure Layer

↓

GitHub Actions
yfinance
Telegram API

Each layer only communicates with adjacent layers.

---

# Configuration

Configuration contains only human-editable values.

Example

settings.yaml

```yaml
telegram:

bot_token:

chat_id:

screening:

atr_multiplier: 1.5

fallback_threshold: 2.0

features:

enable_volume_filter: true

enable_sector_filter: true
```

Generated values never belong here.

---

# Generated Data

Generated market data belongs in SQLite.

Examples

ATR

Sector

Industry

Market Cap

Average Volume

52 Week High

52 Week Low

Universe Ranking

---

# Database

SQLite is the primary datastore.

Database name

```
trading.db
```

---

## stocks

| Column | Description |
|----------|-------------|
| symbol | NSE ticker |
| company | Company name |
| sector | Sector |
| industry | Industry |
| market_cap | Current market cap |
| average_volume | 30-day average volume |
| updated_at | Metadata refresh timestamp |

---

## volatility

| Column | Description |
|----------|-------------|
| symbol | NSE ticker |
| atr | ATR(14) |
| threshold_pct | Dynamic threshold |
| updated_at | Last calculation |

---

## alerts

| Column | Description |
|----------|-------------|
| symbol | Alert stock |
| strategy | Strategy name |
| trigger_price | Price |
| alert_time | Timestamp |
| status | Sent/Skipped |

---

## metadata

Generic key-value table.

Example

```
last_metadata_refresh

last_atr_update

schema_version
```

---

# Weekly Metadata Workflow

Runs every Sunday.

Workflow

Load Master Universe

↓

Download Metadata

↓

Update Company Information

↓

Calculate ATR

↓

Update Dynamic Thresholds

↓

Store SQLite

↓

Commit Database

Heavy calculations never happen during market hours.

---

# Screening Workflow

Runs every two hours.

Workflow

Load SQLite

↓

Download Latest Prices

↓

Load Enabled Strategies

↓

Execute Strategies

↓

Generate Alerts

↓

Check Duplicate Alerts

↓

Send Telegram

↓

Store Alert History

The screening workflow must complete quickly.

---

# Strategy Engine

Strategies are plugins.

Each strategy implements the same interface.

```
Strategy

run()

↓

List[Alert]
```

Current strategy

Near52WeekLowStrategy

Future strategies

NearAllTimeHighStrategy

GapDownStrategy

BreakoutStrategy

GoldenCrossStrategy

EMACrossoverStrategy

RSIReversalStrategy

VolumeBreakoutStrategy

No strategy should modify another strategy.

---

# Data Flow

Master Universe

↓

Metadata Generator

↓

SQLite

↓

Strategy Engine

↓

Alerts

↓

Telegram

Data always flows in one direction.

---

# ATR Calculation

ATR Period

14

Formula

True Range

=

Maximum

High-Low

High-Previous Close

Low-Previous Close

ATR

=

Rolling Average(True Range)

Threshold

```
ATR %

×

Multiplier
```

Multiplier is configurable.

ATR is calculated only during metadata refresh.

---

# Universe Management

Master Universe

```
master_universe.csv
```

Contains

```
NSE Symbol

Company

Exchange
```

Metadata Generator enriches it.

No web scraping.

No generated YAML.

---

# Alert Lifecycle

Market Data

↓

Strategy Trigger

↓

Alert Created

↓

Duplicate Check

↓

Telegram Sent

↓

Alert Stored

↓

Next Execution

Duplicate alerts should never be sent within the configured cooldown period.

---

# Error Handling

The system must never terminate because one ticker fails.

Every external request should

Retry

↓

Timeout

↓

Log Failure

↓

Continue

Errors should be isolated.

---

# Logging

Every module should log

Start

Finish

Execution Time

Symbols Processed

Alerts Generated

Database Updates

Errors

Structured logging is preferred.

---

# Performance Goals

Screening job

Target

< 2 minutes

Metadata update

Target

< 15 minutes

Avoid repeated downloads.

Prefer SQLite lookups over API requests.

---

# GitHub Actions

Workflow 1

update_metadata.yml

Weekly

Responsibilities

Update metadata

Calculate ATR

Commit SQLite

Workflow 2

screen_market.yml

Every two hours

Responsibilities

Download latest prices

Run strategies

Send Telegram

Store alerts

The two workflows should never duplicate work.

---

# Extensibility

Future modules should require minimal changes.

Examples

Portfolio Tracking

Risk Analysis

Backtesting

REST API

Web Dashboard

Machine Learning Ranking

Sector Rotation

Email Notifications

Discord Notifications

Slack Notifications

---

# Future Architecture

                     Dashboard
                          │
                          ▼
                      REST API
                          │
                          ▼
                  Strategy Engine
          ┌──────────┬──────────┬──────────┐
          │          │          │          │
      52W Low     Breakout     RSI      EMA Cross
          │          │          │          │
          └──────────┴──────────┴──────────┘
                          │
                     SQLite Database
                          │
               Metadata Generator Jobs
                          │
                     GitHub Actions

---

# Design Goals

The project should remain

Simple enough for a solo developer.

Scalable enough to support dozens of strategies.

Reliable enough to run unattended.

Modular enough that AI coding agents can safely implement new features without refactoring unrelated components.

Every new feature should integrate into the existing architecture rather than introducing parallel systems.
