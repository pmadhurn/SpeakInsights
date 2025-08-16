# SpeakInsights Docker Deployment Guide

This guide covers deploying SpeakInsights using Docker and Docker Compose for production or development environments.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- At least 4GB RAM available for containers
- 10GB free disk space for models and data

## Quick Start

### Windows
```cmd
docker-deploy.bat
```

### Linux/Mac
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

### Manual Docker Compose
```bash
# Copy environment template
cp .env.docker .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Architecture

The Docker setup includes:

- **speakinsights**: Main application container (FastAPI + Streamlit)
- **speakinsights-mcp**: MCP server for Claude integration
- **postgres**: PostgreSQL database for data persistence

## Configuration

### Environment Variables

Create a `.env` file or modify `.env.docker`:

```env
# Whisper Model (tiny, base, small, medium, large)
WHISPER_MODEL=base

# Application Mode (full, api, frontend, mcp)
SPEAKINSIGHTS_MODE=full

# Database Configuration
POSTGRES_DB=speakinsights
POSTGRES_USER=speakinsights_user
POSTGRES_PASSWORD=speakinsights_password
```

### Ports

Default port mapping:
- `8501`: Streamlit frontend
- `8000`: FastAPI backend
- `3000`: External API access
- `5432`: PostgreSQL database

To change ports, modify `docker-compose.yml` or use environment variables.

## Deployment Modes

### Full Application (Default)
```bash
./docker-deploy.sh --mode full
```
Starts both frontend and backend services.

### API Only
```bash
./docker-deploy.sh --mode api
```
Starts only the FastAPI backend.

### Frontend Only
```bash
./docker-deploy.sh --mode frontend
```
Starts only the Streamlit frontend.

### MCP Server Only
```bash
./docker-deploy.sh --mode mcp
```
Starts only the MCP server for Claude integration.

## Data Persistence

### Volumes

- `app_data`: Application data (transcripts, exports)
- `model_cache`: ML model cache (Whisper, Transformers)
- `sqlite_data`: SQLite database backup
- `postgres_data`: PostgreSQL data

### Host Directories

- `./persistent_data`: Accessible from host system
- `./backups`: Database and data backups

## Development

### Building Images
```bash
# Rebuild all images
docker-compose up --build

# Rebuild specific service
docker-compose build speakinsights
```

### Debugging
```bash
# View logs
docker-compose logs -f speakinsights

# Access container shell
docker exec -it speakinsights-app bash

# Run tests in container
docker exec -it speakinsights-app python test_setup.py
```

### Hot Reload
For development, mount source code:
```yaml
volumes:
  - .:/app
  - app_data:/app/data
```

## MCP Server Integration

### Starting MCP Server
```bash
# Start MCP container
docker-compose up -d speakinsights-mcp

# Connect to MCP server
docker exec -it speakinsights-mcp python mcp_server.py
```

### Claude Integration
1. Start the MCP container
2. Configure Claude to connect to the container
3. Use MCP tools to interact with SpeakInsights data

## Production Deployment

### Security Considerations

1. **Change default passwords**:
   ```env
   POSTGRES_PASSWORD=your_secure_password
   ```

2. **Use secrets management**:
   ```yaml
   secrets:
     postgres_password:
       file: ./secrets/postgres_password.txt
   ```

3. **Enable SSL/TLS** for external access

4. **Configure firewall** to restrict access

### Performance Optimization

1. **Resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 4G
         cpus: '2'
   ```

2. **Model caching**: Ensure models are cached in volumes

3. **Database tuning**: Configure PostgreSQL for your workload

### Monitoring

1. **Health checks**: Built-in health endpoints
2. **Logging**: Centralized logging with Docker logs
3. **Metrics**: Add Prometheus/Grafana if needed

## Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use 8001 instead of 8000
   ```

2. **Permission issues**:
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 ./persistent_data
   ```

3. **Out of memory**:
   ```bash
   # Check container memory usage
   docker stats
   
   # Increase Docker Desktop memory limit
   # Or use smaller Whisper model (tiny instead of base)
   ```

4. **Database connection failed**:
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f speakinsights

# Follow logs with timestamps
docker-compose logs -f -t

# View last 100 lines
docker-compose logs --tail=100 speakinsights
```

## Backup and Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker exec speakinsights-postgres pg_dump -U speakinsights_user speakinsights > backup.sql

# Restore PostgreSQL
docker exec -i speakinsights-postgres psql -U speakinsights_user speakinsights < backup.sql
```

### Data Backup
```bash
# Backup application data
docker run --rm -v speakinsights_app_data:/data -v $(pwd):/backup alpine tar czf /backup/app_data_backup.tar.gz -C /data .

# Restore application data
docker run --rm -v speakinsights_app_data:/data -v $(pwd):/backup alpine tar xzf /backup/app_data_backup.tar.gz -C /data
```

## Scaling

### Horizontal Scaling
```yaml
# Scale main application
docker-compose up -d --scale speakinsights=3

# Use load balancer (nginx, traefik)
```

### Vertical Scaling
```yaml
# Increase resources
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4'
```

## Updates

### Application Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d

# Or use deployment script
./docker-deploy.sh --build
```

### Model Updates
Models are cached in volumes and will persist across container restarts. To update models, clear the model cache volume:

```bash
docker volume rm speakinsights_model_cache
docker-compose up -d
```

## Support

For issues with Docker deployment:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test setup: `docker exec -it speakinsights-app python test_setup.py`
4. Check resources: `docker stats`