"""
Demo mode with sample data for presentation
"""
import os
import json
from datetime import datetime, timedelta
from app.database import save_meeting

def create_demo_data():
    """Create sample meetings for demonstration"""
    
    demo_meetings = [
        {
            "title": "Q4 Strategic Planning",
            "date": (datetime.now() - timedelta(days=2)).isoformat(),
            "transcript": "Welcome everyone to our Q4 strategic planning meeting. Today we'll discuss our goals for the next quarter. First, we need to increase our market share by 15%. John will lead the marketing campaign. Sarah, you'll handle the product development timeline. We should launch the new feature by November 15th. Mike will coordinate with the sales team. Action items: John will prepare the marketing strategy by next Friday. Sarah will finalize the development roadmap. Mike will set up meetings with key clients.",
            "summary": "Q4 planning meeting focused on 15% market share growth. Key initiatives include new marketing campaign, product feature launch by Nov 15, and client outreach.",
            "sentiment": "Positive (87% confidence)",
            "action_items": [
                "John will prepare the marketing strategy by next Friday",
                "Sarah will finalize the development roadmap",
                "Mike will set up meetings with key clients",
                "Launch new feature by November 15th",
                "Increase market share by 15%"
            ]
        },
        {
            "title": "Weekly Team Standup",
            "date": (datetime.now() - timedelta(days=1)).isoformat(),
                        "transcript": "Good morning team. Let's do our weekly standup. I'm concerned about the delayed deliverables from last week. We need to address the bottlenecks in our development process. The client is not happy with the delays. However, I'm pleased with the quality of work when it's completed. We must improve our time estimates. Action items: Everyone should update their task estimates in Jira. We will implement daily check-ins starting tomorrow. I need the bug report from the QA team by end of day.",
            "summary": "Team standup addressed concerns about delivery delays and process bottlenecks. Focus on improving time estimates and implementing daily check-ins.",
            "sentiment": "Negative (65% confidence)",
            "action_items": [
                "Everyone should update their task estimates in Jira",
                "We will implement daily check-ins starting tomorrow",
                "Need the bug report from the QA team by end of day"
            ]
        },
        {
            "title": "Product Launch Review",
            "date": datetime.now().isoformat(),
            "transcript": "Great job everyone on the successful product launch! The numbers are exceeding our expectations. We had 10,000 signups in the first week. Customer feedback has been overwhelmingly positive. The marketing campaign was particularly effective. We should celebrate this win but also prepare for scaling challenges. Action items: DevOps team will prepare scaling plan for 50k users. Marketing will create case studies from early adopters. Support team should hire 2 additional members.",
            "summary": "Successful product launch review with 10,000 signups in week one. Team celebrating success while preparing for scaling challenges.",
            "sentiment": "Positive (92% confidence)",
            "action_items": [
                "DevOps team will prepare scaling plan for 50k users",
                "Marketing will create case studies from early adopters",
                "Support team should hire 2 additional members"
            ]
        }
    ]
    
    print("🎬 Creating demo data...")
    
    for meeting in demo_meetings:
        meeting_id = save_meeting(meeting)
        print(f"✅ Created demo meeting: {meeting['title']}")
    
    print("\n✨ Demo data created successfully!")
    print("You can now run the application and see these sample meetings.")

if __name__ == "__main__":
    create_demo_data()