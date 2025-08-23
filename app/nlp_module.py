from transformers import pipeline
import nltk
import re
import torch
import requests
import json
from config import config
from .webhook import WebhookManager

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Check GPU availability
def get_device():
    """Get the best available device (GPU if available, else CPU)"""
    if torch.cuda.is_available():
        device = 0  # Use first GPU
        print(f"[GPU] GPU detected: {torch.cuda.get_device_name(0)}")
        return device, "GPU"
    else:
        print("[CPU] No GPU detected, using CPU")
        return -1, "CPU"

# Get device info once
DEVICE, DEVICE_NAME = get_device()

# Initialize webhook manager
webhook_manager = WebhookManager(config.RAW_CONFIG)

# Lazy loading for models
_summarizer = None
_sentiment_analyzer = None

def get_summarizer():
    """Get summarizer with lazy loading and GPU support"""
    global _summarizer
    if _summarizer is None:
        print(f"Loading summarization model: {config.SUMMARIZER_MODEL} on {DEVICE_NAME}")
        try:
            _summarizer = pipeline("summarization", model=config.SUMMARIZER_MODEL, device=DEVICE)
            print(f"[OK] Summarization model loaded successfully on {DEVICE_NAME}")
        except Exception as e:
            print(f"[ERROR] Error loading summarization model: {e}")
            print("Falling back to default model...")
            _summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", device=DEVICE)
    return _summarizer

def get_sentiment_analyzer():
    """Get sentiment analyzer with lazy loading and GPU support"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        print(f"Loading sentiment model: {config.SENTIMENT_MODEL} on {DEVICE_NAME}")
        try:
            _sentiment_analyzer = pipeline("text-classification", model=config.SENTIMENT_MODEL, device=DEVICE)
            print(f"[OK] Sentiment model loaded successfully on {DEVICE_NAME}")
        except Exception as e:
            print(f"[ERROR] Error loading sentiment model: {e}")
            print("Falling back to default model...")
            _sentiment_analyzer = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english", device=DEVICE)
    return _sentiment_analyzer

def summarize_with_ollama(text):
    """Generate summary using Ollama API"""
    try:
        print(f"[OLLAMA] Generating summary using {config.OLLAMA_MODEL}...")
        
        # Create a detailed prompt for better summarization
        prompt = f"""Please provide a comprehensive summary of the following meeting transcript. Focus on:
1. Main topics discussed
2. Key decisions made
3. Important points raised
4. Overall meeting outcome

Meeting Transcript:
{text}

