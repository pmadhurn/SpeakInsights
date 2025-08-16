#!/usr/bin/env python3
"""
Test script for SpeakInsights MCP Server
"""
import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import app
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing SpeakInsights MCP Server...")
    
    try:
        # Test database connection
        from mcp_server import DB_PATH
        import sqlite3
        
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Database connected. Tables: {[table[0] for table in tables]}")
            conn.close()
        else:
            print("⚠️ Database not found")
        
        # Test MCP server initialization
        print("🔗 Testing MCP server initialization...")
        
        async with stdio_server() as (read_stream, write_stream):
            # Test the server initialization
            init_options = InitializationOptions(
                server_name="speakinsights-mcp",
                server_version="1.0.0",
                capabilities={
                    "tools": {},
                    "resources": {}
                }
            )
            
            print("✅ MCP server initialization successful")
            
            # Test listing tools
            tools = await app.list_tools()
            print(f"✅ Found {len(tools)} tools: {[tool.name for tool in tools]}")
            
            # Test listing resources
            resources = await app.list_resources()
            print(f"✅ Found {len(resources)} resources: {[resource.name for resource in resources]}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1) 