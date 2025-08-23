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

# System Status Check
col1, col2, col3 = st.columns(3)

with col1:
    # GPU Status
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            st.success(f"🚀 GPU Available: {gpu_name}")
        else:
            st.warning("⚠️ GPU not available - using CPU")
    except:
        st.info("ℹ️ GPU status unknown")

with col2:
    # WhisperX Status
    try:
        from app.transcription import check_whisperx_status
        whisperx_status = check_whisperx_status()
        
        if whisperx_status['available'] and whisperx_status['enabled']:
            model_info = whisperx_status['model_size']
            diarization = "🎭" if whisperx_status['diarization_enabled'] else ""
            vad = "🔊" if whisperx_status['vad_enabled'] else ""
            st.success(f"🎙️ WhisperX: {model_info} {diarization}{vad}")
        elif whisperx_status['available'] and not whisperx_status['enabled']:
            st.info("🎙️ WhisperX: Available (Disabled)")
        else:
            error_msg = whisperx_status.get('error', 'Unknown error')
            if 'numpy' in error_msg.lower() or 'numba' in error_msg.lower():
                st.warning("🎙️ WhisperX: NumPy Conflict")
            else:
                st.warning("🎙️ WhisperX: Not Available")
    except Exception as e:
        st.info("🎙️ WhisperX: Status unknown")

