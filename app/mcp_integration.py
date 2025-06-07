# Create app/mcp_integration.py
import json
import os

def export_to_mcp_format(meeting_data):
    """Export meeting data in MCP-compatible format"""
    mcp_data = {
        "type": "meeting_transcript",
        "title": meeting_data["title"],
        "content": {
            "transcript": meeting_data["transcript"],
            "summary": meeting_data["summary"],
            "action_items": meeting_data["action_items"],
            "metadata": {
                "date": meeting_data["date"],
                "sentiment": meeting_data["sentiment"]
            }
        }
    }
    
    # Save to MCP export directory
    os.makedirs("data/mcp_exports", exist_ok=True)
    export_path = f"data/mcp_exports/meeting_{meeting_data['id']}.json"
    
    with open(export_path, "w") as f:
        json.dump(mcp_data, f, indent=2)
    
    return export_path

def create_task_export(action_items, meeting_title):
    """Create task list for external tools"""
    tasks = []
    for idx, item in enumerate(action_items):
        tasks.append({
            "id": f"task_{idx+1}",
            "title": item,
            "source": f"Meeting: {meeting_title}",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })
    
    return tasks