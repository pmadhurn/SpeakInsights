import streamlit as st
import sys
import os
import tempfile
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Fix the import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.transcription import transcribe_audio
from app.nlp_module import summarize_text, analyze_sentiment, extract_action_items
from app.database import save_meeting, get_all_meetings, get_meeting_by_id

st.set_page_config(page_title="SpeakInsights", page_icon="🎙️", layout="wide")

# Load meetings from database without aggressive caching
def load_meetings():
    try:
        meetings = get_all_meetings()
        return meetings
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

st.title("🎙️ SpeakInsights - AI Meeting Assistant")

# Add refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh", help="Reload meetings from database"):
        st.rerun()

# GPU Status Check
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        st.success(f"🚀 GPU Available: {gpu_name}")
    else:
        st.warning("⚠️ GPU not available - using CPU (slower processing)")
except:
    st.info("ℹ️ GPU status unknown")

# Sidebar for new meeting upload
with st.sidebar:
    st.header("📤 Upload New Meeting")
    
    meeting_title = st.text_input("Meeting Title", placeholder="e.g., Weekly Team Standup")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm']
    )
    
    if st.button("Process Meeting", type="primary") and uploaded_file and meeting_title:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Transcribe
        status_text.text("📝 Transcribing audio...")
        progress_bar.progress(25)
        transcript = transcribe_audio(tmp_file_path)
        
        # Step 2: Generate summary
        status_text.text("🧠 Generating summary...")
        progress_bar.progress(50)
        summary = summarize_text(transcript)
        
        # Step 3: Analyze sentiment
        status_text.text("😊 Analyzing sentiment...")
        progress_bar.progress(75)
        sentiment = analyze_sentiment(transcript)
        
        # Step 4: Extract action items
        status_text.text("✅ Extracting action items...")
        progress_bar.progress(90)
        action_items = extract_action_items(transcript)
        
        # Complete
        status_text.text("🎉 Processing complete!")
        progress_bar.progress(100)
        
        # Save meeting data to database
        meeting_data = {
            "title": meeting_title,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": transcript,
            "summary": summary,
            "sentiment": sentiment,
            "action_items": action_items,
            "audio_filename": uploaded_file.name
        }
        
        # Save to database
        try:
            meeting_id = save_meeting(meeting_data)
            st.success(f"✅ Meeting saved to database with ID: {meeting_id}")
            st.success("✅ Meeting processed successfully!")
            # Force refresh to show new data
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Database error: {e}")
        
        # Clean up temp file
        os.unlink(tmp_file_path)

# Main content area - Load meetings from database
meetings = load_meetings()

if len(meetings) == 0:
    st.info("👋 Welcome! Upload your first meeting recording using the sidebar.")
    st.info("💾 Your meetings will be stored in the persistent PostgreSQL database.")
else:
    # Meeting selector
    st.header("📊 Meeting Dashboard")
    st.info(f"📈 Found {len(meetings)} meetings in database")
    
    meeting_titles = [f"{m['title']} ({m['date']})" for m in meetings]
    selected_idx = st.selectbox("Select a meeting:", range(len(meeting_titles)), 
                                format_func=lambda x: meeting_titles[x])
    
    if selected_idx is not None:
        meeting = meetings[selected_idx]
        
        # Display meeting details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Date", meeting["date"])
        with col2:
            st.metric("Sentiment", meeting["sentiment"])
        with col3:
            st.metric("Action Items", len(meeting["action_items"]))
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📝 Full Transcript", "✅ Action Items", "📊 Analytics"])
        
        with tab1:
            st.subheader("Meeting Summary")
            st.info(meeting["summary"])
            
        with tab2:
            st.subheader("Full Transcript")
            st.text_area("", meeting["transcript"], height=400)
            
            # Download button
            st.download_button(
                label="📥 Download Transcript",
                data=meeting["transcript"],
                file_name=f"{meeting['title']}_transcript.txt",
                mime="text/plain"
            )
            
        with tab3:
            st.subheader("Action Items")
            if meeting["action_items"]:
                for i, item in enumerate(meeting["action_items"], 1):
                    st.checkbox(f"{i}. {item}", key=f"action_{meeting['id']}_{i}")
            else:
                st.write("No action items detected in this meeting.")
                
        with tab4:
            st.subheader("Meeting Analytics")
            
            # Word count
            word_count = len(meeting["transcript"].split())
            st.metric("Total Words", f"{word_count:,}")
            
            # Estimated duration (rough estimate: 150 words per minute)
            est_duration = word_count / 150
            st.metric("Estimated Duration", f"{est_duration:.1f} minutes")
            
            # Sentiment indicator
            if "Positive" in meeting["sentiment"]:
                st.success(f"Meeting Sentiment: {meeting['sentiment']}")
            else:
                st.warning(f"Meeting Sentiment: {meeting['sentiment']}")

def create_analytics_dashboard(meetings):
    """Create analytics visualizations"""
    if not meetings:
        return
    
    st.header("📈 Meeting Analytics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Meetings", len(meetings))
    
    with col2:
        total_actions = sum(len(m["action_items"]) for m in meetings)
        st.metric("Total Action Items", total_actions)
    
    with col3:
        positive_meetings = sum(1 for m in meetings if "Positive" in m["sentiment"])
        st.metric("Positive Meetings", f"{positive_meetings}/{len(meetings)}")
    
    with col4:
        avg_actions = total_actions / len(meetings) if meetings else 0
        st.metric("Avg Actions/Meeting", f"{avg_actions:.1f}")
    
    # Sentiment distribution
    st.subheader("Sentiment Distribution")
    sentiments = [m["sentiment"].split()[0] for m in meetings]
    fig = px.pie(values=[sentiments.count("Positive"), sentiments.count("Negative")], 
                 names=["Positive", "Negative"],
                 color_discrete_map={"Positive": "#2E8B57", "Negative": "#DC143C"})
    st.plotly_chart(fig) 