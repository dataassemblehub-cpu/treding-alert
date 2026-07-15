# Trading Alert System

An automated stock screener that checks for stocks near their 52-week or all-time lows and sends alerts via Telegram. Runs on GitHub Actions.

## Setup Instructions

### 1. Telegram Bot Setup
1. Message **@BotFather** on Telegram and send the `/newbot` command.
2. Follow the prompts to create your bot.
3. Save the **Bot Token** provided (it looks like `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`).
4. Message your new bot at least once (e.g., say "hello").
5. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a web browser. Find the `"chat":{"id":...}` part and copy the numeric ID. This is your **Chat ID**.

### 2. GitHub Actions Setup
1. Go to your GitHub repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. Add a secret named `TELEGRAM_BOT_TOKEN` and paste your bot token.
4. Add another secret named `TELEGRAM_CHAT_ID` and paste your chat ID.

### 3. Local Testing
Before enabling the schedule, test the script locally to ensure everything works and you don't burn GitHub Actions minutes on a broken run.
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file in the root of the project with your secrets:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```
3. Run the screener: `python src/main.py`
4. Ensure you receive a message in Telegram if any stocks match the criteria.

### 4. Configuration
- **Add stocks/categories**: Edit `config/universe.yaml`. No code changes are needed to add a new category. Make sure Indian stocks have the `.NS` (NSE) or `.BO` (BSE) suffix.
- **Adjust thresholds**: Edit `config/settings.yaml` to change the `threshold_pct` (default 2% / 0.02) or `min_volume_ratio` (default 0.5).

## Infrastructure Notes
- The screener uses GitHub Actions to run every 2 hours during market hours.
- Price history data is cached across runs using GitHub Actions Cache to avoid downloading the entire history every time.
- A backup workflow runs weekly to commit the SQLite database to the repository, ensuring the cache is never permanently lost.
- Alert logs are committed back to the repository after every successful run to prevent duplicate alerts.
