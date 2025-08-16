# Start from Python 3.11 with CUDA support
FROM python:3.11-slim

# Install system dependencies (including ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

# Set the working directory inside container
WORKDIR /app

# Copy requirements files
COPY requirements.txt ./
COPY requirements-mcp.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Create necessary directories and set permissions
RUN mkdir -p /app/data /app/models /home/appuser/.cache \
    && chown -R appuser:appgroup /app /home/appuser \
    && chmod -R 777 /app/data /app/models /home/appuser/.cache

# Set environment variables for model caching
ENV TRANSFORMERS_CACHE=/app/models/transformers
ENV HF_HOME=/app/models/huggingface
ENV TORCH_HOME=/app/models/torch

# Copy the rest of the project
COPY . .

# Ensure all files have correct permissions
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/data /app/models /home/appuser/.cache

# Create volumes
VOLUME ["/app/data", "/app/models"]

# Expose the ports your apps use
EXPOSE 8000 8501 3000

# Create a simple startup script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Switch to non-root user
USER appuser

# For MCP server, we need the container to stay alive
# The actual command will be specified in docker-compose or via docker exec
CMD ["tail", "-f", "/dev/null"]
