import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List

from .provider import NotificationProvider
from src.models.decision import InvestmentDecision

class EmailProvider(NotificationProvider):
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
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #333;">{icon} {decision.symbol}{name_display}</h3>
                <p><strong>Recommendation:</strong> {decision.recommendation}</p>
                <p><strong>Current Price:</strong> ₹{decision.current_price:.2f}</p>
                <p><strong>Target Entry:</strong> ₹{decision.target_price:.2f} (Distance: {((decision.current_price / decision.target_price - 1) * 100) if decision.target_price else 0:.1f}%)</p>
                <p><strong>Score:</strong> {decision.investment_score}/100<br/>
                Business: {decision.scores.get('quality', 0):.0f}/100 | 
                Entry: {decision.scores.get('entry', 0):.0f}/100 | 
                Risk: {decision.scores.get('risk', 0):.0f}/100</p>
                <p><strong>Confidence:</strong> {decision.confidence}<br/>
                <strong>Investment Horizon:</strong> {decision.investment_horizon}<br/>
                <strong>Review Period:</strong> {decision.review_period}</p>
            </div>
        """
        
        if decision.transition_alert:
            alert_icon = "🟢" if "UPGRADE" in decision.transition_alert else "🔴"
            html += f"<p><strong>{alert_icon} Decision {decision.transition_alert}</strong></p>"
            
        html += "<h3>Why:</h3><ul>"
        for t in decision.thesis:
            html += f"<li>{t}</li>"
        html += "</ul>"
            
        if decision.warnings:
            html += "<h3>Warnings:</h3><ul>"
            for w in decision.warnings:
                html += f"<li>{w}</li>"
            html += "</ul>"
                
        if decision.red_flags:
            html += "<h3>Red Flags:</h3><ul>"
            for r in decision.red_flags:
                html += f"<li>{r}</li>"
            html += "</ul>"
            
        html += """
            <hr style="border: 1px solid #eee; margin-top: 20px;" />
            <p style="font-size: 12px; color: #888;">Trading Alert System Automated Report</p>
        </body>
        </html>
        """
        return html

    def send_batch(self, decisions: List[InvestmentDecision]) -> bool:
        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = os.environ.get("SMTP_PORT", 587)
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        smtp_from = os.environ.get("SMTP_FROM", smtp_user)
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            logging.warning("Missing SMTP credentials in .env file. Email notifications skipped.")
            return False
            
        destinations = self.config.get('destinations', [])
        success_count = 0
        
        for dest in destinations:
            if not dest.get('enabled', False):
                continue
                
            email_env = f"EMAIL_TO_{dest['name'].upper()}"
            to_email = os.environ.get(email_env)
            
            if not to_email:
                logging.warning(f"Missing {email_env} in .env file. Skipping {dest['name']} email route.")
                continue
                
            allow_all = dest.get('detailed_research_alerts', False)
            blocks = []
            
            for decision in decisions:
                if not allow_all and decision.recommendation in ["WAIT", "AVOID", "WATCHLIST", "RESEARCH"]:
                    continue
                blocks.append(self.format_decision(decision))
                
            if not blocks:
                continue
                
            msg = MIMEMultipart("alternative")
            
            # If multiple decisions, use generic subject, else specific
            if len(blocks) == 1:
                title_decision = [d for d in decisions if d.recommendation not in ["WAIT", "AVOID", "WATCHLIST", "RESEARCH"] or allow_all][0]
                msg["Subject"] = f"Trading Alert: {title_decision.recommendation} {title_decision.symbol}"
            else:
                msg["Subject"] = f"Trading Alerts: {len(blocks)} Notifications"
                
            msg["From"] = smtp_from
            msg["To"] = to_email
            
            combined_html = f"<html><body>{'<hr/>'.join(blocks)}</body></html>"
            msg.attach(MIMEText(combined_html, "html"))
            
            try:
                with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                logging.info(f"Delivered Email batch to {dest['name']}")
                success_count += 1
            except Exception as e:
                logging.error(f"Failed Email delivery to {dest['name']}: {e}")
                
        return success_count > 0
