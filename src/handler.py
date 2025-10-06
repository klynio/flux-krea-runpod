import os
import sys

# Add volume venv to path FIRST
VOLUME_PATH = "/runpod-volume"
VENV_PATH = os.path.join(VOLUME_PATH, "venv")
VENV_SITE_PACKAGES = os.path.join(VENV_PATH, "lib", "python3.10", "site-packages")

# Prepend to sys.path to prioritize volume packages
if os.path.exists(VENV_SITE_PACKAGES):
    sys.path.insert(0, VENV_SITE_PACKAGES)
    print(f"Using venv from: {VENV_SITE_PACKAGES}")

import runpod
import torch
from diffusers import FluxPipeline
from io import BytesIO
import base64
from PIL import Image

# Set cache directories to volume
os.environ['HF_HOME'] = os.path.join(VOLUME_PATH, ".cache", "huggingface")
os.environ['TRANSFORMERS_CACHE'] = os.path.join(VOLUME_PATH, ".cache", "transformers")
os.environ['HF_DATASETS_CACHE'] = os.path.join(VOLUME_PATH, ".cache", "datasets")

# Models directory
MODELS_DIR = os.path.join(VOLUME_PATH, "models")

# Initialize the pipeline globally
pipe = None

def load_model():
    """Load the FLUX.1-Krea-dev model from volume"""
    global pipe
    
    if pipe is None:
        print("Loading FLUX.1-Krea-dev model...")
        
        # Get HF token from RunPod environment variables
        hf_token = os.environ.get("HF_TOKEN")
        
        if not hf_token:
            raise ValueError("HF_TOKEN environment variable not set. Please add it to your RunPod endpoint configuration.")
        
        # Define model path in volume
        model_name = "black-forest-labs/FLUX.1-Krea-dev"
        model_path = os.path.join(MODELS_DIR, model_name.replace("/", "--"))
        
        # Check if model exists locally in volume
        if os.path.exists(model_path) and os.listdir(model_path):
            print(f"Loading model from volume: {model_path}")
            pipe = FluxPipeline.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                local_files_only=True
            )
        else:
            print(f"Downloading model to volume: {model_path}")
            os.makedirs(model_path, exist_ok=True)
            pipe = FluxPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                token=hf_token,
                cache_dir=MODELS_DIR
            )
            # Save to volume for future use
            pipe.save_pretrained(model_path)
        
        # Move to GPU
        pipe.to("cuda")
        
        # Optional: Enable memory optimizations
        # Uncomment if you have VRAM constraints
        # pipe.enable_model_cpu_offload()
        # pipe.enable_attention_slicing()
        
        print("Model loaded successfully!")
    
    return pipe

def generate_image(job):
    """
    Generate image from text prompt
    
    Expected input:
    {
        "prompt": "A frog holding a sign that says hello world",
        "height": 1024,
        "width": 1024,
        "guidance_scale": 4.5,
        "num_inference_steps": 50,
        "seed": -1
    }
    """
    try:
        job_input = job["input"]
        
        # Get parameters
        prompt = job_input.get("prompt", "")
        height = job_input.get("height", 1024)
        width = job_input.get("width", 1024)
        guidance_scale = job_input.get("guidance_scale", 4.5)
        num_inference_steps = job_input.get("num_inference_steps", 50)
        seed = job_input.get("seed", -1)
        
        # Validate inputs
        if not prompt:
            return {"error": "No prompt provided"}
        
        # Clamp dimensions
        height = max(512, min(2048, height))
        width = max(512, min(2048, width))
        
        # Set seed if provided
        generator = None
        if seed != -1:
            generator = torch.Generator(device="cuda").manual_seed(seed)
        
        # Load model
        pipeline = load_model()
        
        # Generate image
        print(f"Generating image with prompt: {prompt}")
        image = pipeline(
            prompt,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator
        ).images[0]
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image": img_str,
            "image_format": "png",
            "seed": seed if seed != -1 else "random"
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return {"error": str(e), "trace": error_trace}

# Start the serverless worker
if __name__ == "__main__":
    print("Starting FLUX.1-Krea-dev serverless worker...")
    print(f"Volume path: {VOLUME_PATH}")
    print(f"Models directory: {MODELS_DIR}")
    print(f"Cache directory: {os.environ['HF_HOME']}")
    runpod.serverless.start({"handler": generate_image})