import logging
import requests
import yaml
import os
from typing import List
from dotenv import load_dotenv
from src.models.decision import InvestmentDecision

class TelegramRouter:
    def __init__(self, db_path=None):
        self._load_settings()
        load_dotenv()
        
    def _load_settings(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'telegram.yaml')
        try:
            with open(settings_path, 'r') as f:
                self.config = yaml.safe_load(f).get('notifications', {}).get('telegram', {})
        except FileNotFoundError:
            self.config = {'enabled': True, 'destinations': [{'name': 'personal', 'enabled': True, 'message_profile': 'detailed'}]}

    def format_decision(self, decision: InvestmentDecision) -> str:
        icon = {
            "BUY": "🟢🟢",
            "ACCUMULATE": "🟢",
            "WATCHLIST": "🟡",
            "WAIT": "⚪",
            "RESEARCH": "🟠",
            "AVOID": "🔴"
        }.get(decision.recommendation, "⚪")
        
        name_display = f" - {decision.company_name}" if decision.company_name else ""
        lines = [
            f"{icon} <b>{decision.symbol}{name_display}</b>",
            f"Recommendation: <b>{decision.recommendation}</b>",
            f"Score: {decision.investment_score}/100",
            f"Business Score: {decision.scores.get('quality', 0):.0f}/100",
            f"Entry Score: {decision.scores.get('entry', 0):.0f}/100",
            f"Risk Score: {decision.scores.get('risk', 0):.0f}/100",
            f"Confidence: {decision.confidence}\n",
            f"Investment Horizon: {decision.investment_horizon}",
            f"Review Period: {decision.review_period}\n",
        ]
        
        if decision.transition_alert:
            alert_icon = "🟢" if "UPGRADE" in decision.transition_alert else "🔴"
            lines.append(f"{alert_icon} <b>Decision {decision.transition_alert}</b>\n")
            
        lines.append(f"<b>Why:</b>")
        for t in decision.thesis:
            lines.append(f"✓ {t}")
            
        if decision.warnings:
            lines.append(f"\n<b>Warnings:</b>")
            for w in decision.warnings:
                lines.append(f"⚠ {w}")
                
        if decision.red_flags:
            lines.append(f"\n<b>Red Flags:</b>")
            for r in decision.red_flags:
                lines.append(f"❌ {r}")
                
        return "\n".join(lines)

    def route_decisions(self, decisions: List[InvestmentDecision]) -> bool:
        if not self.config.get('enabled', False):
            return False
            
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logging.warning("TELEGRAM_BOT_TOKEN not found. Notifications skipped.")
            return False
            
        destinations = self.config.get('destinations', [])
        success_count = 0
        
        for dest in destinations:
            if not dest.get('enabled', False):
                continue
                
            chat_id_env = f"TELEGRAM_CHAT_ID_{dest['name'].upper()}"
            chat_id = os.environ.get(chat_id_env)
            
            if not chat_id:
                logging.warning(f"Missing {chat_id_env} in .env file. Skipping {dest['name']} route.")
                continue
                
            allow_all = dest.get('detailed_research_alerts', False)
            blocks = []
            
            for decision in decisions:
                if not allow_all and decision.recommendation in ["WAIT", "AVOID", "WATCHLIST", "RESEARCH"]:
                    continue
                    
                blocks.append(self.format_decision(decision))
                blocks.append("\n───────────────\n")
            
            if not blocks:
                continue
                
            final_msg = "\n".join(blocks)
            
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    payload = {"chat_id": chat_id, "text": final_msg, "parse_mode": "HTML"}
                    resp = requests.post(url, json=payload, timeout=10)
                    resp.raise_for_status()
                    logging.info(f"Delivered to {dest['name']}")
                except Exception as e:
                    logging.error(f"Failed delivery to {dest['name']}: {e}")
                    success = False
        return success
