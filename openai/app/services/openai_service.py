import httpx
import json
import logging
import socket
from typing import List, Optional, Dict, Any
import os
import sys
from fastapi import HTTPException
from app.config import get_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_response(response, response_format):
    """
    Process the API response and extract image data based on response format.

    Sample prompt:
      Create a trendy social media cover image inspired by Xiaohongshu (RED) posts. Use a modern, youthful aesthetic with a light pastel or stylish vivid color palette. Include soft lighting, and a lifestyle/artistic vibe. Overlay elegant Chinese text “王老师艺术留学工作室” in a clean, semi-transparent font centered or toward the top. The design should look like a fashionable post promoting an art education brand for international students on Xiaohongshu.

    Args:
        response: The HTTP response from the OpenAI API
        response_format: Format of the response (url or b64_json)
        
    Returns:
        List of URLs or base64 encoded JSON strings
    """
    result = response.json()
    logger.info("Successfully parsed OpenAI API response")
    
    # Extract the image URLs or base64 data depending on the response format
    if response_format == "url":
        return [item["url"] for item in result["data"]]
    else:  # b64_json
        return [item["b64_json"] for item in result["data"]]

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
    try:
        settings = get_settings()
        
        # Log the API key length to check if it's properly loaded (don't log the actual key)
        api_key = settings.openai_api_key
        logger.info(f"Using OpenAI API Key (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            logger.error("OpenAI API key is missing")
            raise ValueError("OpenAI API key is missing or invalid")
        
        # Define API endpoint and headers
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Log network environment information to help debug connectivity issues
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            logger.info(f"Network environment: hostname={hostname}, local_ip={local_ip}")
            
            # Try to resolve OpenAI's domain
            openai_ip = socket.gethostbyname("api.openai.com")
            logger.info(f"Successfully resolved api.openai.com to {openai_ip}")
        except Exception as e:
            logger.warning(f"Failed to get network information: {str(e)}")
        
        # Log proxy environment variables
        proxy_env_vars = {k: v for k, v in os.environ.items() if 'proxy' in k.lower()}
        logger.info(f"Proxy environment variables: {proxy_env_vars}")
        
        # Prepare request data
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
            "style": style,
            "quality": quality
        }
        
        logger.info(f"Making request to OpenAI API: {url} with data: {json.dumps(data, indent=2)}")
        
        # Try with system proxies first (which might be needed in some environments)
        try:
            logger.info("Attempting connection with system proxies...")
            async with httpx.AsyncClient(trust_env=True, timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                logger.info(f"Connection with system proxies successful, status: {response.status_code}")
                if response.status_code == 200:
                    return process_response(response, response_format)
        except Exception as e:
            logger.warning(f"Connection with system proxies failed: {str(e)}")
        
        # If that fails, try direct connection without proxies
        logger.info("Attempting direct connection without proxies...")
        async with httpx.AsyncClient(trust_env=False) as client:
            try:
                response = await client.post(url, headers=headers, json=data, timeout=60.0)
                
                # Log the response status and headers
                logger.info(f"OpenAI API response status: {response.status_code}")
                logger.info(f"OpenAI API response headers: {response.headers}")
                
                # Try to get the response content
                content = response.content
                logger.info(f"OpenAI API response content: {content}")
                
                # Check if the response is successful
                if response.status_code != 200:
                    error_detail = "Unknown error"
                    try:
                        error_json = response.json()
                        if "error" in error_json:
                            error_detail = error_json["error"].get("message", str(error_json))
                        else:
                            error_detail = str(error_json)
                    except Exception as e:
                        error_detail = f"Failed to parse error response: {str(e)}, Raw content: {content}"
                    
                    logger.error(f"OpenAI API error: {error_detail}")
                    raise HTTPException(status_code=response.status_code, detail=error_detail)
                
                # Parse the response
                result = response.json()
                logger.info("Successfully parsed OpenAI API response")
                
                return process_response(response, response_format)
                    
            except httpx.TimeoutException:
                logger.error("OpenAI API request timed out")
                raise HTTPException(status_code=504, detail="API request timed out")
            except httpx.RequestError as e:
                logger.error(f"OpenAI API request error: {str(e)}")
                raise HTTPException(status_code=502, detail=f"API request failed: {str(e)}")
            
    except Exception as e:
        logger.exception(f"Error in generate_image: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
