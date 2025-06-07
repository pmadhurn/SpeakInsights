"""
Optimization utilities for better performance
"""
import os
import torch
import whisper
from transformers import pipeline

class OptimizedModels:
    """Singleton class for model management"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def initialize(self):
        if not self.initialized:
            print("Loading optimized models...")
            
            # Use CPU-optimized settings
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load smaller models for speed
            self.whisper_model = whisper.load_model("tiny", device=device)
            
            # Use distilled models
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-xsum-1-1",
                device=0 if device == "cuda" else -1
            )
            
            self.sentiment = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if device == "cuda" else -1
            )
            
            self.initialized = True
            print("Models loaded successfully!")
    
    def transcribe(self, audio_path):
        """Optimized transcription"""
        result = self.whisper_model.transcribe(
            audio_path,
            language="en",
            fp16=False,
            verbose=False
        )
        return result["text"]
    
    def summarize(self, text, max_length=100):
        """Optimized summarization"""
        # Chunk text if too long
        max_chunk = 512
        if len(text) > max_chunk:
            text = text[:max_chunk]
        
        summary = self.summarizer(
            text,
            max_length=max_length,
            min_length=30,
            do_sample=False,
            early_stopping=True,
            num_beams=2  # Reduced for speed
        )
        return summary[0]['summary_text']

# Global instance
models = OptimizedModels()