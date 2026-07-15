# PROMPT.md — Implementation Prompt

Copy the prompt below into Claude Code (or any coding agent) inside this repo folder to
build the full system. It references `AGENT.md` and `SKILL.md`, which the agent should
read first.

---

## Prompt to use

```
Read AGENT.md and SKILL.md in this repo before doing anything else — they define the
architecture, screening logic, and guardrails you must follow exactly.

Build the Trading Alert System described in AGENT.md, in this order:

1. config/settings.yaml
   - threshold_pct: 0.02
   - min_volume_ratio: 0.5
   - run frequency notes (for my reference, not used by code directly)

2. config/universe.yaml
   - Start with ONE category "IT" and 5 well-known NSE-listed IT stocks
     (e.g. TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS, TECHM.NS)
   - Leave commented-out example sections for Finance, Gold, Sports categories so I can
     uncomment/expand later

3. src/fetcher.py
   - Use yfinance
   - Function get_price_data(symbol) -> latest price + volume
   - Function backfill_history(symbol, db_path) -> stores max available daily history
     into SQLite (data/price_history.db) if not already present
   - Function update_history(symbol, db_path) -> appends only new daily data since the
     last stored date (don't redownload everything each run)
   - Handle failures per-symbol with try/except + logging, never crash the whole run

4. src/screener.py
   - Implement exactly the screen_symbol() logic from SKILL.md
   - Read thresholds from config/settings.yaml
   - Include the volume filter and trend label as specified
   - Include the "N-day low" fallback label if less than 252 days of history exist

5. src/notifier.py
   - Telegram send function using bot token + chat ID from environment variables
     (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
   - Format grouped-by-category message exactly as shown in SKILL.md
   - Read/write data/alert_log.db to avoid duplicate same-day alerts per symbol+signal

6. src/main.py
   - Orchestrate: for each symbol in universe.yaml -> update_history -> screen_symbol
     -> collect matches -> group by category -> send one Telegram message if there are
     any matches (skip sending if zero matches, but log "no matches" to console)
   - Should run cleanly via: python src/main.py

7. .github/workflows/run_screener.yml
   - Cron schedule for every 2 hours during NSE market hours (9:15 AM–3:30 PM IST),
     Monday–Friday. Remember cron is UTC — convert correctly and comment the UTC times.
   - Checkout repo, set up Python, install requirements.txt, run python src/main.py
   - Use secrets.TELEGRAM_BOT_TOKEN and secrets.TELEGRAM_CHAT_ID as env vars
   - Cache the data/ folder between runs (GitHub Actions cache or commit the SQLite file
     back to the repo after each run — pick the simpler approach and explain your choice)

8. requirements.txt with pinned versions of yfinance, pyyaml, requests (or
   python-telegram-bot), and any others used

9. README.md
   - How to get a Telegram bot token (via @BotFather) and chat ID
   - How to add repo secrets in GitHub
   - How to run locally for testing before relying on the automated schedule
   - How to add a new category or stock to universe.yaml
   - How to adjust the alert threshold

Write clean, commented code. Do not add order-execution logic. Do not hardcode secrets
anywhere. After building, show me the final file tree and a summary of what each file
does.
```

---

## Notes for you (the user) before running this

1. **Get a Telegram bot token first** — message `@BotFather` on Telegram, run `/newbot`,
   follow the prompts, you'll get a token like `123456:ABC-DEF...`.
2. **Get your chat ID** — message your new bot once, then visit
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser to find your
   `chat.id`.
3. **Add both as GitHub Actions secrets**: repo → Settings → Secrets and variables →
   Actions → New repository secret → `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. **Test locally first** with a `.env` file (add `.env` to `.gitignore`!) before turning
   on the GitHub Actions schedule — this avoids burning Actions minutes on a broken script.
5. **Start with the IT category only** (as the prompt specifies) — confirm you get a
   correct, sensible alert before expanding to Finance, Gold, and other sectors. Adding a
   category later is just editing `universe.yaml`, no code changes needed.
6. **Sanity-check the first few alerts manually** against a site like NSE India or Google
   Finance before trusting the automation — yfinance data can occasionally lag or glitch.

## Easy-to-start checklist

- [ ] Create the Telegram bot, save token + chat ID somewhere safe
- [ ] Clone this repo / unzip this folder, `cd` into it
- [ ] Run the prompt above in Claude Code inside this folder
- [ ] `pip install -r requirements.txt`
- [ ] Create a local `.env` with your Telegram token/chat ID for testing
- [ ] Run `python src/main.py` locally, confirm you get a Telegram message (even a
      "no matches" console log is a good sign the pipeline works)
- [ ] Add secrets to GitHub, push the repo, confirm the Action runs on schedule
- [ ] Expand `universe.yaml` one category at a time
