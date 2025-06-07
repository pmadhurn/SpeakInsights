"""
Emergency demo mode - works even if models fail to load
"""
import streamlit as st
import json
from datetime import datetime, timedelta
import random

# Predefined demo data
DEMO_MEETINGS = [
    {
        "id": 1,
        "title": "Q4 Strategic Planning Session",
        "date": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "duration": "45 minutes",
        "participants": "John, Sarah, Mike, Lisa",
        "transcript": """Welcome everyone to our Q4 planning session. I'm excited to share 
        that we've exceeded our Q3 targets by 15%. For Q4, we need to focus on three 
        main areas: expanding our market presence, launching the new product feature, 
        and improving customer retention. John will lead the marketing expansion, 
        Sarah will handle the product launch, and Mike will work on retention strategies. 
        We should aim to increase revenue by 20% this quarter. Let's schedule weekly 
        check-ins to track progress. Any questions?""",
        
        "summary": "Q3 exceeded targets by 15%. Q4 focus: market expansion (John), 
        product launch (Sarah), customer retention (Mike). Goal: 20% revenue increase. 
        Weekly progress check-ins scheduled.",
        
        "sentiment": "Positive (92% confidence)",
        
        "action_items": [
            "John will lead the marketing expansion initiative",
            "Sarah will handle the new product feature launch",
            "Mike will develop customer retention strategies",
            "Schedule weekly check-ins to track progress",
            "Aim to increase revenue by 20% in Q4"
        ],
        
        "key_metrics": {
            "word_count": 92,
            "speaking_pace": "122 words/min",
            "questions_asked": 1,
            "decisions_made": 4
        }
    },
    {
        "id": 2,
        "title": "Daily Engineering Standup",
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
        "duration": "15 minutes",
        "participants": "Dev Team",
        "transcript": """Good morning team. Let's do our standup. I'll start - yesterday 
        I fixed the login bug and started working on the API optimization. Today I'll 
        complete the API work. I'm blocked on database access permissions. Sarah, you're next. 
        Thanks John. I completed the UI redesign for the dashboard. Today I'm implementing 
        the new charts. No blockers. Mike? I investigated the performance issues. Found 
        memory leaks in the caching system. I'll push the fix today. Need code review from John.""",
        
        "summary": "Engineering standup: John fixed login bug, working on API optimization, 
        blocked on DB permissions. Sarah completed UI redesign, implementing charts. 
        Mike found memory leaks in caching, needs code review.",
        
        "sentiment": "Neutral (78% confidence)",
        
                "action_items": [
            "John will complete API optimization work",
            "Resolve database access permissions for John",
            "Sarah will implement new dashboard charts",
            "Mike will push caching system fix",
            "John needs to review Mike's code"
        ],
        
        "key_metrics": {
            "word_count": 76,
            "speaking_pace": "152 words/min",
            "blockers_mentioned": 2,
            "tasks_completed": 3
        }
    },
    {
        "id": 3,
        "title": "Customer Feedback Review",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": "30 minutes",
        "participants": "Product Team",
        "transcript": """Let's review this week's customer feedback. We received mixed 
        responses about the new feature. 60% love the functionality but find it complex. 
        Several users requested better documentation. The mobile app crashes are our 
        biggest concern - 15 reports this week. Customer satisfaction dropped to 72%. 
        We must address these issues urgently. I suggest we simplify the UI, create 
        video tutorials, and fix the mobile crashes as priority one.""",
        
        "summary": "Customer feedback: 60% like new feature but find it complex. 
        Documentation needs improvement. Mobile app crashes (15 reports) are critical. 
        Customer satisfaction at 72%. Priority: simplify UI, create tutorials, fix crashes.",
        
        "sentiment": "Negative (65% confidence)",
        
        "action_items": [
            "Simplify the UI for the new feature",
            "Create video tutorials for better documentation",
            "Fix mobile app crashes as priority one",
            "Improve customer satisfaction from 72%",
            "Address complexity concerns in the new feature"
        ],
        
        "key_metrics": {
            "word_count": 68,
            "speaking_pace": "136 words/min",
            "issues_raised": 4,
            "satisfaction_score": "72%"
        }
    }
]

