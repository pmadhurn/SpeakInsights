#!/bin/sh
echo "Starting SpeakInsights..."

# Start the backend API
echo "Starting backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Health check for backend
echo "Waiting for backend to be healthy..."
RETRY_COUNT=0
MAX_RETRIES=30 # Try for 30 seconds (30 * 1 second sleep)
HEALTHY=false
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Try to curl the /docs endpoint, suppress output, and fail on error
    if curl -s --fail http://localhost:8000/docs > /dev/null; then
        echo "Backend is healthy!"
        HEALTHY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Backend not ready yet (attempt: $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 1
done

if [ "$HEALTHY" != "true" ]; then
    echo "Error: Backend did not become healthy after $MAX_RETRIES seconds."
    # For now, we'll print an error but let Streamlit attempt to start.
    # Depending on requirements, one might choose to exit 1 here.
fi

# Start the frontend
echo "Starting frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0