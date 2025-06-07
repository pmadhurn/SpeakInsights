from transformers import pipeline

# Initialize pipelines (this will download models on first run)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")

def summarize_text(text, max_length=150):
    """Generate summary of the transcript"""
    try:
        # Split long text into chunks if needed
        max_chunk = 1024
        if len(text) > max_chunk:
            text = text[:max_chunk]
        
        summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error summarizing: {str(e)}"

def analyze_sentiment(text):
    """Analyze sentiment of the meeting"""
    try:
        # Take first 512 characters for sentiment analysis
        text_sample = text[:512]
        result = sentiment_analyzer(text_sample)
        return result[0]['label']
    except Exception as e:
        return "NEUTRAL"

def extract_action_items(text):
    """Simple action item extraction"""
    action_keywords = ['will', 'should', 'must', 'need to', 'have to', 'action:', 'todo:', 'task:']
    sentences = text.split('.')
    action_items = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if any(keyword in sentence_lower for keyword in action_keywords):
            action_items.append(sentence.strip())
    
    return action_items[:5]  # Return top 5 action items

