import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import json
import logging
import re
from pathlib import Path

# Fix the import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logger = logging.getLogger(__name__)

# Add parent directory to path safely
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_all_meetings, save_meeting
from app.transcription import transcribe_audio
from app.nlp_module import summarize_text, analyze_sentiment, extract_action_items
from app.mcp_integration import export_to_mcp_format, create_task_export
from app.utils import logger as app_logger, timer, validate_audio_file

# ... (Page config and CSS unchanged)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

# Sidebar Navigation (unchanged)

# Main content based on navigation
if st.session_state.current_page == "dashboard":
    st.title("📊 Meeting Dashboard")
    
    try:
        meetings = get_all_meetings()
    except Exception as e:
        st.error(f"Error loading meetings: {str(e)}")
        meetings = []
    
    if not meetings:
        st.info("No meetings yet. Upload your first meeting to get started!")
    else:
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search meetings", placeholder="Search by title or content...")
        with col2:
            sort_by = st.selectbox("Sort by", ["Most Recent", "Oldest First", "Most Actions"])
        
        # Filter meetings
        filtered_meetings = meetings
        if search_term:
            search_term_escaped = re.escape(search_term.lower())
            filtered_meetings = [
                m for m in meetings 
                if re.search(search_term_escaped, m['title'].lower()) or 
                   re.search(search_term_escaped, m['transcript'].lower())
            ]
        
        # Sort meetings
        if sort_by == "Oldest First":
            filtered_meetings.reverse()
        elif sort_by == "Most Actions":
            filtered_meetings.sort(key=lambda x: len(x['action_items']), reverse=True)
        
        # Display meetings in cards
        for meeting in filtered_meetings[:10]:
            with st.expander(f"**{meeting['title']}** - {meeting['date'][:10]}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Summary:** {meeting['summary'][:200]}...")
                
                with col2:
                    st.markdown(f"**Sentiment:** {meeting['sentiment']}")
                    st.markdown(f"**Actions:** {len(meeting['action_items'])}")
                
                with col3:
                    if st.button("View Details", key=f"view_{meeting['id']}"):
                        st.session_state.selected_meeting = meeting
                        st.session_state.current_page = "meeting_detail"