with col3:
    # Ollama Status
    try:
        from app.nlp_module import check_ollama_availability
        from config import config
        
        if config.USE_OLLAMA:
            ollama_available, status_msg = check_ollama_availability()
            if ollama_available:
                st.success(f"🦙 Ollama: {config.OLLAMA_MODEL}")
            else:
                st.warning(f"🦙 Ollama: {status_msg}")
        else:
            st.info("🦙 Ollama: Disabled")
    except:
        st.info("🦙 Ollama: Status unknown")

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
        
        # Step 1: Transcribe with WhisperX
        status_text.text("📝 Transcribing audio with WhisperX...")
        progress_bar.progress(25)
        
        # Import enhanced transcription functions
        from app.transcription import transcribe_audio, get_transcript_text, get_formatted_transcript, get_transcription_metadata
        
        transcription_result = transcribe_audio(tmp_file_path)
        transcript = get_transcript_text(transcription_result)
        formatted_transcript = get_formatted_transcript(transcription_result)
        transcription_metadata = get_transcription_metadata(transcription_result)
        
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
        
        # Save meeting data to database with WhisperX enhancements
        meeting_data = {
            "title": meeting_title,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": transcript,
            "formatted_transcript": formatted_transcript,
            "summary": summary,
            "sentiment": sentiment,
            "action_items": action_items,
            "audio_filename": uploaded_file.name,
            "transcription_metadata": transcription_metadata,
            "speaker_segments": transcription_result.get('speaker_segments', []) if isinstance(transcription_result, dict) else []
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
        
        # Display meeting details with WhisperX enhancements
        metadata = meeting.get("transcription_metadata", {})
        has_speakers = metadata.get("has_speakers", False)
        
        if has_speakers:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Date", meeting["date"])
            with col2:
                st.metric("Speakers", metadata.get("total_speakers", 0))
            with col3:
                st.metric("Sentiment", meeting["sentiment"])
            with col4:
                st.metric("Action Items", len(meeting["action_items"]))
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date", meeting["date"])
            with col2:
                st.metric("Sentiment", meeting["sentiment"])
            with col3:
                st.metric("Action Items", len(meeting["action_items"]))
        
        # Tabs for different views - add Speaker Analysis if speakers detected
        if has_speakers:
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Summary", "📝 Full Transcript", "🎭 Speaker Analysis", "✅ Action Items", "📊 Analytics", "⚙️ Settings"])
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "📝 Full Transcript", "✅ Action Items", "📊 Analytics", "⚙️ Settings"])
        
        with tab1:
            st.subheader("Meeting Summary")
            
            # Add regenerate summary button
            col1, col2 = st.columns([4, 1])
            with col1:
                st.info(meeting["summary"])
            with col2:
                if st.button("🔄 Regenerate Summary", key=f"regen_{meeting['id']}", help="Generate a new summary from the transcript"):
                    with st.spinner("Regenerating summary..."):
                        try:
                            # Import the function directly
                            from app.nlp_module import summarize_text
                            from app.database import update_meeting_summary
                            
                            # Generate new summary
                            new_summary = summarize_text(meeting["transcript"])
                            
                            # Update in database
                            update_meeting_summary(meeting["id"], new_summary)
                            
                            st.success("✅ Summary regenerated successfully!")
                            st.info("🔄 Please refresh the page to see the updated summary.")
                            
                            # Show the new summary immediately
                            st.subheader("New Summary:")
                            st.success(new_summary)
                            
                        except Exception as e:
                            st.error(f"❌ Failed to regenerate summary: {str(e)}")
            
        with tab2:
            st.subheader("Full Transcript")
            
            # Show formatted transcript if available (with speakers)
            transcript_to_show = meeting.get("formatted_transcript", meeting["transcript"])
            if transcript_to_show != meeting["transcript"] and has_speakers:
                st.info("📢 Showing transcript with speaker labels")
                st.text_area("", transcript_to_show, height=400, key="formatted_transcript")
                
                # Toggle to show plain transcript
                if st.checkbox("Show plain transcript (no speaker labels)"):
                    st.text_area("Plain Transcript", meeting["transcript"], height=300, key="plain_transcript")
            else:
                st.text_area("", meeting["transcript"], height=400, key="basic_transcript")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Transcript",
                    data=meeting["transcript"],
                    file_name=f"{meeting['title']}_transcript.txt",
                    mime="text/plain"
                )
            
            if has_speakers and transcript_to_show != meeting["transcript"]:
                with col2:
                    st.download_button(
                        label="📥 Download with Speakers",
                        data=transcript_to_show,
                        file_name=f"{meeting['title']}_transcript_with_speakers.txt",
                        mime="text/plain"
                    )
        
        # Speaker Analysis Tab (only if speakers detected)
        if has_speakers:
            with tab3:
                st.subheader("🎭 Speaker Analysis")
                
                speaker_segments = meeting.get("speaker_segments", [])
                speakers = metadata.get("speakers", [])
                
                if speaker_segments and speakers:
                    # Speaker statistics
                    st.subheader("Speaker Statistics")
                    
                    speaker_stats = {}
                    for segment in speaker_segments:
                        speaker = segment.get("speaker", "Unknown")
                        text = segment.get("text", "")
                        duration = segment.get("end", 0) - segment.get("start", 0)
                        
                        if speaker not in speaker_stats:
                            speaker_stats[speaker] = {
                                "word_count": 0,
                                "total_duration": 0,
                                "segments": 0
                            }
                        
                        speaker_stats[speaker]["word_count"] += len(text.split())
                        speaker_stats[speaker]["total_duration"] += duration
                        speaker_stats[speaker]["segments"] += 1
                    
                    # Display speaker stats
                    cols = st.columns(len(speakers))
                    for i, speaker in enumerate(speakers):
                        with cols[i]:
                            stats = speaker_stats.get(speaker, {})
                            st.metric(
                                f"🎤 {speaker}",
                                f"{stats.get('word_count', 0)} words",
                                f"{stats.get('segments', 0)} segments"
                            )
                    
                    # Speaker timeline
                    st.subheader("Speaker Timeline")
                    
                    # Create timeline visualization
                    timeline_data = []
                    for segment in speaker_segments:
                        timeline_data.append({
                            "Speaker": segment.get("speaker", "Unknown"),
                            "Start": segment.get("start", 0),
                            "End": segment.get("end", 0),
                            "Duration": segment.get("end", 0) - segment.get("start", 0),
                            "Text": segment.get("text", "")[:100] + "..." if len(segment.get("text", "")) > 100 else segment.get("text", "")
                        })
                    
                    if timeline_data:
                        import pandas as pd
                        df = pd.DataFrame(timeline_data)
                        
                        # Show timeline as a bar chart
                        fig = px.timeline(
                            df, 
                            x_start="Start", 
                            x_end="End", 
                            y="Speaker", 
                            color="Speaker",
                            title="Speaker Timeline",
                            hover_data=["Text"]
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show detailed segments
                        st.subheader("Detailed Speaker Segments")
                        
                        selected_speaker = st.selectbox(
                            "Filter by speaker:",
                            ["All"] + speakers,
                            key="speaker_filter"
                        )
                        
                        filtered_segments = speaker_segments
                        if selected_speaker != "All":
                            filtered_segments = [s for s in speaker_segments if s.get("speaker") == selected_speaker]
                        
                        for i, segment in enumerate(filtered_segments[:20]):  # Limit to first 20 segments
                            with st.expander(f"{segment.get('speaker', 'Unknown')} - {segment.get('start', 0):.1f}s to {segment.get('end', 0):.1f}s"):
                                st.write(segment.get('text', ''))
                        
                        if len(filtered_segments) > 20:
                            st.info(f"Showing first 20 of {len(filtered_segments)} segments")
                
                else:
                    st.info("No detailed speaker information available for this meeting.")
            
            # Adjust tab numbering for remaining tabs
            action_tab = tab4
            analytics_tab = tab5
            settings_tab = tab6
        else:
            # No speaker analysis tab
            action_tab = tab3
            analytics_tab = tab4
            settings_tab = tab5
            
        with action_tab:
            st.subheader("Action Items")
            
            # Add regenerate action items button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if meeting["action_items"]:
                    for i, item in enumerate(meeting["action_items"], 1):
                        st.checkbox(f"{i}. {item}", key=f"action_{meeting['id']}_{i}")
                else:
                    st.write("No action items detected in this meeting.")
            
            with col2:
                if st.button("🔄 Regenerate Tasks", key=f"regen_tasks_{meeting['id']}", help="Extract new action items from the transcript"):
                    with st.spinner("Regenerating action items..."):
                        try:
                            # Import the function directly
                            from app.nlp_module import extract_action_items
                            from app.database import update_meeting_action_items
                            
                            # Generate new action items
                            new_action_items = extract_action_items(meeting["transcript"])
                            
                            # Update in database
                            update_meeting_action_items(meeting["id"], new_action_items)
                            
                            st.success("✅ Action items regenerated successfully!")
                            st.info("🔄 Please refresh the page to see the updated action items.")
                            
                            # Show the new action items immediately
                            if new_action_items:
                                st.subheader("New Action Items:")
                                for i, item in enumerate(new_action_items, 1):
                                    st.success(f"{i}. {item}")
                            else:
                                st.info("No action items found in the transcript.")
                            
                        except Exception as e:
                            st.error(f"❌ Failed to regenerate action items: {str(e)}")
                
        with analytics_tab:
            st.subheader("Meeting Analytics")
            
            # Word count
            word_count = len(meeting["transcript"].split())
            st.metric("Total Words", f"{word_count:,}")
            
            # Estimated duration (rough estimate: 150 words per minute)
            est_duration = word_count / 150
            st.metric("Estimated Duration", f"{est_duration:.1f} minutes")
            
            # Show actual duration if available from WhisperX
            actual_duration = metadata.get("duration", 0)
            if actual_duration > 0:
                st.metric("Actual Duration", f"{actual_duration/60:.1f} minutes")
            
            # Transcription method info
            method = metadata.get("method", "unknown")
            if method == "whisperx":
                st.success("🎙️ Enhanced transcription with WhisperX")
                if has_speakers:
                    st.info(f"🎭 {len(speakers)} speakers detected")
            else:
                st.info("🎙️ Basic Whisper transcription")
            
            # Sentiment indicator
            if "Positive" in meeting["sentiment"]:
                st.success(f"Meeting Sentiment: {meeting['sentiment']}")
            else:
                st.warning(f"Meeting Sentiment: {meeting['sentiment']}")
        
        with settings_tab:
            # WhisperX Settings Section
            st.subheader("🎙️ WhisperX Settings")
            
            try:
                from app.transcription import check_whisperx_status
                whisperx_status = check_whisperx_status()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Status:** {'✅ Available' if whisperx_status['available'] else '❌ Not Available'}")
                    st.info(f"**Enabled:** {'Yes' if whisperx_status['enabled'] else 'No'}")
                    st.info(f"**Model:** {whisperx_status['model_size']}")
                    st.info(f"**Device:** {whisperx_status['device']}")
                
                with col2:
                    st.info(f"**VAD Filtering:** {'✅ Enabled' if whisperx_status['vad_enabled'] else '❌ Disabled'}")
                    st.info(f"**Speaker Diarization:** {'✅ Enabled' if whisperx_status['diarization_enabled'] else '❌ Disabled'}")
                    st.info(f"**HF Token:** {'✅ Configured' if whisperx_status['hf_token_configured'] else '❌ Not Set'}")
                
                # Test WhisperX
                if st.button("🧪 Test WhisperX"):
                    if not whisperx_status['available']:
                        error_msg = whisperx_status.get('error', 'Unknown error')
                        
                        if 'numpy' in error_msg.lower() or 'numba' in error_msg.lower():
                            st.error("❌ WhisperX unavailable due to NumPy version conflict")
                            st.info("💡 WhisperX requires NumPy >= 2.0, but Streamlit requires NumPy < 2.0")
                            st.info("🔧 See WHISPERX_COMPATIBILITY.md for solutions")
                        else:
                            st.error(f"❌ WhisperX not available: {error_msg}")
                            st.info("💡 Install with: pip install whisperx (in separate environment)")
                    else:
                        st.info("🎙️ WhisperX is available and ready to use!")
                        
                        if not whisperx_status['hf_token_configured']:
                            st.warning("⚠️ No Hugging Face token configured. Speaker diarization will be disabled.")
                            st.info("💡 Get a token from https://huggingface.co/settings/tokens and add it to config.json")
                
                # WhisperX Setup Instructions
                st.subheader("📖 WhisperX Setup Instructions")
                st.markdown("""
                **⚠️ COMPATIBILITY ISSUE:**
                
                WhisperX has a dependency conflict with Streamlit:
                - WhisperX requires NumPy >= 2.0
                - Streamlit requires NumPy < 2.0
                
                **Solutions:**
                
                1. **Separate Environment (Recommended):**
                ```bash
                # Create WhisperX environment
                python -m venv whisperx_env
                whisperx_env\\Scripts\\activate
                pip install whisperx pyannote.audio
                
                # Use CLI for processing
                python whisperx_cli.py audio.mp3 -o ./output
                ```
                
                2. **Current Setup (Standard Whisper):**
                - ✅ Basic transcription works
                - ❌ No speaker diarization
                - ❌ No word-level timestamps
                
                3. **See WHISPERX_COMPATIBILITY.md** for detailed solutions
                
                **WhisperX Features (when available):**
                - ✅ **70× faster** than standard Whisper on GPU
                - ✅ **Word-level timestamps** with precise alignment
                - ✅ **VAD preprocessing** for better accuracy
                - ✅ **Speaker diarization** (who said what)
                - ✅ **Multiple speaker detection**
                - ✅ **Enhanced accuracy** for long-form audio
                """)
                
                # Model recommendations
                st.subheader("🎯 Recommended Models")
                st.markdown("""
                - **large-v2** - Best accuracy, slower processing
                - **medium** - Good balance of speed and accuracy
                - **small** - Faster processing, lower accuracy
                - **base** - Fastest, basic accuracy
                """)
                
            except Exception as e:
                st.error(f"❌ Error loading WhisperX status: {e}")
            
            st.divider()
            
            st.subheader("⚙️ Ollama Settings")
            
            from config import config
            
            # Display current settings
            st.info(f"**Current Model:** {config.OLLAMA_MODEL}")
            st.info(f"**Ollama URL:** {config.OLLAMA_BASE_URL}")
            st.info(f"**Enabled:** {'Yes' if config.USE_OLLAMA else 'No'}")
            
            # Test Ollama connection
            if st.button("🧪 Test Ollama Connection"):
                with st.spinner("Testing Ollama..."):
                    try:
                        from app.nlp_module import check_ollama_availability
                        available, msg = check_ollama_availability()
                        
                        if available:
                            st.success(f"✅ {msg}")
                            
                            # Test summarization
                            st.info("Testing summarization...")
                            test_text = "This is a test meeting about project updates and budget discussions."
                            
                            from app.nlp_module import summarize_with_ollama
                            summary = summarize_with_ollama(test_text)
                            st.success("✅ Summarization test successful!")
                            st.write(f"**Test Summary:** {summary}")
                            
                        else:
                            st.error(f"❌ {msg}")
                            st.info("💡 Make sure Ollama is running and the model is installed:")
                            st.code(f"ollama serve\nollama pull {config.OLLAMA_MODEL}")
                            
                    except Exception as e:
                        st.error(f"❌ Test failed: {str(e)}")
            
            # Instructions
            st.subheader("📖 Setup Instructions")
            st.markdown("""
            **To use Ollama for better summaries:**
            
            1. **Install Ollama:** Download from [ollama.ai](https://ollama.ai)
            2. **Start Ollama:** Run `ollama serve` in terminal
            3. **Install a model:** Run `ollama pull llama3.2` (or your preferred model)
            4. **Update config.json** if needed to change model or URL
            
            **Benefits of using Ollama:**
            - ✅ No text length limits (handles full transcripts)
            - ✅ Better quality summaries
            - ✅ Runs locally (private)
            - ✅ Multiple model options
            """)
            
            # Model recommendations
            st.subheader("🎯 Recommended Models")
            st.markdown("""
            - **llama3.2** (3B) - Fast, good quality
            - **llama3.1** (8B) - Better quality, slower
            - **mistral** (7B) - Good balance
            - **qwen2.5** (7B) - Excellent for summaries
            """)
            
            if st.button("🔄 Reload Configuration"):
                st.rerun()
            
            # Webhook Settings Section
            st.subheader("🔗 Webhook Settings (n8n Integration)")
            
            # Load current webhook config
            try:
                import requests
                response = requests.get("http://localhost:8000/api/webhook/config", timeout=5)
                if response.status_code == 200:
                    webhook_config = response.json()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Status:** {'✅ Enabled' if webhook_config.get('enabled') else '❌ Disabled'}")
                        st.info(f"**Send Action Items:** {'Yes' if webhook_config.get('send_action_items') else 'No'}")
                        st.info(f"**Send Summaries:** {'Yes' if webhook_config.get('send_summaries') else 'No'}")
                    
                    with col2:
                        st.info(f"**Webhook URL:** {'✅ Configured' if webhook_config.get('webhook_url_configured') else '❌ Not Set'}")
                        st.info(f"**Timeout:** {webhook_config.get('timeout', 30)}s")
                        st.info(f"**Retry Attempts:** {webhook_config.get('retry_attempts', 3)}")
                    
                    # Test webhook button
                    if st.button("🧪 Test Webhook Connection"):
                        if not webhook_config.get('webhook_url_configured'):
                            st.error("❌ Please configure webhook URL in config.json first")
                        else:
                            with st.spinner("Testing webhook..."):
                                try:
                                    test_response = requests.post("http://localhost:8000/api/webhook/test", timeout=10)
                                    if test_response.status_code == 200:
                                        result = test_response.json()
                                        if result.get('status') == 'connected':
                                            st.success("✅ Webhook test successful!")
                                        else:
                                            st.error("❌ Webhook test failed")
                                    else:
                                        st.error(f"❌ Test failed: {test_response.status_code}")
                                except Exception as e:
                                    st.error(f"❌ Test failed: {str(e)}")
                    
                else:
                    st.error("❌ Could not load webhook configuration")
                    
            except Exception as e:
                st.warning("⚠️ API server not running - webhook config unavailable")
            
            # Webhook setup instructions
            st.subheader("📖 Webhook Setup Instructions")
            st.markdown("""
            **To integrate with n8n:**
            
            1. **Create n8n workflow** with a Webhook trigger node
            2. **Copy the webhook URL** from n8n
            3. **Update config.json** with your webhook settings:
            
            ```json
            "webhook_settings": {
                "enabled": true,
                "n8n_webhook_url": "https://your-n8n-instance.com/webhook/your-webhook-id",
                "send_action_items": true,
                "send_summaries": false
            }
            ```
            
            4. **Restart the application** to apply changes
            5. **Test the connection** using the button above
            
            **Webhook Payload Format:**
            - `type`: "action_items" or "summary"
            - `meeting_id`: Unique meeting identifier
            - `action_items`: Array of action items (for action_items type)
            - `summary`: Meeting summary text (for summary type)
            - `timestamp`: ISO timestamp
            - `meeting_metadata`: Additional meeting info (optional)
            """)
            
            st.info("💡 **Tip:** You can configure n8n to send action items to email, Discord, Slack, or any other service!")
            
            if st.button("🔄 Reload Webhook Configuration"):
                st.rerun()

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