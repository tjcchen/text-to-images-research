from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from typing import List, Optional

from app.routers import image_router
from app.config import get_settings

# Get application settings
settings = get_settings()

app = FastAPI(
    title="Text to Image API",
    description="API for generating images from text using OpenAI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Text to Image API. Use /docs to view the API documentation."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
