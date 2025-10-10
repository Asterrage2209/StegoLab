"""
StegoLab Backend - LSB Steganography & Anti-Steganography API
Main FastAPI application entry point.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import tempfile
import shutil
from typing import Optional, List
import json

from steganography import SteganographyEngine
from analysis import SteganalysisEngine
from models import EmbedRequest, ExtractRequest, AnalysisResult

app = FastAPI(
    title="StegoLab API",
    description="LSB Steganography & Anti-Steganography Web Application",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
stego_engine = SteganographyEngine()
analysis_engine = SteganalysisEngine()

# Temporary directory for file processing
TEMP_DIR = tempfile.mkdtemp()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up temporary files on shutdown."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "StegoLab API - LSB Steganography & Anti-Steganography",
        "version": "1.0.0",
        "endpoints": {
            "embed": "/api/embed",
            "extract": "/api/extract", 
            "analyze": "/api/analyze",
            "demo_images": "/api/demo-images"
        }
    }

@app.post("/api/embed")
async def embed_data(
    carrier_image: UploadFile = File(...),
    payload_text: Optional[str] = Form(None),
    payload_file: Optional[UploadFile] = File(None),
    bits: int = Form(1),
    channels: str = Form("auto"),
    password: Optional[str] = Form(None),
    encrypt: bool = Form(False)
):
    """
    Embed data into an image using LSB steganography.
    
    Args:
        carrier_image: The cover image (PNG/BMP only)
        payload_text: Text to embed (optional if payload_file provided)
        payload_file: File to embed (optional if payload_text provided)
        bits: Number of LSBs to use (1 or 2)
        channels: Channels to use ("red", "green", "blue", "auto")
        password: Optional password for permutation/encryption
        encrypt: Whether to encrypt the payload
    
    Returns:
        JSON with stego image data and metrics
    """
    try:
        # Validate inputs
        if not payload_text and not payload_file:
            raise HTTPException(status_code=400, detail="Either payload_text or payload_file must be provided")
        
        if bits not in [1, 2]:
            raise HTTPException(status_code=400, detail="bits must be 1 or 2")
        
        # Validate image format
        if not carrier_image.filename.lower().endswith(('.png', '.bmp')):
            raise HTTPException(status_code=400, detail="Only PNG and BMP images are supported for LSB embedding")
        
        # Save uploaded files temporarily
        carrier_path = os.path.join(TEMP_DIR, f"carrier_{carrier_image.filename}")
        with open(carrier_path, "wb") as buffer:
            shutil.copyfileobj(carrier_image.file, buffer)
        
        # Process payload
        payload_data = None
        if payload_text:
            payload_data = payload_text.encode('utf-8')
        elif payload_file:
            payload_data = await payload_file.read()
        
        # Parse channels
        channel_list = []
        if channels == "auto":
            channel_list = ["red", "green", "blue"]
        else:
            channel_list = [channels]
        
        # Perform embedding
        result = stego_engine.embed(
            carrier_path=carrier_path,
            payload_data=payload_data,
            bits=bits,
            channels=channel_list,
            password=password,
            encrypt=encrypt
        )
        
        # Clean up carrier file
        os.remove(carrier_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if 'carrier_path' in locals() and os.path.exists(carrier_path):
            os.remove(carrier_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract")
async def extract_data(
    image: UploadFile = File(...),
    password: Optional[str] = Form(None),
    bits: int = Form(1),
    channels: str = Form("auto"),
    encrypt: bool = Form(False)
):
    """
    Extract data from a stego image.
    
    Args:
        image: The stego image
        password: Password used during embedding
        bits: Number of LSBs used
        channels: Channels used ("red", "green", "blue", "auto")
        encrypt: Whether payload was encrypted
    
    Returns:
        Extracted payload data
    """
    try:
        # Parse channels
        channel_list = []
        if channels == "auto":
            channel_list = ["red", "green", "blue"]
        else:
            channel_list = [channels]
        
        # Save uploaded image temporarily
        image_path = os.path.join(TEMP_DIR, f"stego_{image.filename}")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Perform extraction
        result = stego_engine.extract(
            stego_path=image_path,
            bits=bits,
            channels=channel_list,
            password=password,
            encrypt=encrypt
        )
        
        # Clean up
        os.remove(image_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze an image for steganographic content.
    
    Args:
        image: The image to analyze
    
    Returns:
        Analysis results with confidence score and visualizations
    """
    try:
        # Save uploaded image temporarily
        image_path = os.path.join(TEMP_DIR, f"analyze_{image.filename}")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Perform analysis
        result = analysis_engine.analyze(image_path)
        
        # Clean up
        os.remove(image_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo-images")
async def get_demo_images():
    """Get list of demo images for testing."""
    demo_images = [
        {
            "name": "sample_cover.png",
            "description": "Sample cover image for embedding",
            "type": "cover"
        },
        {
            "name": "sample_stego.png", 
            "description": "Sample stego image with embedded text",
            "type": "stego"
        }
    ]
    return {"demo_images": demo_images}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
