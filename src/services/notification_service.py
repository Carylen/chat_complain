import requests
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__, settings.log_level)

class NotificationService:
    def __init__(self):
        # Ambil webhook URL dari settings (config.py)
        self.finance_webhook_url = settings.google_chat_finance_webhook
        if not self.finance_webhook_url:
            logger.warning("GOOGLE_CHAT_FINANCE_WEBHOOK not set. Notifications disabled.")

    def send_finance_alert(self, message: str):
        if not self.finance_webhook_url:
            return

        try:
            payload = {"text": message}
            response = requests.post(self.finance_webhook_url, json=payload)
            response.raise_for_status() # Error jika gagal kirim
            logger.info("Sent notification to Finance Google Chat")
        except Exception as e:
            logger.error(f"Failed to send Google Chat notification: {e}")

# Factory function
def create_notification_service() -> NotificationService:
    return NotificationService()