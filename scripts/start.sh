#!/bin/bash
set -e

# Initialize volume if needed
if [ ! -f "/runpod-volume/.initialized" ]; then
    echo "First run: Initializing volume..."
    /app/scripts/init_volume.sh
    touch /runpod-volume/.initialized
else
    echo "Volume already initialized"
fi

# Activate volume venv
source /runpod-volume/fluxvenv/bin/activate

# Run handler
python -u /app/src/handler.py