def run_emergency_demo():
    """Run the emergency demo interface"""
    st.set_page_config(page_title="SpeakInsights Demo", page_icon="🎙️", layout="wide")
    
    st.title("🎙️ SpeakInsights - Emergency Demo Mode")
    st.warning("Running in demo mode with pre-loaded data")
    
    # Sidebar
    with st.sidebar:
        st.header("Demo Controls")
        
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()
        
        st.markdown("---")
        st.info("""
        This is a failsafe demo mode that works without AI models.
        Perfect for presentations when live processing isn't available.
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Meeting Details", "📈 Analytics"])
    
    with tab1:
        st.header("Recent Meetings")
        
        # Meeting cards
        for meeting in DEMO_MEETINGS:
            with st.expander(f"**{meeting['title']}** - {meeting['date']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Summary:** {meeting['summary'][:150]}...")
                
                with col2:
                    st.metric("Sentiment", meeting['sentiment'].split()[0])
                    st.metric("Duration", meeting['duration'])
                
                with col3:
                    st.metric("Actions", len(meeting['action_items']))
                    st.metric("Participants", len(meeting['participants'].split(',')))
                
                if st.button(f"View Details", key=f"view_{meeting['id']}"):
                    st.session_state.selected_meeting = meeting['id']
                    st.experimental_rerun()
    
    with tab2:
        if 'selected_meeting' in st.session_state:
            meeting = next(m for m in DEMO_MEETINGS if m['id'] == st.session_state.selected_meeting)
            
            st.header(meeting['title'])
            st.caption(f"Date: {meeting['date']} | Duration: {meeting['duration']}")
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Words", meeting['key_metrics']['word_count'])
            with col2:
                st.metric("Speaking Pace", meeting['key_metrics']['speaking_pace'])
            with col3:
                st.metric("Sentiment", meeting['sentiment'].split()[0])
            with col4:
                st.metric("Actions", len(meeting['action_items']))
            
            # Content tabs
            content_tab1, content_tab2, content_tab3 = st.tabs(["Summary", "Transcript", "Action Items"])
            
            with content_tab1:
                st.info(meeting['summary'])
            
            with content_tab2:
                st.text_area("", meeting['transcript'], height=300)
            
            with content_tab3:
                for i, action in enumerate(meeting['action_items'], 1):
                    st.checkbox(f"{action}", key=f"action_{meeting['id']}_{i}")
        else:
            st.info("Select a meeting from the Dashboard to view details")
    
    with tab3:
        st.header("Meeting Analytics")
        
        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Meetings", len(DEMO_MEETINGS))
        with col2:
            total_actions = sum(len(m['action_items']) for m in DEMO_MEETINGS)
            st.metric("Total Actions", total_actions)
        with col3:
            positive = sum(1 for m in DEMO_MEETINGS if "Positive" in m['sentiment'])
            st.metric("Positive Meetings", f"{positive}/{len(DEMO_MEETINGS)}")
        with col4:
            avg_duration = sum(int(m['duration'].split()[0]) for m in DEMO_MEETINGS) / len(DEMO_MEETINGS)
            st.metric("Avg Duration", f"{avg_duration:.0f} min")
        
        # Sentiment chart
        st.subheader("Sentiment Distribution")
        sentiments = [m['sentiment'].split()[0] for m in DEMO_MEETINGS]
        
        # Simple bar chart using metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Positive", sentiments.count("Positive"), delta="+15%")
        with col2:
            st.metric("Neutral", sentiments.count("Neutral"), delta="0%")
        with col3:
            st.metric("Negative", sentiments.count("Negative"), delta="-5%")

if __name__ == "__main__":
    run_emergency_demo()