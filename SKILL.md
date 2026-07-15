# Trading Alert System Knowledge Base

This file defines engineering standards and domain knowledge the AI agent should follow.

---

# Project Stack

Python 3.12+

SQLite

GitHub Actions

yfinance

Telegram Bot API

PyYAML

Pandas

NumPy

---

# Architecture

Preferred flow

Weekly Workflow

↓

Update market metadata

↓

Compute ATR

↓

Store SQLite

↓

Commit database

Daily Workflow

↓

Load SQLite

↓

Fetch latest prices

↓

Run strategies

↓

Generate alerts

↓

Send Telegram

---

# SQLite

Preferred tables

stocks

symbol

company

sector

industry

market_cap

average_volume

updated_at

---

volatility

symbol

atr

threshold_pct

atr_period

updated_at

---

history_cache

symbol

last_date

rows_cached

---

alerts

symbol

strategy

trigger_price

alert_time

status

---

metadata

key

value

---

# ATR

Use ATR(14)

Formula

True Range

=

max

High-Low

High-Previous Close

Low-Previous Close

ATR

=

Rolling Mean(True Range)

Threshold

=

ATR %

×

Multiplier

Never calculate ATR during screening.

ATR should only be updated during metadata refresh.

---

# Universe

Maintain one master universe.

Never scrape NSE.

Prefer

NIFTY500

or

Top Indian Equities

Metadata generator enriches symbols.

---

# Screening

Current strategy

Near52WeekLow

Trigger

distance_to_low

<=

dynamic threshold

Future strategies should implement

run()

return Alert[]

---

# Strategy Interface

Example

class Strategy

run()

name

description

enabled

Every strategy should be independent.

---

# Telegram

Preferred message

🚨 Near 52 Week Low

Stock

Current Price

52W Low

Distance

ATR Threshold

Sector

Industry

Volume Ratio

Time

---

# GitHub Actions

Heavy jobs

Weekly

Metadata

ATR

Universe

Light jobs

Every 2 hours

Screen

Alert

Logging

---

# Error Handling

Retry API calls.

Timeout external requests.

Continue processing remaining stocks.

Never fail entire workflow because of one symbol.

---

# Performance

Prefer

SQLite lookup

over

API requests.

Reuse cached history.

Avoid downloading multiple years repeatedly.

Batch requests whenever possible.

---

# Logging

Every module should log

Execution time

Symbols processed

Alerts generated

API failures

Database updates

---

# Testing

Every feature should be testable.

Prefer dependency injection.

Avoid hardcoded dependencies.

Mock external APIs.

---

# Coding Style

PEP8

Type hints

Dataclasses

Small functions

Single responsibility

No duplicated logic

No hidden side effects

Prefer explicit over implicit.

---

# Long-Term Roadmap

Phase 1

Static screener

Completed

Phase 2

Dynamic universe

ATR

SQLite metadata

Phase 3

Strategy engine

Ranking

Watchlists

Phase 4

Dashboard

Analytics

Backtesting

Phase 5

AI ranking

ML models

REST API

Portfolio optimization
