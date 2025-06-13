#!/bin/bash
echo "Starting SpeakInsights..."

# Start the backend API
echo "Starting backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait a bit for backend to start
sleep 5

# Start the frontend
echo "Starting frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0