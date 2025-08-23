import os
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = Bot(token=self.bot_token) if self.bot_token else None
        
    def send_jobs(self, jobs: list, keyword: str = ""):
        if not self.bot or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
            
        if not jobs:
            return False  # Não enviar se não há vagas
            
        # Filtrar apenas vagas relevantes (máximo 5)
        filtered_jobs = self._filter_relevant_jobs(jobs, keyword)[:5]
        
        if not filtered_jobs:
            return False
            
        message = f"🚀 **{len(filtered_jobs)} NOVAS VAGAS - {keyword.upper()}**\n\n"
        
        for i, job in enumerate(filtered_jobs, 1):
            message += f"{i}. **{job['title']}**\n"
            message += f"📅 {job['date']} | 🌐 {job['source']}\n"
            message += f"🔗 {job['link']}\n\n"
            
        return self._send_message(message)
    
    def _filter_relevant_jobs(self, jobs: list, keyword: str) -> list:
        """Filtra vagas mais relevantes para evitar spam"""
        keyword_lower = keyword.lower()
        relevant = []
        
        for job in jobs:
            title_lower = job['title'].lower()
            # Priorizar vagas que contenham a palavra-chave no título
            if any(word in title_lower for word in keyword_lower.split()):
                relevant.append(job)
        
        return relevant or jobs  # Se nenhuma relevante, retorna todas
    
    def send_status(self, message: str):
        if self.bot and self.chat_id:
            return self._send_message(f"ℹ️ {message}")
        return False
    
    def _send_message(self, message: str):
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            logger.info("Message sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False