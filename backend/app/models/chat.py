"""Chat-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class MessageRole(str, Enum):
    """Chat message role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Message ID")
    role: MessageRole = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Optional metadata
    paper_ids: list[str] = Field(default_factory=list, description="Referenced paper IDs")
    citations: list[str] = Field(default_factory=list, description="Citation snippets from papers")

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for context continuity")
    paper_context: list[str] = Field(
        default_factory=list,
        description="Paper IDs to use as context for RAG"
    )
    include_sources: bool = Field(
        default=True,
        description="Whether to include source citations in response"
    )
    max_tokens: int = Field(default=2000, ge=100, le=8000, description="Max response tokens")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "message": "Explain the key contributions of this paper",
            "session_id": "abc123",
            "paper_context": ["paper-id-1", "paper-id-2"],
            "include_sources": True
        }
    })


class ChatResponse(BaseModel):
    """Chat response model."""

    message: ChatMessage
    session_id: str = Field(..., description="Session ID for follow-up messages")
    sources: list[dict] = Field(
        default_factory=list,
        description="Source papers and relevant excerpts"
    )
    suggested_followups: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions"
    )

    model_config = ConfigDict(from_attributes=True)


class ChatSession(BaseModel):
    """Chat session model for conversation history."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Session ID")
    title: Optional[str] = Field(None, description="Session title (auto-generated)")
    messages: list[ChatMessage] = Field(default_factory=list, description="Message history")
    paper_context: list[str] = Field(default_factory=list, description="Papers in context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class StreamingChatChunk(BaseModel):
    """Streaming chat response chunk for SSE."""

    chunk: str = Field(..., description="Text chunk")
    done: bool = Field(default=False, description="Whether this is the final chunk")
    session_id: Optional[str] = Field(None, description="Session ID (only in final chunk)")
    sources: Optional[list[dict]] = Field(None, description="Sources (only in final chunk)")

