#!/bin/bash
set -e

echo "=== Initializing RunPod Volume ==="

# Define paths
VOLUME_PATH="/runpod-volume"
VENV_PATH="$VOLUME_PATH/fluxvenv"
MODELS_PATH="$VOLUME_PATH/flux-models"
CACHE_PATH="$VOLUME_PATH/.cache"

# Create directories
mkdir -p "$VENV_PATH"
mkdir -p "$MODELS_PATH"
mkdir -p "$CACHE_PATH"

# Check if venv exists
if [ ! -d "$VENV_PATH/bin" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install --no-cache-dir -r /app/requirements.txt

echo "=== Volume initialization complete ==="