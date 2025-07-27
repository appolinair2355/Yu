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
            # Log the update for debugging
            logger.info(f"Received update: {json.dumps(update, indent=2)}")
            
            # Use the advanced handlers for processing
            self.handlers.handle_update(update)
            
            # Also process for card predictions if it's a message
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
            
            # Only process card predictions in groups/channels
            if chat_type in ['group', 'supergroup', 'channel'] and 'text' in message:
                text = message['text']
                
                # Check if we should make a prediction
                should_predict, game_number, combination = card_predictor.should_predict(text)
                
                if should_predict and game_number is not None and combination is not None:
                    prediction = card_predictor.make_prediction(game_number, combination)
                    logger.info(f"Making prediction: {prediction}")
                    
                    # Send prediction to the chat
                    self.send_message(chat_id, prediction)
                
                # Check if this message verifies a previous prediction
                verification_result = card_predictor.verify_prediction(text)
                if verification_result:
                    logger.info(f"Verification result: {verification_result}")
                    
                    if verification_result['type'] == 'update_message':
                        # For webhook mode, just send the updated status as a new message
                        self.send_message(chat_id, verification_result['new_message'])
                        
        except Exception as e:
            logger.error(f"Error processing card predictions: {e}")
    
    def handle_start_command(self, chat_id: int) -> None:
        """Handle /start command by sending deployment zip file"""
        try:
            # Send initial message
            self.send_message(
                chat_id, 
                "🚀 Preparing your deployment zip file... Please wait a moment."
            )
            
            # Check if deployment file exists
            if not os.path.exists(self.deployment_file_path):
                self.send_message(
                    chat_id,
                    "❌ Deployment file not found. Please contact the administrator."
                )
                logger.error(f"Deployment file {self.deployment_file_path} not found")
                return
            
            # Send the file
            success = self.send_document(chat_id, self.deployment_file_path)
            
            if success:
                self.send_message(
                    chat_id,
                    "✅ Deployment zip file sent successfully!\n\n"
             
