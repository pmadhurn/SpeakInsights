#!/usr/bin/env python3
"""
Test Ollama connectivity and model availability
"""

import requests
import json
from config import config

def test_ollama():
    print("=" * 60)
    print("🦙 Ollama Integration Test")
    print("=" * 60)
    
    print(f"Ollama URL: {config.OLLAMA_BASE_URL}")
    print(f"Target Model: {config.OLLAMA_MODEL}")
    print(f"Timeout: {config.OLLAMA_TIMEOUT}s")
    print()
    
    try:
        # Test server connectivity
        print("[1/3] Testing Ollama server connectivity...")
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama server is running")
        else:
            print(f"❌ Ollama server error: {response.status_code}")
            return
        
        # Check available models
        print("[2/3] Checking available models...")
        models_data = response.json()
        models = models_data.get('models', [])
        
        if not models:
            print("❌ No models found in Ollama")
            print("💡 Try running: ollama pull llama3.2")
            return
        
        print("Available models:")
        model_names = []
        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3) if size else 0
            print(f"  - {name} ({size_gb:.1f} GB)")
            model_names.append(name.split(':')[0])
        
        # Check if target model is available
        available_models = [model.get('name', '') for model in models]
        model_found = (config.OLLAMA_MODEL in available_models or 
                      config.OLLAMA_MODEL.split(':')[0] in model_names)
        
        if model_found:
            print(f"✅ Target model '{config.OLLAMA_MODEL}' is available")
        else:
            print(f"❌ Target model '{config.OLLAMA_MODEL}' not found")
            print(f"Available models: {', '.join(available_models)}")
            print(f"💡 Try running: ollama pull {config.OLLAMA_MODEL}")
            return
        
        # Test summarization and action items
        print("[3/4] Testing summarization...")
        test_text = """
        This is a test meeting transcript. We discussed the quarterly budget review and decided to increase marketing spend by 15%. 
        John raised concerns about the timeline, but Sarah confirmed that the development team can meet the deadline. 
        Action items include finalizing the budget proposal and scheduling a follow-up meeting next week.
        We need to contact the vendor by Friday. Sarah will prepare the presentation for next Monday's board meeting.
        """
        
        prompt = f"""Please provide a brief summary of this meeting transcript:

{test_text}

Summary:"""

        payload = {
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 200
            }
        }
        
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=config.OLLAMA_TIMEOUT  # Use config timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', '').strip()
            
            if summary:
                print("✅ Summarization test successful!")
                print(f"Test summary: {summary}")
            else:
                print("❌ Empty response from model")
        else:
            print(f"❌ Summarization failed: {response.status_code}")
            print(response.text)
            return
        
        # Test action item extraction
        print("[4/4] Testing action item extraction...")
        action_prompt = f"""Please analyze the following meeting transcript and extract all action items, tasks, and follow-up items. 

Format your response as a simple numbered list of actionable tasks.

Meeting Transcript:
{test_text}

Action Items:"""

        action_payload = {
            "model": config.OLLAMA_MODEL,
            "prompt": action_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.8,
                "max_tokens": 200
            }
        }
        
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json=action_payload,
            timeout=config.OLLAMA_TIMEOUT  # Use config timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            actions = result.get('response', '').strip()
            
            if actions:
                print("✅ Action item extraction test successful!")
                print(f"Test action items: {actions}")
            else:
                print("❌ Empty response for action items")
        else:
            print(f"❌ Action item extraction failed: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server")
        print("💡 Make sure Ollama is running: ollama serve")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 Try a smaller/faster model")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_ollama()