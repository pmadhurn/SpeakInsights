Write-Host "Docker SpeakInsights MCP Setup" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t speakinsights:latest .

Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Services started!" -ForegroundColor Green
Write-Host "Container status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "MCP Server ready!" -ForegroundColor Green
Write-Host "Now restart Claude Desktop to use the integration." -ForegroundColor Cyan
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  - View logs: docker-compose logs -f speakinsights-mcp"
Write-Host "  - Stop services: docker-compose down"
Write-Host "  - Rebuild: docker-compose down; docker build -t speakinsights:latest .; docker-compose up -d"
Write-Host ""
Write-Host "Testing MCP connection..." -ForegroundColor Yellow
Write-Host "Waiting for container to be ready..."
Start-Sleep -Seconds 5

$testResult = docker exec speakinsights-mcp python -c "import mcp; print('MCP available')" 2>$null
if ($testResult -eq "MCP available") {
    Write-Host "✅ MCP dependencies are installed correctly!" -ForegroundColor Green
} else {
    Write-Host "❌ MCP dependencies may be missing. Check container logs." -ForegroundColor Red
    Write-Host "Run: docker-compose logs speakinsights-mcp" -ForegroundColor Yellow
}
