#!/bin/bash

# Startup script for SSH Manager API

echo "Starting SSH Manager API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create upload directory if it doesn't exist
mkdir -p uploads

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

