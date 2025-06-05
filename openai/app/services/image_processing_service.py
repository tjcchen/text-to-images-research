from PIL import Image, ImageDraw, ImageFont
import io
import base64
import httpx
import logging
from typing import Union, Tuple, Optional
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextOverlayConfig:
    def __init__(
        self,
        text: str,
        font_size: int = 60,
        font_path: Optional[str] = None,
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        opacity: float = 0.8,
        align: str = "center"
    ):
        self.text = text
        self.font_size = font_size
        self.font_path = font_path or self._get_default_font()
        self.position = position
        self.color = color
        self.opacity = opacity
        self.align = align

    def _get_default_font(self) -> str:
        """Get the default font path for Chinese text."""
        # Try to find a system font that supports Chinese characters
        system_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                return font_path
        
        # If no system font is found, use a default font
        return "arial.ttf"

async def add_text_overlay(
    image_source: Union[str, bytes],
    config: TextOverlayConfig
) -> bytes:
    """
    Add text overlay to an image.
    
    Args:
        image_source: URL or base64 encoded image data
        config: TextOverlayConfig object containing text overlay settings
        
    Returns:
        bytes: The processed image data
    """
    try:
        # Load the image
        if isinstance(image_source, str):
            if image_source.startswith('http'):
                # Download image from URL
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source)
                    image_data = response.content
            else:
                # Assume it's base64 encoded
                image_data = base64.b64decode(image_source)
        else:
            image_data = image_source

        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create a new transparent layer for the text
        txt_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Load font
        try:
            font = ImageFont.truetype(config.font_path, config.font_size)
        except Exception as e:
            logger.warning(f"Failed to load specified font: {e}")
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox(config.position, config.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        if config.align == "center":
            x = (image.width - text_width) // 2
            y = config.position[1]
        elif config.align == "right":
            x = image.width - text_width - config.position[0]
            y = config.position[1]
        else:  # left align
            x = config.position[0]
            y = config.position[1]
        
        # Draw text with opacity
        color_with_opacity = (*config.color, int(255 * config.opacity))
        draw.text((x, y), config.text, font=font, fill=color_with_opacity)
        
        # Composite the text layer onto the image
        result = Image.alpha_composite(image, txt_layer)
        
        # Convert back to RGB if needed
        if result.mode == 'RGBA':
            result = result.convert('RGB')
        
        # Save to bytes
        output = io.BytesIO()
        result.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error adding text overlay: {str(e)}")
        raise

async def process_image_with_text(
    image_source: Union[str, bytes],
    text: str,
    font_size: int = 60,
    position: Tuple[int, int] = (0, 0),
    color: Tuple[int, int, int] = (255, 255, 255),
    opacity: float = 0.8,
    align: str = "center",
    font_path: Optional[str] = None
) -> bytes:
    """
    Convenience function to process an image with text overlay.
    
    Args:
        image_source: URL or base64 encoded image data
        text: Text to overlay
        font_size: Size of the font
        position: (x, y) position of the text
        color: RGB color tuple for the text
        opacity: Text opacity (0.0 to 1.0)
        align: Text alignment ("left", "center", or "right")
        font_path: Optional path to a font file
        
    Returns:
        bytes: The processed image data
    """
    config = TextOverlayConfig(
        text=text,
        font_size=font_size,
        position=position,
        color=color,
        opacity=opacity,
        align=align,
        font_path=font_path
    )
    return await add_text_overlay(image_source, config) 