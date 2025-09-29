"""
User Feedback Module - C-MORP
WhatsApp Integration for Thumbs Up/Down Feedback
Smart India Hackathon 2025
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import requests
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Feedback:
    """User feedback data structure"""
    feedback_id: str
    user_id: str
    timestamp: str
    rating: str  # 'thumbs_up' or 'thumbs_down'
    category: str
    message: Optional[str] = None
    metadata: Optional[Dict] = None


class WhatsAppFeedbackHandler:
    """Handle user feedback via WhatsApp Business API"""
    
    def __init__(self, api_key: str, phone_number_id: str):
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def send_feedback_request(self, recipient: str, context: Dict) -> bool:
        """Send feedback request with thumbs up/down buttons"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": f"How would you rate the optimization result?\n\n"
                                f"💡 Cost Savings: ₹{context.get('cost_savings', 0):.2f}\n"
                                f"⚡ Energy Saved: {context.get('energy_saved', 0):.2f} kWh\n"
                                f"🌱 Carbon Reduced: {context.get('carbon_saved', 0):.2f} kg CO2"
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": f"thumbs_up_{context.get('optimization_id')}",
                                    "title": "👍 Good"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": f"thumbs_down_{context.get('optimization_id')}",
                                    "title": "👎 Not Good"
                                }
                            }
                        ]
                    }
                }
            }
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Feedback request sent to {recipient}")
                return True
            else:
                logger.error(f"Failed to send feedback: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def process_feedback(self, webhook_data: Dict) -> Optional[Feedback]:
        """Process incoming feedback from WhatsApp webhook"""
        try:
            # Extract feedback from webhook
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])
            
            if not messages:
                return None
            
            message = messages[0]
            button_reply = message.get('interactive', {}).get('button_reply', {})
            reply_id = button_reply.get('id', '')
            
            # Parse feedback
            if reply_id.startswith('thumbs_up_'):
                rating = 'thumbs_up'
                opt_id = reply_id.replace('thumbs_up_', '')
            elif reply_id.startswith('thumbs_down_'):
                rating = 'thumbs_down'
                opt_id = reply_id.replace('thumbs_down_', '')
            else:
                return None
            
            feedback = Feedback(
                feedback_id=f"fb_{datetime.now().timestamp()}",
                user_id=message.get('from'),
                timestamp=datetime.now().isoformat(),
                rating=rating,
                category='optimization_result',
                metadata={'optimization_id': opt_id}
            )
            
            logger.info(f"Feedback received: {rating} from {feedback.user_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return None
    
    def send_thank_you(self, recipient: str, rating: str):
        """Send thank you message after feedback"""
        emoji = "🙏" if rating == "thumbs_up" else "📝"
        message = (
            f"{emoji} Thank you for your feedback!\n\n"
            f"{'We are glad you found it helpful!' if rating == 'thumbs_up' else 'We will work to improve the results.'}"
        )
        
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": message}
            }
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            requests.post(url, headers=self.headers, json=payload, timeout=10)
            
        except Exception as e:
            logger.error(f"Error sending thank you: {e}")


class FeedbackAnalytics:
    """Analyze user feedback patterns"""
    
    def __init__(self):
        self.feedbacks = []
    
    def add_feedback(self, feedback: Feedback):
        """Add feedback to analytics"""
        self.feedbacks.append(asdict(feedback))
    
    def get_satisfaction_rate(self) -> float:
        """Calculate overall satisfaction rate"""
        if not self.feedbacks:
            return 0.0
        
        positive = sum(1 for fb in self.feedbacks if fb['rating'] == 'thumbs_up')
        return (positive / len(self.feedbacks)) * 100
    
    def get_category_stats(self) -> Dict:
        """Get statistics by category"""
        stats = {}
        for fb in self.feedbacks:
            category = fb['category']
            if category not in stats:
                stats[category] = {'thumbs_up': 0, 'thumbs_down': 0, 'total': 0}
            
            stats[category][fb['rating']] += 1
            stats[category]['total'] += 1
        
        return stats


# Benchmark example
def run_feedback_benchmark():
    """Test feedback system"""
    # Note: Replace with actual API credentials for production
    handler = WhatsAppFeedbackHandler(
        api_key=os.getenv("WHATSAPP_API_KEY", "test_key"),
        phone_number_id=os.getenv("WHATSAPP_PHONE_ID", "test_id")
    )
    
    # Simulate feedback
    analytics = FeedbackAnalytics()
    
    sample_feedbacks = [
        Feedback("fb1", "user1", datetime.now().isoformat(), "thumbs_up", "optimization_result"),
        Feedback("fb2", "user2", datetime.now().isoformat(), "thumbs_up", "optimization_result"),
        Feedback("fb3", "user3", datetime.now().isoformat(), "thumbs_down", "optimization_result"),
    ]
    
    for fb in sample_feedbacks:
        analytics.add_feedback(fb)
    
    satisfaction = analytics.get_satisfaction_rate()
    logger.info(f"Satisfaction Rate: {satisfaction:.2f}%")
    logger.info(f"Category Stats: {analytics.get_category_stats()}")
    
    return satisfaction


if __name__ == "__main__":
    run_feedback_benchmark()
