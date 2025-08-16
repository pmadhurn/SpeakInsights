# Multi-stage build for better optimization
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-mcp.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user -r requirements-mcp.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set the working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/audio /app/data/transcripts /app/data/exports \
             /app/models/transformers /app/models/huggingface /app/models/torch \
             /app/database /app/persistent_data /app/backups \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app \
    && chmod -R 777 /app/data /app/models /app/database

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=/home/appuser/.local/bin:$PATH
ENV TRANSFORMERS_CACHE=/app/models/transformers
ENV HF_HOME=/app/models/huggingface
ENV TORCH_HOME=/app/models/torch
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY --chown=appuser:appgroup . .

# Make scripts executable
RUN chmod +x docker-entrypoint.sh start.py test_setup.py

# Create volumes
VOLUME ["/app/data", "/app/models", "/app/database"]

# Expose ports
EXPOSE 8000 8501 3000

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - can be overridden in docker-compose
CMD ["python", "start.py"]
