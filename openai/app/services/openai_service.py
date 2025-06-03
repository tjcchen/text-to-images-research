from openai import AsyncOpenAI
from typing import List, Optional
from app.config import get_settings

async def generate_image(
    prompt: str,
    n: int = 1,
    size: str = "1024x1024",
    response_format: str = "url",
    style: str = "vivid",
    quality: str = "standard"
) -> List[str]:
    """
    Generate images using OpenAI's DALL-E model.
    
    Args:
        prompt: Text description of the desired image
        n: Number of images to generate (1-10)
        size: Size of the generated images (256x256, 512x512, or 1024x1024)
        response_format: Format of the generated images (url or b64_json)
        style: Style of the generated images (vivid or natural)
        quality: Quality of the generated images (standard or hd)
        
    Returns:
        A list of image URLs or base64-encoded JSON strings
    """
    settings = get_settings()
    # Initialize the OpenAI client with only the API key
    # Explicitly set http_client to None to prevent proxy issues
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        http_client=None
    )
    
    response = await client.images.generate(
        model="dall-e-3",  # Using DALL-E 3 which is the most advanced model
        prompt=prompt,
        n=n,
        size=size,
        response_format=response_format,
        style=style,
        quality=quality
    )
    
    # Extract the image URLs or base64 data depending on the response format
    if response_format == "url":
        return [item.url for item in response.data]
    else:  # b64_json
        return [item.b64_json for item in response.data]
