#!/bin/bash

# Run script for Customer Data Tools Flask application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set PYTHONPATH to project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults
export PORT=${PORT:-6000}
export DEBUG=${DEBUG:-True}
export FLASK_ENV=${FLASK_ENV:-development}

# Create logs directory if it doesn't exist
mkdir -p logs

echo "🚀 Starting Customer Data Tools..."
echo "   Port: $PORT"
echo "   Debug: $DEBUG"
echo "   Environment: $FLASK_ENV"
echo ""

# Run the application
./venv/bin/python src/app.py
