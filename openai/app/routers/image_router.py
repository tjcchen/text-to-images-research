from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import base64
import os
from app.services.openai_service import generate_image
from app.config import get_settings

router = APIRouter(
    prefix="/images",
    tags=["Images"],
    responses={404: {"description": "Not found"}},
)

class ImageGenerationRequest(BaseModel):
    prompt: str
    n: Optional[int] = 1
    size: Optional[str] = "1024x1024"
    response_format: Optional[str] = "url"  # can be "url" or "b64_json"
    style: Optional[str] = "vivid"  # can be "vivid" or "natural"
    quality: Optional[str] = "standard"  # can be "standard" or "hd"

class ImageGenerationResponse(BaseModel):
    images: List[str]
    prompt: str

@router.post("/generate", response_model=ImageGenerationResponse)
async def create_image(request: ImageGenerationRequest):
    """
    Generate images based on a text prompt using OpenAI's DALL-E.
    
    - **prompt**: Text description of the desired image
    - **n**: Number of images to generate (1-10)
    - **size**: Size of the generated images (256x256, 512x512, or 1024x1024)
    - **response_format**: Format of the generated images (url or b64_json)
    - **style**: Style of the generated images (vivid or natural)
    - **quality**: Quality of the generated images (standard or hd)
    """
    try:
        # Validate number of images
        if request.n < 1 or request.n > 10:
            raise HTTPException(status_code=400, detail="Number of images must be between 1 and 10")
        
        # Validate image size
        valid_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
        if request.size not in valid_sizes:
            raise HTTPException(status_code=400, detail=f"Size must be one of {valid_sizes}")
        
        # Generate images
        images = await generate_image(
            prompt=request.prompt,
            n=request.n,
            size=request.size,
            response_format=request.response_format,
            style=request.style,
            quality=request.quality
        )
        
        return ImageGenerationResponse(
            images=images,
            prompt=request.prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