Summary:"""

        payload = {
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=config.OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', '').strip()
            
            if summary:
                print(f"[OLLAMA] Summary generated successfully ({len(summary)} chars)")
                return summary
            else:
                raise Exception("Empty response from Ollama")
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Ollama summarization failed: {e}")
        raise

def summarize_with_local_model(text, max_length=None):
    """Fallback to local model summarization"""
    if max_length is None:
        max_length = config.MAX_SUMMARY_LENGTH
    
    try:
        print("[LOCAL] Using local model for summarization...")
        summarizer = get_summarizer()
        
        # For local model, we still need to chunk if text is too long
        max_chunk_length = 1024
        
        if len(text) <= max_chunk_length:
            summary = summarizer(text, max_length=max_length, min_length=10, do_sample=False)
            return summary[0]['summary_text']
        else:
            # Use first chunk only for local model to avoid complexity
            chunk = text[:max_chunk_length]
            summary = summarizer(chunk, max_length=max_length, min_length=10, do_sample=False)
            return summary[0]['summary_text'] + " [Summary of beginning - full transcript too long for local model]"
            
    except Exception as e:
        print(f"[ERROR] Local summarization failed: {e}")
        return f"Could not generate summary: {str(e)}"

def check_ollama_availability():
    """Check if Ollama is available and the model is loaded"""
    try:
        # Check if Ollama is running
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, "Ollama server not responding"
        
        # Check if our model is available
        models = response.json().get('models', [])
        available_models = [model.get('name', '') for model in models]
        model_names = [model.split(':')[0] for model in available_models]
        
        # Check both full name and base name
        model_found = (config.OLLAMA_MODEL in available_models or 
                      config.OLLAMA_MODEL.split(':')[0] in model_names)
        
        if not model_found:
            return False, f"Model {config.OLLAMA_MODEL} not found. Available: {', '.join(available_models)}"
        
        return True, "Ollama available"
        
    except Exception as e:
        return False, f"Ollama check failed: {str(e)}"

def summarize_text(text, max_length=None):
    """Generate summary using Ollama (preferred) or local model (fallback)"""
    if not text or not text.strip():
        return "No content to summarize"
    
    # Try Ollama first if enabled
    if config.USE_OLLAMA:
        ollama_available, status_msg = check_ollama_availability()
        print(f"[INFO] Ollama status: {status_msg}")
        
        if ollama_available:
            try:
                return summarize_with_ollama(text)
            except Exception as e:
                print(f"[WARNING] Ollama failed: {e}")
                if config.FALLBACK_TO_LOCAL:
                    print("[INFO] Falling back to local model...")
                else:
                    return f"Ollama summarization failed: {str(e)}"
        else:
            print(f"[WARNING] Ollama not available: {status_msg}")
            if not config.FALLBACK_TO_LOCAL:
                return f"Ollama not available: {status_msg}"
    
    # Use local model as fallback or primary method
    return summarize_with_local_model(text, max_length)

def analyze_sentiment(text):
    """Analyze sentiment of the text"""
    if not text or not text.strip():
        return "neutral"
    
    try:
        sentiment_analyzer = get_sentiment_analyzer()
        
        # Use a simpler sentiment analysis approach to avoid tensor size issues
        sample = text[:512] if len(text) > 512 else text  # Limit input size
        
        # Use a more robust sentiment analysis
        raw_results = sentiment_analyzer(sample, truncation=True, padding=True)

        # Handle different model outputs
        if isinstance(raw_results, list) and len(raw_results) > 0:
            result = raw_results[0]
            
            if isinstance(result, dict) and 'label' in result and 'score' in result:
                label = result['label'].upper()
                score = result['score']
                
                # Map different model outputs to standard sentiment
                if label in ['POSITIVE', 'POS', '1']:
                    return f"positive ({score:.1%})"
                elif label in ['NEGATIVE', 'NEG', '0']:
                    return f"negative ({score:.1%})"
                else:
                    return f"neutral ({score:.1%})"
            
        return "neutral"
            
    except Exception as e:
        print(f"Error in analyze_sentiment: {e}")
        return "neutral"

def extract_action_items_with_ollama(text):
    """Extract action items using Ollama API"""
    try:
        print(f"[OLLAMA] Extracting action items using {config.OLLAMA_MODEL}...")
        
        prompt = f"""Please analyze the following meeting transcript and extract all action items, tasks, and follow-up items. 

Format your response as a simple numbered list of actionable tasks. Focus on:
- Specific tasks that need to be completed
- Follow-up actions mentioned
- Assignments given to people
- Deadlines or commitments made
- Next steps discussed

If no clear action items are found, respond with "No specific action items identified."

Meeting Transcript:
{text}

