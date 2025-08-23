#!/usr/bin/env python3
"""
Test script for webhook functionality
"""

import json
import requests
from datetime import datetime

def test_webhook_direct(webhook_url):
    """Test webhook directly with sample data"""
    print(f"Testing webhook URL: {webhook_url}")
    
    # Test payload for action items
    test_payload = {
        "type": "action_items",
        "meeting_id": "test_123",
        "action_items": [
            "Follow up with client about project timeline",
            "Schedule team meeting for next week",
            "Review budget proposal by Friday"
        ],
        "timestamp": datetime.now().isoformat(),
        "count": 3,
        "meeting_metadata": {
            "filename": "test_meeting.mp3",
            "duration": 1800,
            "processed_at": datetime.now().isoformat(),
            "summary": "Test meeting summary for webhook integration"
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'SpeakInsights-Webhook-Test/1.0'
            }
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            return True
        else:
            print(f"❌ Webhook test failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Webhook test timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_api_webhook():
    """Test webhook through the API"""
    print("Testing webhook through SpeakInsights API...")
    
    try:
        response = requests.post("http://localhost:8000/api/webhook/test", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"API Response: {result}")
            
            if result.get('status') == 'connected':
                print("✅ API webhook test successful!")
                return True
            else:
                print("❌ API webhook test failed")
                return False
        else:
            print(f"❌ API test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def load_config():
    """Load webhook configuration"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config.get('webhook_settings', {})
    except Exception as e:
        print(f"❌ Could not load config: {e}")
        return {}

def main():
    print("🔗 SpeakInsights Webhook Test Tool")
    print("=" * 40)
    
    # Load configuration
    webhook_config = load_config()
    
    if not webhook_config:
        print("❌ No webhook configuration found in config.json")
        return
    
    print(f"Webhook enabled: {webhook_config.get('enabled', False)}")
    print(f"Send action items: {webhook_config.get('send_action_items', True)}")
    print(f"Send summaries: {webhook_config.get('send_summaries', False)}")
    
    webhook_url = webhook_config.get('n8n_webhook_url', '')
    
    if not webhook_url:
        print("❌ No webhook URL configured")
        print("Please set 'n8n_webhook_url' in config.json")
        return
    
    print(f"Webhook URL: {webhook_url}")
    print()
    
    # Test 1: Direct webhook test
    print("Test 1: Direct webhook test")
    print("-" * 30)
    success1 = test_webhook_direct(webhook_url)
    print()
    
    # Test 2: API webhook test
    print("Test 2: API webhook test")
    print("-" * 30)
    success2 = test_api_webhook()
    print()
    
    # Summary
    print("Test Summary:")
    print(f"Direct test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"API test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Webhook integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check your n8n webhook configuration.")

if __name__ == "__main__":
    main()