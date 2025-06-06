from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import base64
import os
from app.services.openai_service import generate_image
from app.services.image_processing_service import process_image_with_text
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

class TextOverlayRequest(BaseModel):
    image_source: str  # URL or base64 encoded image
    text: str
    font_size: Optional[int] = Field(default=60, ge=10, le=200)
    position: Optional[Tuple[int, int]] = Field(default=(0, 0))
    color: Optional[Tuple[int, int, int]] = Field(default=(255, 255, 255))
    opacity: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    align: Optional[str] = Field(default="center", pattern="^(left|center|right)$")
    font_path: Optional[str] = None
    bg_color: Optional[Tuple[int, int, int]] = Field(default=(255, 255, 0))
    bg_opacity: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    padding: Optional[int] = Field(default=16, ge=0, le=128)
    border_radius: Optional[int] = Field(default=16, ge=0, le=128)

class TextOverlayResponse(BaseModel):
    image: str  # base64 encoded image
    text: str

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

        # If prompt is empty, use static/image.jpg as background
        if not request.prompt.strip():
            # Read the static image as bytes
            static_image_path = "static/image.jpg"
            try:
                with open(static_image_path, "rb") as f:
                    image_bytes = f.read()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load default image: {e}")
            # Apply overlay if Chinese text is provided
            chinese_text = getattr(request, 'chinese_text', None) or ""
            if chinese_text.strip():
                # Use overlay parameters from request if available
                overlay_bytes = await process_image_with_text(
                    image_source=image_bytes,
                    text=chinese_text,
                    font_size=getattr(request, 'font_size', 60),
                    position=getattr(request, 'position', (0, 0)),
                    color=getattr(request, 'color', (255, 255, 255)),
                    opacity=getattr(request, 'opacity', 0.8),
                    align=getattr(request, 'align', 'center'),
                    font_path=getattr(request, 'font_path', None),
                    bg_color=getattr(request, 'bg_color', (255, 255, 0)),
                    bg_opacity=getattr(request, 'bg_opacity', 0.8),
                    padding=getattr(request, 'padding', 16),
                    border_radius=getattr(request, 'border_radius', 16)
                )
                image_bytes = overlay_bytes
            # Return as base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            return ImageGenerationResponse(images=[base64_image], prompt=request.prompt)

        # Normal DALL-E flow
        images = await generate_image(
            prompt=request.prompt,
            n=request.n,
            size=request.size,
            response_format=request.response_format,
            style=request.style,
            quality=request.quality
        )
        return ImageGenerationResponse(images=images, prompt=request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-text", response_model=TextOverlayResponse)
async def add_text_to_image(request: TextOverlayRequest):
    """
    Add text overlay to an image.
    
    - **image_source**: URL or base64 encoded image data
    - **text**: Text to overlay on the image
    - **font_size**: Size of the font (10-200)
    - **position**: (x, y) position of the text
    - **color**: RGB color tuple for the text
    - **opacity**: Text opacity (0.0 to 1.0)
    - **align**: Text alignment ("left", "center", or "right")
    - **font_path**: Optional path to a font file
    """
    try:
        # Process the image with text overlay
        processed_image = await process_image_with_text(
            image_source=request.image_source,
            text=request.text,
            font_size=request.font_size,
            position=request.position,
            color=request.color,
            opacity=request.opacity,
            align=request.align,
            font_path=request.font_path,
            bg_color=request.bg_color,
            bg_opacity=request.bg_opacity,
            padding=request.padding,
            border_radius=request.border_radius
        )
        
        # Convert the processed image to base64
        base64_image = base64.b64encode(processed_image).decode('utf-8')
        
        return TextOverlayResponse(
            image=base64_image,
            text=request.text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