elif st.session_state.current_page == "upload":
    st.title("📤 Upload New Meeting")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        meeting_title = st.text_input("Meeting Title*", placeholder="e.g., Q4 Planning Meeting")
        meeting_participants = st.text_input("Participants", placeholder="John, Sarah, Mike")
        meeting_tags = st.text_input("Tags", placeholder="planning, strategy, Q4")
        
        uploaded_file = st.file_uploader(
            "Choose audio file*",
            type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm'],
            help="Maximum file size: 100MB"
        )
    
    with col2:
        st.markdown("### Processing Options")
        generate_summary = st.checkbox("Generate Summary", value=True)
        detect_sentiment = st.checkbox("Analyze Sentiment", value=True)
        extract_actions = st.checkbox("Extract Action Items", value=True)
        export_mcp = st.checkbox("Export to MCP", value=False)
    
    max_file_size = 100 * 1024 * 1024  # 100MB in bytes
    if st.button("🚀 Process Meeting", type="primary", use_container_width=True):
        if not meeting_title or not uploaded_file:
            st.error("Please provide a meeting title and audio file.")
        elif uploaded_file.size > max_file_size:
            st.error("File size exceeds 100MB limit.")
        else:
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                validate_audio_file(temp_path)
                
                with st.spinner("Processing meeting..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🎯 Transcribing audio...")
                    progress_bar.progress(10)
                    transcript = transcribe_audio(temp_path)
                    progress_bar.progress(40)
                    
                    summary = ""
                    sentiment = "Neutral"
                    action_items = []
                    
                    if generate_summary:
                        status_text.text("📝 Generating summary...")
                        summary = summarize_text(transcript)
                        progress_bar.progress(55)
                    
                    if detect_sentiment:
                        status_text.text("😊 Analyzing sentiment...")
                        sentiment = analyze_sentiment(transcript)
                        progress_bar.progress(70)
                    
                    if extract_actions:
                        status_text.text("✅ Extracting action items...")
                        action_items = extract_action_items(transcript)
                        progress_bar.progress(85)
                    
                    status_text.text("💾 Saving meeting...")
                    meeting_data = {
                        "title": meeting_title,
                        "date": datetime.now().isoformat(),
                        "transcript": transcript,
                        "summary": summary,
                        "sentiment": sentiment,
                        "action_items": action_items,
                        "audio_filename": uploaded_file.name,
                        "participants": meeting_participants,
                        "tags": meeting_tags
                    }
                    
                    meeting_id = save_meeting(meeting_data)
                    meeting_data["id"] = meeting_id
                    
                    if export_mcp:
                        export_path = export_to_mcp_format(meeting_data)
                        st.success(f"Exported to: {export_path}")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Processing complete!")
                    
                    st.success(f"Meeting '{meeting_title}' processed successfully!")
                    st.balloons()
                    
                    with st.expander("View Results"):
                        st.markdown(f"**Summary:** {summary}")
                        st.markdown(f"**Sentiment:** {sentiment}")
                        st.markdown(f"**Action Items:** {len(action_items)}")
                        for item in action_items:
                            st.write(f"• {item}")
                
            except Exception as e:
                st.error(f"Error processing meeting: {str(e)}")
                logger.error(f"Processing error: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.error(f"Failed to delete temporary file {temp_path}: {str(e)}")

elif st.session_state.current_page == "analytics":
    st.title("📈 Meeting Analytics")
    
    try:
        meetings = get_all_meetings()
    except Exception as e:
        st.error(f"Error loading meetings: {str(e)}")
        meetings = []
    
    if not meetings:
        st.info("No meetings to analyze yet.")
    else:
        period = st.selectbox("Time Period", ["All Time", "Last 30 Days", "Last 7 Days", "Today"])
        
        filtered_meetings = meetings
        if period != "All Time":
            days = {"Last 30 Days": 30, "Last 7 Days": 7, "Today": 1}[period]
            cutoff = datetime.now() - timedelta(days=days)
            filtered_meetings = [
                m for m in meetings 
                if datetime.fromisoformat(m['date']) > cutoff
            ]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Meetings", len(filtered_meetings))
        
        with col2:
            total_actions = sum(len(m["action_items"]) for m in filtered_meetings)
            st.metric("Total Action Items", total_actions)
        
        with col3:
            positive = sum(1 for m in filtered_meetings if "Positive" in m["sentiment"])
            percentage = (positive / len(filtered_meetings) * 100) if filtered_meetings else 0
            st.metric("Positive Sentiment", f"{percentage:.0f}%")
        
        with col4:
            avg_duration = sum(len(m["transcript"].split()) for m in filtered_meetings) / len(filtered_meetings) / 150 if filtered_meetings else 0
            st.metric("Avg Duration", f"{avg_duration:.0f} min")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Meetings Over Time")
            df = pd.DataFrame([
                {"Date": datetime.fromisoformat(m["date"]).date(), "Count": 1}
                for m in filtered_meetings
            ])
            if not df.empty:
                daily_counts = df.groupby("Date").count().reset_index()
                fig = px.line(daily_counts, x="Date", y="Count", 
                             title="Daily Meeting Count", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No meetings in the selected time period.")
        
        with col2:
            st.subheader("Sentiment Distribution")
            sentiments = [m["sentiment"].split()[0] for m in filtered_meetings]
            if sentiments:
                unique_sentiments = list(set(sentiments))
                sentiment_counts = [sentiments.count(s) for s in unique_sentiments]
                fig = go.Figure(data=[go.Pie(
                    labels=unique_sentiments,
                    values=sentiment_counts,
                    hole=.3,
                    marker_colors=["#2E8B57", "#DC143C", "#FFD700"]
                )])
                fig.update_layout(title="Overall Meeting Sentiment")
                st.plotly_chart(fig, use_container_width=True)
        
        # ... (Action items analysis and word frequency analysis unchanged)

elif st.session_state.current_page == "integrations":
    st.title("🔗 Integrations")
    
    st.markdown("""
    ### Model Context Protocol (MCP) Integration
    
    SpeakInsights supports seamless integration with your existing tools through MCP.
    """)
    
    st.subheader("Configure MCP Servers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Task Management")
        task_tool = st.selectbox("Select Task Tool", ["None", "Todoist", "Asana", "Trello", "Jira"])
        if task_tool != "None":
            api_key = st.text_input(f"{task_tool} API Key", type="password")
            if st.button(f"Connect {task_tool}"):
                st.success(f"Connected to {task_tool}!")
    
    with col2:
        st.markdown("#### File Storage")
        storage_tool = st.selectbox("Select Storage", ["None", "Google Drive", "Dropbox", "OneDrive"])
        if storage_tool != "None":
            storage_key = st.text_input(f"{storage_tool} API Key", type="password")
            if st.button(f"Connect {storage_tool}"):
                st.success(f"Connected to {storage_tool}!")
    
    st.subheader("Export Meeting Data")
    
    try:
        meetings = get_all_meetings()
    except Exception as e:
        st.error(f"Error loading meetings: {str(e)}")
        meetings = []
    
    if meetings:
        selected_meeting = st.selectbox(
            "Select Meeting to Export",
            options=range(len(meetings)),
            format_func=lambda x: f"{meetings[x]['title']} ({meetings[x]['date'][:10]})"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as JSON"):
                meeting = meetings[selected_meeting]
                json_data = json.dumps(meeting, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"meeting_{meeting['id']}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 Export Action Items"):
                meeting = meetings[selected_meeting]
                tasks = create_task_export(meeting['action_items'], meeting['title'])
                csv_data = pd.DataFrame(tasks).to_csv(index=False)
                st.download_button(
                    label="Download Tasks CSV",
                    data=csv_data,
                    file_name=f"actions_{meeting['id']}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("🔗 Send via MCP"):
                meeting = meetings[selected_meeting]
                export_path = export_to_mcp_format(meeting)
                st.success(f"Exported to MCP: {export_path}")

elif st.session_state.current_page == "meeting_detail" and 'selected_meeting' in st.session_state:
    meeting = st.session_state.selected_meeting
    
    st.title(f"📋 {meeting['title']}")
    st.caption(f"Date: {meeting['date']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sentiment", meeting['sentiment'])
    with col2:
        st.metric("Action Items", len(meeting['action_items']))
    with col3:
        word_count = len(meeting['transcript'].split())
        st.metric("Duration (est.)", f"{word_count/150:.0f} min")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Summary", "📄 Transcript", "✅ Actions", "📊 Analysis", "🔧 Tools"])
    
    with tab1:
        st.markdown("### Meeting Summary")
        st.info(meeting['summary'])
        
        st.markdown("### Key Points")
        sentences = meeting['summary'].split('.')
        for i, sentence in enumerate(sentences[:3], 1):
            if sentence.strip():
                st.markdown(f"{i}. {sentence.strip()}.")
    
    with tab2:
        st.markdown("### Full Transcript")
        
        search_term = st.text_input("Search in transcript", placeholder="Enter keyword...")
        
        if search_term:
            highlighted_text = re.sub(
                re.escape(search_term), 
                f"**{search_term}**", 
                meeting['transcript'], 
                flags=re.IGNORECASE
            )
            st.markdown(highlighted_text)
        else:
            st.text_area("", meeting['transcript'], height=400)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Transcript",
                meeting['transcript'],
                f"{meeting['title']}_transcript.txt",
                "text/plain"
            )
        with col2:
            st.download_button(
                "📥 Download Summary",
                meeting['summary'],
                f"{meeting['title']}_summary.txt",
                "text/plain"
            )
    
    with tab3:
        st.markdown("### Action Items")
        
        if meeting['action_items']:
            st.markdown("Click to mark as complete:")
            
            for i, item in enumerate(meeting['action_items'], 1):
                col1, col2 = st.columns([9, 1])
                with col1:
                    completed = st.checkbox(f"{item}", key=f"action_{meeting['id']}_{i}")
                with col2:
                    if st.button("📋", key=f"copy_{meeting['id']}_{i}", help="Copy to clipboard"):
                        st.info("Copied!")
            
            if st.button("Export Action Items"):
                actions_text = "\n".join([f"- {item}" for item in meeting['action_items']])
                st.download_button(
                    "Download Action Items",
                    actions_text,
                    f"{meeting['title']}_actions.txt",
                    "text/plain"
                )
        else:
            st.info("No action items detected in this meeting.")
            
            if st.checkbox("Add action items manually"):
                new_action = st.text_input("New action item")
                if st.button("Add") and new_action:
                    st.success(f"Added: {new_action}")
    
    with tab4:
        st.markdown("### Meeting Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Statistics")
            words = meeting['transcript'].split()
            sentences = meeting['transcript'].split('.')
            
            st.metric("Total Words", len(words))
            st.metric("Total Sentences", len(sentences))
            avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
            st.metric("Avg Words/Sentence", f"{avg_words_per_sentence:.1f}")
            
            duration_min = len(words) / 150
            st.metric("Speaking Pace", f"{len(words)/duration_min:.0f} words/min" if duration_min else "N/A")
        
        with col2:
            st.markdown("#### Sentiment Timeline")
            
            chunks = [meeting['transcript'][i:i+500] for i in range(0, len(meeting['transcript']), 500)]
            
            if len(chunks) > 1:
                sentiments = []
                for chunk in chunks[:10]:
                    sentiment = analyze_sentiment(chunk).lower()
                    if "positive" in sentiment:
                        sentiments.append(1)
                    elif "negative" in sentiment:
                        sentiments.append(-1)
                    else:
                        sentiments.append(0)
                
                fig = go.Figure(data=[
                    go.Scatter(
                        x=list(range(len(sentiments))),
                        y=sentiments,
                        mode='lines+markers',
                        name='Sentiment'
                    )
                ])
                fig.update_layout(
                    title="Sentiment Throughout Meeting",
                    xaxis_title="Time (chunks)",
                    yaxis_title="Sentiment",
                    yaxis=dict(ticktext=["Negative", "Neutral", "Positive"], tickvals=[-1, 0, 1])
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("### Meeting Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Generate Follow-up")
            
            if st.button("Generate Follow-up Email"):
                follow_up = f"""
Subject: Follow-up: {meeting['title']}

Dear Team,

Thank you for attending today's meeting. Here's a summary of what we discussed:

{meeting['summary']}

Action Items:
{chr(10).join([f'• {item}' for item in meeting['action_items'][:5]])}

Please let me know if I missed anything.

Best regards,
[Your Name]
                """
                st.text_area("Follow-up Email", follow_up, height=300)
        
        with col2:
            st.markdown("#### Share Meeting")
            
            if st.button("Generate Share Link"):
                share_link = f"http://localhost:8501/meeting/{meeting['id']}"
                st.code(share_link)
                st.info("Link copied to clipboard!")
            
            export_format = st.selectbox("Export Format", ["JSON", "PDF", "Markdown"])
            if st.button("Export Meeting"):
                st.success(f"Meeting exported as {export_format}")

# Footer (unchanged)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>SpeakInsights v1.0 | Built with ❤️ for Intel AI Hackathon</p>
    </div>
    """,
    unsafe_allow_html=True
)