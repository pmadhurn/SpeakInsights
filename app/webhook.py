import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookManager:
    def __init__(self, config: Dict):
        self.config = config.get('webhook_settings', {})
        self.enabled = self.config.get('enabled', False)
        self.webhook_url = self.config.get('n8n_webhook_url', '')
        self.timeout = self.config.get('timeout', 30)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.send_action_items = self.config.get('send_action_items', True)
        self.send_summaries = self.config.get('send_summaries', False)
        self.include_metadata = self.config.get('include_meeting_metadata', True)
    
    def send_action_items(self, meeting_id: str, action_items: List[str], meeting_data: Optional[Dict] = None) -> bool:
        """Send action items to n8n webhook"""
        if not self.enabled or not self.webhook_url or not self.send_action_items:
            logger.info("Webhook disabled or not configured for action items")
            return False
        
        payload = {
            "type": "action_items",
            "meeting_id": meeting_id,
            "action_items": action_items,
            "timestamp": datetime.now().isoformat(),
            "count": len(action_items)
        }
        
        if self.include_metadata and meeting_data:
            payload["meeting_metadata"] = {
                "filename": meeting_data.get('filename', ''),
                "duration": meeting_data.get('duration', 0),
                "processed_at": meeting_data.get('processed_at', ''),
                "summary": meeting_data.get('summary', '') if self.send_summaries else None
            }
        
        return self._send_webhook(payload)
    
    def send_summary(self, meeting_id: str, summary: str, meeting_data: Optional[Dict] = None) -> bool:
        """Send meeting summary to n8n webhook"""
        if not self.enabled or not self.webhook_url or not self.send_summaries:
            logger.info("Webhook disabled or not configured for summaries")
            return False
        
        payload = {
            "type": "summary",
            "meeting_id": meeting_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.include_metadata and meeting_data:
            payload["meeting_metadata"] = {
                "filename": meeting_data.get('filename', ''),
                "duration": meeting_data.get('duration', 0),
                "processed_at": meeting_data.get('processed_at', '')
            }
        
        return self._send_webhook(payload)
    
    def _send_webhook(self, payload: Dict) -> bool:
        """Send webhook with retry logic using GET request with query parameters"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending webhook (attempt {attempt + 1}/{self.retry_attempts})")
                
                # Convert payload to query parameters for GET request
                params = {
                    'type': payload.get('type', ''),
                    'meeting_id': payload.get('meeting_id', ''),
                    'timestamp': payload.get('timestamp', ''),
                    'count': payload.get('count', 0)
                }
                
                # Add action items as comma-separated string
                if 'action_items' in payload:
                    params['action_items'] = '|'.join(payload['action_items'])
                
                # Add summary if present
                if 'summary' in payload:
                    params['summary'] = payload['summary']
                
                # Add meeting metadata as JSON string
                if 'meeting_metadata' in payload:
                    import json
                    params['meeting_metadata'] = json.dumps(payload['meeting_metadata'])
                
                response = requests.get(
                    self.webhook_url,
                    params=params,
                    timeout=self.timeout,
                    headers={
                        'User-Agent': 'SpeakInsights-Webhook/1.0'
                    }
                )
                
                if response.status_code == 200:
                    logger.info("Webhook sent successfully")
                    return True
                else:
                    logger.warning(f"Webhook failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Webhook timeout on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Webhook error on attempt {attempt + 1}: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                logger.info("Retrying webhook in 2 seconds...")
                import time
                time.sleep(2)
        
        logger.error("All webhook attempts failed")
        return False
    
    def test_webhook(self) -> bool:
        """Test webhook connectivity"""
        if not self.webhook_url:
            logger.error("No webhook URL configured")
            return False
        
        test_payload = {
            "type": "test",
            "message": "SpeakInsights webhook test",
            "timestamp": datetime.now().isoformat()
        }
        
        return self._send_webhook(test_payload)