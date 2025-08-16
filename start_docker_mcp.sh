#!/bin/bash
echo "Docker SpeakInsights MCP Setup"
echo "=============================="

echo "Building Docker image..."
docker build -t speakinsights:latest .

echo "Starting services..."
docker-compose up -d

echo "Services started!"
echo "Container status:"
docker-compose ps

echo ""
echo "MCP Server ready!"
echo "Now restart Claude Desktop to use the integration."
echo ""
echo "Available commands:"
echo "  - View logs: docker-compose logs -f speakinsights-mcp"
echo "  - Stop services: docker-compose down"
echo "  - Rebuild: docker-compose down && docker build -t speakinsights:latest . && docker-compose up -d"
