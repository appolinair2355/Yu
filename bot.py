"""
Telegram Bot implementation with advanced features and deployment capabilities
"""
import os
import logging
import requests
import json
from typing import Dict, Any
from handlers import TelegramHandlers
from card_predictor import card_predictor

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.deployment_file_path = "deployment.zip"
        # Initialize advanced handlers
        self.handlers = TelegramHandlers(token)
        
    def handle_update(self, update: Dict[str, Any]) -> None:
        """Handle incoming Telegram update with advanced features"""
        try:
            logger.info(f"Received update: {json.dumps(update, indent=2)}")
            self.handlers.handle_update(update)

            if 'message' in update:
                self._process_card_predictions(update['message'])
            elif 'edited_message' in update:
                self._process_card_predictions(update['edited_message'])

        except Exception as e:
            logger.error(f"Error handling update: {e}")
    
    def _process_card_predictions(self, message: Dict[str, Any]) -> None:
        """Process message for card predictions"""
        try:
            chat_id = message['chat']['id']
            chat_type = message['chat'].get('type', 'private')

            if chat_type in ['group', 'supergroup', 'channel'] and 'text' in message:
                text = message['text']
                should_predict, game_number, combination = card_predictor.should_predict(text)

                if should_predict and game_number and combination:
                    prediction = card_predictor.make_prediction(game_number, combination)
                    logger.info(f"Making prediction: {prediction}")
                    self.send_message(chat_id, prediction)

                verification_result = card_predictor.verify_prediction(text)
                if verification_result:
                    logger.info(f"Verification result: {verification_result}")
                    if verification_result['type'] == 'update_message':
                        self.send_message(chat_id, verification_result['new_message'])

        except Exception as e:
            logger.error(f"Error processing card predictions: {e}")
    
    def handle_start_command(self, chat_id: int) -> None:
        """Handle /start command by sending deployment zip file"""
        try:
            self.send_message(chat_id, "🚀 Preparing your deployment zip file... Please wait a moment.")

            if not os.path.exists(self.deployment_file_path):
                self.send_message(chat_id, "❌ Deployment file not found. Please contact the administrator.")
                logger.error(f"Deployment file {self.deployment_file_path} not found")
                return
            
            success = self.send_document(chat_id, self.deployment_file_path)

            if success:
                self.send_message(chat_id, "✅ Deployment zip file sent successfully!\n\n")
        except Exception as e:
            logger.error(f"Error in handle_start_command: {e}")

    def send_message(self, chat_id: int, text: str) -> bool:
        """Send a text message via Telegram Bot API"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_document(self, chat_id: int, file_path: str) -> bool:
        """Send a document (like a zip file) via Telegram Bot API"""
        try:
            url = f"{self.base_url}/sendDocument"
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': chat_id}
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send document: {e}")
            return False

    def set_webhook(self, url: str) -> bool:
        """Set the Telegram webhook"""
        try:
            full_url = f"{self.base_url}/setWebhook"
            payload = {"url": url}
            response = requests.post(full_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False
