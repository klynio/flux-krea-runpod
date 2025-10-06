# FLUX.1-Krea-dev RunPod Serverless

Serverless deployment of FLUX.1-Krea-dev image generation model on RunPod.

## Features

- 🚀 Automatic Docker builds from GitHub
- 💾 Persistent model storage in RunPod volume
- 🔒 Secure API key management via RunPod environment variables
- ⚡ Fast cold starts with volume caching
- 🎨 High-quality image generation

## Deployment

This repository is designed to be deployed directly to RunPod serverless endpoints.

### Prerequisites

1. RunPod account
2. Hugging Face account with FLUX.1-Krea-dev access
3. RunPod Network Volume (50GB+)

### Setup Instructions

See deployment guide in this repository.

## API Usage

### Input Parameters
```json
{
  "prompt": "A majestic lion in Renaissance style",
  "height": 1024,
  "width": 1024,
  "guidance_scale": 4.5,
  "num_inference_steps": 50,
  "seed": 42
}