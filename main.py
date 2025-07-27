"""
Main entry point for the Telegram bot deployment on render.com
"""
import os
import logging
from flask import Flask, request
from bot import TelegramBot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = Config()

# Initialize bot
bot = TelegramBot(config.BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        update = request.get_json()
        if update:
            bot.handle_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return 'Error', 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render.com"""
    return {'status': 'healthy', 'service': 'telegram-bot'}, 200

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return {'message': 'Telegram Bot is running', 'status': 'active'}, 200

if __name__ == '__main__':
    # --- Webhook setup forcé ---
    if config.WEBHOOK_URL:
        success = bot.set_webhook(f"{config.WEBHOOK_URL}/webhook")
        if success:
            logger.info(f"✅ Webhook set to {config.WEBHOOK_URL}/webhook")
        else:
            logger.error("❌ Failed to set webhook")
    else:
        logger.warning("⚠️ WEBHOOK_URL not provided. Skipping webhook setup.")

    # --- Run the Flask app ---
    port = config.PORT
    logger.info(f"🚀 Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
