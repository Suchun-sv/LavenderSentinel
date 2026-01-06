"""Chat API endpoints with RAG support."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse

from app.db.database import DbSession
from app.db.repositories import ChatSessionRepository, PaperRepository
from app.models.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatSession,
    MessageRole,
)
from app.services.chat_service import ChatService


router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: DbSession,
) -> ChatResponse:
    """
    Send a message and get an AI response with RAG context.
    
    This endpoint:
    1. Retrieves relevant paper context using vector search
    2. Generates a response using the LLM with the context
    3. Returns the response with source citations
    """
    chat_service = ChatService(db)
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session = await chat_service.create_session(
            paper_context=request.paper_context
        )
        session_id = session.id
    
    # Generate response
    response = await chat_service.chat(
        session_id=session_id,
        message=request.message,
        paper_context=request.paper_context,
        include_sources=request.include_sources,
        max_tokens=request.max_tokens,
    )
    
    return response


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    db: DbSession,
) -> StreamingResponse:
    """
    Stream a chat response using Server-Sent Events.
    
    This endpoint provides real-time streaming of the AI response
    for a more interactive user experience.
    """
    chat_service = ChatService(db)
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session = await chat_service.create_session(
            paper_context=request.paper_context
        )
        session_id = session.id
    
    async def generate():
        async for chunk in chat_service.chat_stream(
            session_id=session_id,
            message=request.message,
            paper_context=request.paper_context,
            include_sources=request.include_sources,
            max_tokens=request.max_tokens,
        ):
            yield f"data: {chunk.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/sessions", response_model=list[ChatSession])
async def list_sessions(
    db: DbSession,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[ChatSession]:
    """
    List chat sessions for a user.
    """
    repo = ChatSessionRepository(db)
    
    if user_id:
        sessions_orm = await repo.get_user_sessions(user_id, skip, limit)
    else:
        # For now, return empty list if no user_id
        # TODO: Implement proper session listing for anonymous users
        return []
    
    return [repo.orm_to_model(s) for s in sessions_orm]


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    db: DbSession,
) -> ChatSession:
    """
    Get a specific chat session with message history.
    """
    repo = ChatSessionRepository(db)
    session_orm = await repo.get_by_id(session_id)
    
    if not session_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found",
        )
    
    return repo.orm_to_model(session_orm)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: DbSession,
) -> None:
    """
    Delete a chat session.
    """
    repo = ChatSessionRepository(db)
    deleted = await repo.delete(session_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found",
        )


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """
    WebSocket endpoint for real-time chat.
    
    This provides a persistent connection for continuous
    conversation without repeated HTTP requests.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            paper_context = data.get("paper_context", [])
            
            if not message:
                await websocket.send_json({
                    "error": "Message is required",
                })
                continue
            
            # TODO: Implement WebSocket chat with ChatService
            # For now, send a placeholder response
            await websocket.send_json({
                "type": "message",
                "content": f"Received: {message}",
                "session_id": session_id,
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e),
        })
        await websocket.close()

