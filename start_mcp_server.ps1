# Start SpeakInsights MCP Server
Write-Host "Starting SpeakInsights MCP Server..." -ForegroundColor Green
Write-Host "This server will provide Claude Desktop access to your meeting transcripts" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" * 60

try {
    python mcp_server.py
}
catch {
    Write-Host "Error starting MCP server: $_" -ForegroundColor Red
}

Write-Host "MCP Server stopped." -ForegroundColor Yellow
