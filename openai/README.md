# Text to Images Generator with OpenAI

This FastAPI application provides an API for generating images from text prompts using OpenAI's DALL-E models.

## Features

- Generate images from text prompts
- Customize image size, quality, and style
- Support for multiple image generation
- Response in URL or base64 format

## Prerequisites

- Python 3.8+
- OpenAI API key

## Setup

1. Clone the repository (if you haven't already)

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root based on `.env.example`:
   ```
   cp .env.example .env
   ```

4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

Start the server with:

```
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Generate Images

```
POST /api/images/generate
```

Request body:
```json
{
  "prompt": "A sunset over mountains with a lake in the foreground",
  "n": 1,
  "size": "1024x1024",
  "response_format": "url",
  "style": "vivid",
  "quality": "standard"
}
```

Parameters:
- `prompt`: Text description of the desired image
- `n`: Number of images to generate (1-10)
- `size`: Size of the generated images (256x256, 512x512, 1024x1024, 1792x1024, or 1024x1792)
- `response_format`: Format of the generated images (url or b64_json)
- `style`: Style of the generated images (vivid or natural)
- `quality`: Quality of the generated images (standard or hd)

### Example Usage with curl

```bash
curl -X 'POST' \
  'http://localhost:8000/api/images/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "A sunset over mountains with a lake in the foreground",
  "n": 1,
  "size": "1024x1024",
  "response_format": "url",
  "style": "vivid",
  "quality": "standard"
}'
```

Example response:
```json
{
  "images": [
    "https://oaidalleapiprodscus.blob.core.windows.net/private/..."
  ],
  "prompt": "A sunset over mountains with a lake in the foreground"
}
```

## License

MIT
