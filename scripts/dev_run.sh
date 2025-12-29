#!/bin/bash

# Development run script

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Run the application
echo "Starting AI Research Agent..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
