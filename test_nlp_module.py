import sys
# Add the parent directory to sys.path to allow importing app.nlp_module
# This assumes the script is run from the root of the repository where 'app' is a subdirectory.
sys.path.insert(0, '.')

try:
    from app.nlp_module import analyze_sentiment, sentiment_analyzer

    # Ensure the model downloads by explicitly initializing (if not already done by module import)
    # This line might trigger the download if the sentiment_analyzer is lazily loaded
    # or if the script execution context is fresh.
    if sentiment_analyzer:
         print("Sentiment analyzer pipeline object exists.")

    print("Successfully imported analyze_sentiment.")

    test_texts = [
        "I am feeling overjoyed and thankful for this wonderful opportunity!",
        "This is really frustrating and makes me quite angry.",
        "I'm not sure what to think about this, it's a bit confusing.",
        "This meeting was okay, nothing particularly special.",
        "We need to approach this with caution and be mindful of the risks."
    ]

    for i, text in enumerate(test_texts):
        print(f"--- Testing text {i+1} ---")
        print(f"Input: {text}")
        sentiment_output = analyze_sentiment(text)
        print(f"Output: {sentiment_output}")
        print("-------------------------")

except ImportError as e:
    print(f"ImportError: {e}. Check if app.nlp_module is accessible and dependencies are met.")
    # If the error is about a missing dependency that should be in requirements.txt,
    # try to install it. This is a fallback, as disk space is an issue.
    if "No module named 'transformers'" in str(e) or "No module named 'torch'" in str(e):
        print("Attempting to install missing core NLP libraries...")
        import subprocess
        try:
            subprocess.run(["pip", "install", "transformers", "torch"], check=True)
            print("Re-attempting import after installation...")
            from app.nlp_module import analyze_sentiment
            # Re-run a single test if re-import succeeds
            sentiment_output = analyze_sentiment(test_texts[0])
            print(f"Output after re-install: {sentiment_output}")
        except Exception as install_e:
            print(f"Failed to install libraries or re-run: {install_e}")
    elif "No module named 'nltk'" in str(e):
         print("Attempting to install NLTK...")
         import subprocess
         try:
             subprocess.run(["pip", "install", "nltk"], check=True)
             print("NLTK installed. Please ensure NLTK data (punkt, stopwords) is downloaded by the module.")
             # NLTK data download is handled in nlp_module.py itself.
         except Exception as install_e:
             print(f"Failed to install NLTK: {install_e}")


except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # This might catch errors during pipeline initialization (e.g. model download failure)
    if "HTTPSConnectionPool" in str(e) or "Connection error" in str(e):
        print("This might be a network issue or a problem reaching Hugging Face Hub.")
    if "enough space" in str(e).lower() or "errno 28" in str(e).lower():
         print("This is likely a disk space issue, similar to previous attempts.")
