import logging
import requests
import yaml
import os
from typing import List
from src.models import Alert
from src.repositories.market_repo import MarketRepository

class NotificationService:
    def __init__(self, repo: MarketRepository):
        self.repo = repo
        self._load_settings()

    def _load_settings(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.yaml')
        try:
            with open(settings_path, 'r') as f:
                self.settings = yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.settings = {}

    def format_alert(self, alert: Alert) -> str:
        lines = [
            f"🟢 <b>{alert.symbol}</b> ({alert.strategy_name})",
            f"Sector: {alert.sector} | Ind: {alert.industry}",
            f"Current: ₹{alert.current_price:.2f}",
            f"Ref Price: ₹{alert.reference_price:.2f} ({alert.distance_pct:+.2f}%)",
            f"Threshold: {alert.threshold_used * 100:.2f}%",
            f"Trend: {alert.trend}"
        ]
        return "\n".join(lines)

    def send_alerts(self, alerts: List[Alert]) -> bool:
        if not alerts:
            msg = "📉 <b>Trading Alert</b>\n\nNo matches found in this run."
            return self._send_to_telegram(msg)

        # Filter out alerts that have already been sent today
        new_alerts = [a for a in alerts if not self.repo.has_alert_today(a.symbol, a.strategy_name)]
        
        if not new_alerts:
            logging.info("All generated alerts have already been sent today. Skipping.")
            return True

        blocks = ["📉 <b>Trading Alert</b>\n"]
        for alert in new_alerts:
            blocks.append(self.format_alert(alert))
            blocks.append("")
            
        final_msg = "\n".join(blocks).strip()
        success = self._send_to_telegram(final_msg)
        
        if success:
            for alert in new_alerts:
                self.repo.log_alert(alert)
                
        return success

    def _send_to_telegram(self, message: str) -> bool:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logging.warning("Telegram credentials not found in env vars. Printing to console instead:")
            print(message)
            return True # Pretend success for local testing
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logging.info("Telegram message sent successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to send telegram message: {e}")
            return False
