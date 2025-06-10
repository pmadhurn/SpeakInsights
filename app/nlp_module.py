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
sentiment_analyzer = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

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
    try:
        sample = text[:512] # Keep sampling for performance
        raw_results = sentiment_analyzer(sample)

        professional_sentiments_list = [
            'admiration', 'amusement', 'approval', 'excitement', 'gratitude',
            'joy', 'love', 'optimism', 'pride', 'relief', 'anger',
            'annoyance', 'disappointment', 'disapproval', 'disgust',
            'fear', 'sadness', 'remorse', 'embarrassment', 'nervousness',
            'confusion', 'curiosity', 'neutral', 'surprise'
        ]

        # The pipeline with top_k=None returns a list containing a list of dicts
        # e.g. [[{'label': '...', 'score': ...}, {'label': '...', 'score': ...}]]
        if not raw_results or not raw_results[0]:
            return "Could not analyze sentiment (empty model output)"

        processed_sentiments = []
        for result in raw_results[0]: # Access the inner list of sentiment dicts
            if result['label'] in professional_sentiments_list and result['score'] > 0.3:
                processed_sentiments.append(result)
        
        # Sort by score
        processed_sentiments.sort(key=lambda x: x['score'], reverse=True)
        
        top_sentiments = processed_sentiments[:3]

        if not top_sentiments:
            # Check if 'neutral' was high scoring but below 0.3 for professional list,
            # or simply return a default neutral message.
            # For simplicity, let's find the raw neutral score if no other professional sentiment is strong.
            neutral_score_info = next((item for item in raw_results[0] if item['label'] == 'neutral'), None)
            if neutral_score_info and neutral_score_info['score'] > 0.5: # Default threshold for general neutral
                 return f"Neutral ({neutral_score_info['score']:.2%})"
            return "No strong specific emotions detected"

        sentiment_strings = [f"{s['label'].capitalize()} ({s['score']:.0%})" for s in top_sentiments]
        return "Top emotions: " + ", ".join(sentiment_strings)
            
    except Exception as e:
        # Log the exception e for debugging
        print(f"Error in analyze_sentiment: {str(e)}")
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