Action Items:"""

        payload = {
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.8,
                "max_tokens": 400
            }
        }
        
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=config.OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            action_text = result.get('response', '').strip()
            
            if action_text and "no specific action items" not in action_text.lower():
                # Parse the numbered list into individual items
                action_items = []
                lines = action_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Remove numbering (1., 2., -, *, etc.)
                    cleaned = re.sub(r'^[\d\-\*\•]+\.?\s*', '', line)
                    cleaned = cleaned.strip()
                    
                    if len(cleaned) > 10 and len(cleaned) < 200:
                        action_items.append(cleaned)
                
                print(f"[OLLAMA] Extracted {len(action_items)} action items")
                return action_items[:config.MAX_ACTION_ITEMS]
            else:
                print("[OLLAMA] No action items found")
                return []
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Ollama action item extraction failed: {e}")
        raise

def extract_action_items_with_local_model(text):
    """Fallback to regex-based action item extraction"""
    print("[LOCAL] Using regex-based action item extraction...")
    
    if not text or not text.strip():
        return []
    
    action_items = []
    
    # Keywords that often indicate action items
    action_patterns = [
        r"(?i)(we will|I will|will)\s+(.+?)(?:\.|$)",
        r"(?i)(need to|needs to)\s+(.+?)(?:\.|$)",
        r"(?i)(should|must)\s+(.+?)(?:\.|$)",
        r"(?i)(action item[s]?:|todo:|task:)\s*(.+?)(?:\.|$)",
        r"(?i)(follow up on|follow-up on)\s+(.+?)(?:\.|$)",
        r"(?i)(let's|let us)\s+(.+?)(?:\.|$)",
        r"(?i)(going to|gonna)\s+(.+?)(?:\.|$)",
    ]
    
    # Split into sentences more robustly
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        for pattern in action_patterns:
            matches = re.findall(pattern, sentence)
            for match in matches:
                # Get the action part (usually the second group)
                action = match[1] if len(match) > 1 else match[0]
                action = action.strip()
                
                # Clean up the action text
                action = re.sub(r'\s+', ' ', action)  # Remove extra whitespace
                
                # Filter out very short or very long items
                if 5 < len(action) < 150:
                    action_items.append(action.capitalize())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in action_items:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique_items.append(item)
    
    return unique_items[:config.MAX_ACTION_ITEMS]

def extract_action_items(text):
    """Extract action items using Ollama (preferred) or regex (fallback)"""
    if not text or not text.strip():
        return []
    
    # Try Ollama first if enabled
    if config.USE_OLLAMA:
        ollama_available, status_msg = check_ollama_availability()
        
        if ollama_available:
            try:
                return extract_action_items_with_ollama(text)
            except Exception as e:
                print(f"[WARNING] Ollama action item extraction failed: {e}")
                if config.FALLBACK_TO_LOCAL:
                    print("[INFO] Falling back to regex-based extraction...")
                else:
                    return []
        else:
            print(f"[WARNING] Ollama not available for action items: {status_msg}")
            if not config.FALLBACK_TO_LOCAL:
                return []
    
    # Use regex-based extraction as fallback or primary method
    return extract_action_items_with_local_model(text)

def send_action_items_webhook(meeting_id: str, action_items: list, meeting_data: dict = None):
    """Send action items to n8n webhook"""
    try:
        success = webhook_manager.send_action_items(meeting_id, action_items, meeting_data)
        if success:
            print(f"[WEBHOOK] Action items sent successfully for meeting {meeting_id}")
        else:
            print(f"[WEBHOOK] Failed to send action items for meeting {meeting_id}")
        return success
    except Exception as e:
        print(f"[WEBHOOK ERROR] Failed to send action items: {e}")
        return False

def send_summary_webhook(meeting_id: str, summary: str, meeting_data: dict = None):
    """Send summary to n8n webhook"""
    try:
        success = webhook_manager.send_summary(meeting_id, summary, meeting_data)
        if success:
            print(f"[WEBHOOK] Summary sent successfully for meeting {meeting_id}")
        else:
            print(f"[WEBHOOK] Failed to send summary for meeting {meeting_id}")
        return success
    except Exception as e:
        print(f"[WEBHOOK ERROR] Failed to send summary: {e}")
        return False

def test_webhook_connection():
    """Test webhook connectivity"""
    try:
        success = webhook_manager.test_webhook()
        if success:
            print("[WEBHOOK] Test successful - webhook is working")
        else:
            print("[WEBHOOK] Test failed - check webhook configuration")
        return success
    except Exception as e:
        print(f"[WEBHOOK ERROR] Test failed: {e}")
        return False