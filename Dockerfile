# Start from Python 3.9
FROM python:3.9-slim

# Install system dependencies (including ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project into the container
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose the ports your apps use
EXPOSE 8000 8501

# Create a simple startup script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Run the startup script
CMD ["./docker-entrypoint.sh"]