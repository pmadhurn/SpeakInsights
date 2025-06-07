from transformers import pipeline
import nltk
import re

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Initialize models (this will download on first run)
print("Loading NLP models...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")  # Smaller model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def summarize_text(text, max_length=150):
    """Generate summary of the transcript"""
    try:
        # Handle long texts by chunking
        max_chunk_length = 1024
        
        if len(text) <= max_chunk_length:
            summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        else:
            # For long texts, summarize first chunk
            chunk = text[:max_chunk_length]
            summary = summarizer(chunk, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]['summary_text'] + " [Summary of beginning of meeting]"
            
    except Exception as e:
        return f"Could not generate summary: {str(e)}"

def analyze_sentiment(text):
    """Analyze overall sentiment"""
    try:
        # Analyze first 512 characters
        sample = text[:512]
        result = sentiment_analyzer(sample)
        
        label = result[0]['label']
        score = result[0]['score']
        
        # Convert to more readable format
        if label == 'POSITIVE':
            return f"Positive ({score:.2%} confidence)"
        else:
            return f"Negative ({score:.2%} confidence)"
            
    except Exception as e:
        return "Could not analyze sentiment"

def extract_action_items(text):
    """Extract potential action items from text"""
    action_items = []
    
    # Keywords that often indicate action items
    action_patterns = [
        r"(?i)(we will|I will|will)\s+(.+?)(?:\.|$)",
        r"(?i)(need to|needs to)\s+(.+?)(?:\.|$)",
        r"(?i)(should|must)\s+(.+?)(?:\.|$)",
        r"(?i)(action item[s]?:|todo:|task:)\s*(.+?)(?:\.|$)",
        r"(?i)(follow up on|follow-up on)\s+(.+?)(?:\.|$)",
    ]
    
    sentences = text.split('.')
    
    for sentence in sentences:
        for pattern in action_patterns:
            matches = re.findall(pattern, sentence)
            for match in matches:
                # Get the action part (usually the second group)
                action = match[1] if len(match) > 1 else match[0]
                action = action.strip()
                
                # Filter out very short or very long items
                if 10 < len(action) < 200:
                    action_items.append(action.capitalize())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in action_items:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique_items.append(item)
    
    return unique_items[:5]  # Return top 5 items
