#!/usr/bin/env python3
"""
Simple test for MCP server functionality
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import get_meetings, get_meeting_details

async def test_mcp_functions():
    """Test MCP server functions directly"""
    print("Testing SpeakInsights MCP Server Functions...")
    
    try:
        # Test get_meetings
        print("\n1. Testing get_meetings...")
        meetings_result = await get_meetings(5)
        print(f"✅ get_meetings returned: {meetings_result[0].text if meetings_result else 'No result'}")
        
        # Test get_meeting_details
        print("\n2. Testing get_meeting_details...")
        details_result = await get_meeting_details(1)
        print(f"✅ get_meeting_details returned: {details_result[0].text[:200] if details_result else 'No result'}...")
        
        print("\n✅ All basic MCP functions work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_functions())
    sys.exit(0 if success else 1)
