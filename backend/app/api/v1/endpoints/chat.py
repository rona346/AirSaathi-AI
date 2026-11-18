from fastapi import APIRouter, Body, HTTPException
from backend.app.models.chat import ChatRequest, ChatResponse
from backend.app.models.response import ApiResponse
from backend.app.services.chat_service import ChatService

router = APIRouter()


@router.post("/message", response_model=ApiResponse[ChatResponse])
def send_chat_message(
    request: ChatRequest = Body(...),
):
    """
    Intelligent bilingual conversational assistant for urban air quality,
    health precautions, indoor air filtration, and daily smog navigation.
    Context-aware with real-time CPCB telemetry injection.
    """
    clean_msg = request.message.strip()
    if not clean_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty or whitespace only.")
    if len(clean_msg) > 1000:
        raise HTTPException(status_code=400, detail="Message exceeds maximum allowed length of 1000 characters.")

    request.message = clean_msg
    response = ChatService.process_chat_message(request)

    return ApiResponse(
        success=True,
        message="Chat response generated successfully",
        data=response,
        is_demo_data=response.context_used.is_demo_data,
    )
