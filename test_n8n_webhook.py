#!/usr/bin/env python3
"""
Simple n8n webhook test script
Run this after clicking 'Execute workflow' in n8n
"""

import requests
import json
from datetime import datetime

def test_n8n_webhook():
    webhook_url = "http://localhost:5678/webhook-test/9f78fcb9-8e15-46ee-b493-90fc8c698ebd"
    
    # Convert to GET request parameters
    params = {
        "type": "action_items",
        "meeting_id": "test_meeting_001",
        "action_items": "Follow up with client about project timeline|Schedule team meeting for next week|Review budget proposal by Friday|Update project documentation",
        "timestamp": datetime.now().isoformat(),
        "count": 4,
        "meeting_metadata": json.dumps({
            "filename": "weekly_standup.mp3",
            "duration": 1800,
            "processed_at": datetime.now().isoformat(),
            "summary": "Weekly standup meeting discussing project progress and upcoming deadlines"
        })
    }
    
    print("🔗 Testing n8n webhook with GET request...")
    print(f"URL: {webhook_url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    print()
    
    try:
        response = requests.get(
            webhook_url, 
            params=params, 
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 Webhook test successful!")
            return True
        else:
            print(f"\n❌ Webhook test failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 n8n Webhook Test")
    print("=" * 30)
    print("📋 Instructions:")
    print("1. Go to your n8n workflow")
    print("2. Click 'Execute workflow' button")
    print("3. Run this script within a few seconds")
    print()
    
    input("Press Enter when ready to test...")
    test_n8n_webhook()