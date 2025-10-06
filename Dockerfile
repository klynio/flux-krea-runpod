# Use RunPod's PyTorch base image
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Copy initialization script
COPY scripts/init_volume.sh /app/scripts/
RUN chmod +x /app/scripts/init_volume.sh

# Copy source code
COPY src/ ./src/

# Set environment variables for volume paths
ENV VOLUME_PATH=/runpod-volume
ENV VENV_PATH=/runpod-volume/venv
ENV MODELS_PATH=/runpod-volume/flux-models
ENV HF_HOME=/runpod-volume/.cache/huggingface
ENV TRANSFORMERS_CACHE=/runpod-volume/.cache/transformers
ENV HF_DATASETS_CACHE=/runpod-volume/.cache/datasets

# Create a startup script that initializes volume and runs handler
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Initialize volume if needed\n\
if [ ! -f "/runpod-volume/.initialized" ]; then\n\
    echo "First run: Initializing volume..."\n\
    /app/scripts/init_volume.sh\n\
    touch /runpod-volume/.initialized\n\
else\n\
    echo "Volume already initialized"\n\
fi\n\
\n\
# Activate volume venv\n\
source /runpod-volume/venv/bin/activate\n\
\n\
# Run handler\n\
python -u /app/src/handler.py\n\
' > /start.sh && chmod +x /start.sh

# Use the startup script
CMD ["/start.sh"]