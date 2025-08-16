from transformers import pipeline
import nltk
import re
from config import config

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Lazy loading for models
_summarizer = None
_sentiment_analyzer = None

def get_summarizer():
    """Get summarizer with lazy loading"""
    global _summarizer
    if _summarizer is None:
        print(f"Loading summarization model: {config.SUMMARIZER_MODEL}")
        try:
            _summarizer = pipeline("summarization", model=config.SUMMARIZER_MODEL)
            print("✅ Summarization model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading summarization model: {e}")
            print("Falling back to default model...")
            _summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
    return _summarizer

def get_sentiment_analyzer():
    """Get sentiment analyzer with lazy loading"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        print(f"Loading sentiment model: {config.SENTIMENT_MODEL}")
        try:
            _sentiment_analyzer = pipeline("text-classification", model=config.SENTIMENT_MODEL)
            print("✅ Sentiment model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading sentiment model: {e}")
            print("Falling back to default model...")
            _sentiment_analyzer = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    return _sentiment_analyzer

def summarize_text(text, max_length=None):
    """Generate summary of the transcript"""
    if not text or not text.strip():
        return "No content to summarize"
    
    if max_length is None:
        max_length = config.MAX_SUMMARY_LENGTH
    
    try:
        summarizer = get_summarizer()
        
        # Handle long texts by chunking
        max_chunk_length = 1024
        
        if len(text) <= max_chunk_length:
            summary = summarizer(text, max_length=max_length, min_length=10, do_sample=False)
            return summary[0]['summary_text']
        else:
            # For long texts, summarize first chunk
            chunk = text[:max_chunk_length]
            summary = summarizer(chunk, max_length=max_length, min_length=10, do_sample=False)
            return summary[0]['summary_text'] + " [Summary of beginning of meeting]"
            
    except Exception as e:
        print(f"Error in summarize_text: {e}")
        return f"Could not generate summary: {str(e)}"

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

def extract_action_items(text):
    """Extract potential action items from text"""
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
