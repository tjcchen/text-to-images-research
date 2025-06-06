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
        align: str = "center",
        bg_color: Optional[Tuple[int, int, int]] = None,
        bg_opacity: float = 0.8,
        padding: int = 16,
        border_radius: int = 16
    ):
        self.text = text
        self.font_size = font_size
        self.font_path = font_path or self._get_default_font()
        self.position = position
        self.color = color
        self.opacity = opacity
        self.align = align
        self.bg_color = bg_color or (255, 255, 0)  # Default: yellow
        self.bg_opacity = bg_opacity
        self.padding = padding
        self.border_radius = border_radius

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
    Add text overlay to an image, with Xiaohongshu-style background.
    
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
        
        # Calculate text position and size
        text_bbox = draw.textbbox(config.position, config.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate background rectangle
        bg_x = (image.width - text_width) // 2 if config.align == "center" else (
            image.width - text_width - config.position[0] if config.align == "right" else config.position[0]
        )
        bg_y = config.position[1]
        rect_x0 = bg_x - config.padding
        rect_y0 = bg_y - config.padding
        rect_x1 = bg_x + text_width + config.padding
        # Add extra bottom padding for harmony
        extra_bottom_padding = int(config.font_size * 0.4)
        rect_y1 = bg_y + text_height + config.padding + extra_bottom_padding
        
        # Draw rounded rectangle background
        bg_color_with_opacity = (*config.bg_color, int(255 * config.bg_opacity))
        draw.rounded_rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            radius=config.border_radius,
            fill=bg_color_with_opacity
        )
        # Draw text with opacity, center each line
        color_with_opacity = (*config.color, int(255 * config.opacity))
        lines = config.text.split('\n')
        line_spacing = int(config.font_size * 1.2)  # 1.2x font size for spacing
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            if config.align == "center":
                line_x = bg_x + (text_width - line_width) // 2
            elif config.align == "right":
                line_x = bg_x + (text_width - line_width)
            else:  # left
                line_x = bg_x
            line_y = bg_y + i * line_spacing
            # Simulate bold by drawing text multiple times with slight offsets
            for dx, dy in [(0,0), (-1,0), (1,0), (0,-1), (0,1)]:
                draw.text((line_x+dx, line_y+dy), line, font=font, fill=color_with_opacity)
        
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
    font_path: Optional[str] = None,
    bg_color: Optional[Tuple[int, int, int]] = None,
    bg_opacity: float = 0.8,
    padding: int = 16,
    border_radius: int = 16
) -> bytes:
    """
    Convenience function to process an image with text overlay, supporting Xiaohongshu style.
    """
    config = TextOverlayConfig(
        text=text,
        font_size=font_size,
        position=position,
        color=color,
        opacity=opacity,
        align=align,
        font_path=font_path,
        bg_color=bg_color,
        bg_opacity=bg_opacity,
        padding=padding,
        border_radius=border_radius
    )
    return await add_text_overlay(image_source, config) 