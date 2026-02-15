#!/bin/bash
# Start the app — builds frontend + runs Flask, all in one command.
# Usage: conda activate aichoir && ./start.sh

set -e

cd "$(dirname "$0")"

# Build frontend
echo "Building frontend..."
npm run build

# Start Flask
echo "Starting server on http://localhost:5001"
python backend/app.py
