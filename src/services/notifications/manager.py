import os
import yaml
import logging
from typing import List

from src.models.decision import InvestmentDecision
from .provider import NotificationProvider
from .telegram_provider import TelegramProvider
from .email_provider import EmailProvider

class NotificationManager:
    def __init__(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config', 'notifications.yaml')
        try:
            with open(settings_path, 'r') as f:
                self.config = yaml.safe_load(f).get('notifications', {})
        except FileNotFoundError:
            self.config = {}
            
        self.providers: List[NotificationProvider] = []
        self._initialize_providers()
        
    def _initialize_providers(self):
        if self.config.get('telegram', {}).get('enabled', False):
            self.providers.append(TelegramProvider(self.config['telegram']))
            
        if self.config.get('email', {}).get('enabled', False):
            self.providers.append(EmailProvider(self.config['email']))
            
    def route_decisions(self, decisions: List[InvestmentDecision]):
        if not self.providers:
            return
            
        for provider in self.providers:
            provider.send_batch(decisions)
