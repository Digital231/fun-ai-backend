from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from utils.gemini_utils import  generate_response_stream
from fastapi.responses import StreamingResponse

# Create router
router = APIRouter()

# Models for requests
class TestPost(BaseModel):
    message: str

class GeminiRequest(BaseModel):
    prompt: str
    character_name: Optional[str] = None


@router.post("/gemini-stream")
async def gemini_stream_response(request: GeminiRequest):
    return await generate_response_stream(
        request.prompt,
        request.character_name
    )
