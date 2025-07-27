"""
Configuration settings for the Telegram bot
"""
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for bot settings"""

    def __init__(self):
        self.BOT_TOKEN = self._get_bot_token()
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL', '').strip()
        self.PORT = int(os.getenv('PORT', 10000))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

        # Validate config
        self._validate_config()

    def _get_bot_token(self) -> str:
        """Get bot token from environment variables"""
        token = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN', '')

        if not token:
            logger.error("❌ Bot token not found in environment variables")
            raise ValueError(
                "BOT_TOKEN is required. Set it in your Render environment variables."
            )

        return token

    def _validate_config(self) -> None:
        """Validate configuration settings"""
        if not self.BOT_TOKEN or len(self.BOT_TOKEN.split(':')) != 2:
            raise ValueError("❌ Invalid or missing bot token format")

        if self.WEBHOOK_URL and not self.WEBHOOK_URL.startswith('https://'):
            logger.warning("⚠️ Webhook URL should use HTTPS")

        logger.info("✅ Configuration validated successfully")

    def get_webhook_url(self) -> str:
        """Return full webhook URL"""
        if self.WEBHOOK_URL:
            return f"{self.WEBHOOK_URL}/webhook"
        return ""

    def __str__(self) -> str:
        return (
            f"Config(webhook_url={self.WEBHOOK_URL}, "
            f"port={self.PORT}, debug={self.DEBUG})"
            )
