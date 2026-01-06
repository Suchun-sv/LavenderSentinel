"""Chat service with RAG support."""

from datetime import datetime
from typing import AsyncGenerator, Optional
from uuid import uuid4

from litellm import acompletion
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories import ChatSessionRepository, PaperRepository
from app.indexing.handlers import vector_search_handler
from app.models.chat import (
    ChatMessage,
    ChatResponse,
    ChatSession,
    MessageRole,
    StreamingChatChunk,
)


class ChatService:
    """Service for handling chat conversations with RAG."""

    SYSTEM_PROMPT = """You are LavenderSentinel, an AI research assistant specialized in helping users understand and explore academic papers.

Your capabilities:
- Explain complex research concepts in clear, accessible language
- Compare and contrast different papers and methodologies
- Identify key contributions, findings, and limitations of papers
- Suggest related papers and research directions
- Answer questions about specific papers in your context

Guidelines:
- Always cite specific papers when referencing their content
- Be precise and accurate - don't make up information
- Acknowledge when you don't have enough information
- Use academic language but remain accessible
- Format responses with clear structure when appropriate

You have access to the following paper context:
{context}

Respond helpfully and accurately to the user's questions."""

    RAG_CONTEXT_TEMPLATE = """
Paper: {title}
---
{content}
---
"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.session_repo = ChatSessionRepository(db_session)
        self.paper_repo = PaperRepository(db_session)

    async def create_session(
        self,
        user_id: Optional[str] = None,
        paper_context: Optional[list[str]] = None,
    ) -> ChatSession:
        """Create a new chat session."""
        session_orm = await self.session_repo.create(
            user_id=user_id,
            paper_context=paper_context,
        )
        return self.session_repo.orm_to_model(session_orm)

    async def _get_rag_context(
        self,
        query: str,
        paper_ids: Optional[list[str]] = None,
        top_k: int = 5,
    ) -> tuple[str, list[dict]]:
        """
        Get relevant context from papers for RAG.
        
        Returns:
            Tuple of (context_string, sources_list)
        """
        # Get relevant chunks from vector search
        chunks = await vector_search_handler.get_context_for_rag(
            query=query,
            paper_ids=paper_ids,
            top_k=top_k,
        )
        
        if not chunks:
            return "", []
        
        # Build context string
        context_parts = []
        sources = []
        
        seen_papers = set()
        for chunk in chunks:
            paper_id = chunk["paper_id"]
            if paper_id in seen_papers:
                continue
            seen_papers.add(paper_id)
            
            context_parts.append(
                self.RAG_CONTEXT_TEMPLATE.format(
                    title=chunk.get("title", "Unknown"),
                    content=chunk.get("text", ""),
                )
            )
            
            sources.append({
                "paper_id": paper_id,
                "title": chunk.get("title", "Unknown"),
                "excerpt": chunk.get("text", "")[:200] + "...",
                "score": chunk.get("score", 0),
            })
        
        context = "\n".join(context_parts)
        return context, sources

    async def _build_messages(
        self,
        session: ChatSession,
        new_message: str,
        context: str,
    ) -> list[dict]:
        """Build message list for LLM API call."""
        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT.format(context=context if context else "No specific papers in context."),
            }
        ]
        
        # Add conversation history (last 10 messages)
        for msg in session.messages[-10:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        
        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message,
        })
        
        return messages

    async def chat(
        self,
        session_id: str,
        message: str,
        paper_context: Optional[list[str]] = None,
        include_sources: bool = True,
        max_tokens: int = 2000,
    ) -> ChatResponse:
        """
        Process a chat message and return response.
        
        Args:
            session_id: Chat session ID
            message: User message
            paper_context: Optional list of paper IDs for context
            include_sources: Whether to include source citations
            max_tokens: Maximum tokens for response
            
        Returns:
            ChatResponse with AI message and sources
        """
        # Get session
        session_orm = await self.session_repo.get_by_id(session_id)
        if not session_orm:
            # Create new session if not found
            session_orm = await self.session_repo.create(paper_context=paper_context)
        
        session = self.session_repo.orm_to_model(session_orm)
        
        # Add user message to session
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=message,
            paper_ids=paper_context or [],
        )
        await self.session_repo.add_message(session_id, user_message)
        
        # Get RAG context
        context, sources = await self._get_rag_context(
            query=message,
            paper_ids=paper_context or session.paper_context,
        )
        
        # Build messages for LLM
        messages = await self._build_messages(session, message, context)
        
        # Generate response
        try:
            response = await acompletion(
                model=settings.llm_model,
                messages=messages,
                api_key=settings.llm_api_key.get_secret_value(),
                base_url=settings.llm_base_url,
                temperature=0.7,
                max_tokens=max_tokens,
            )
            
            assistant_content = response.choices[0].message.content
            
        except Exception as e:
            assistant_content = f"I apologize, but I encountered an error processing your request: {str(e)}"
            sources = []
        
        # Create assistant message
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            paper_ids=[s["paper_id"] for s in sources],
            citations=[s["excerpt"] for s in sources],
        )
        
        # Save assistant message
        await self.session_repo.add_message(session_id, assistant_message)
        
        # Generate follow-up suggestions
        suggested_followups = self._generate_followup_suggestions(message, assistant_content)
        
        return ChatResponse(
            message=assistant_message,
            session_id=session_id,
            sources=sources if include_sources else [],
            suggested_followups=suggested_followups,
        )

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        paper_context: Optional[list[str]] = None,
        include_sources: bool = True,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """
        Stream chat response.
        
        Yields:
            StreamingChatChunk objects with text chunks
        """
        # Get session
        session_orm = await self.session_repo.get_by_id(session_id)
        if not session_orm:
            session_orm = await self.session_repo.create(paper_context=paper_context)
        
        session = self.session_repo.orm_to_model(session_orm)
        
        # Add user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=message,
            paper_ids=paper_context or [],
        )
        await self.session_repo.add_message(session_id, user_message)
        
        # Get RAG context
        context, sources = await self._get_rag_context(
            query=message,
            paper_ids=paper_context or session.paper_context,
        )
        
        # Build messages
        messages = await self._build_messages(session, message, context)
        
        # Stream response
        full_response = ""
        try:
            response = await acompletion(
                model=settings.llm_model,
                messages=messages,
                api_key=settings.llm_api_key.get_secret_value(),
                base_url=settings.llm_base_url,
                temperature=0.7,
                max_tokens=max_tokens,
                stream=True,
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield StreamingChatChunk(chunk=content, done=False)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield StreamingChatChunk(chunk=error_msg, done=False)
            full_response = error_msg
            sources = []
        
        # Save complete assistant message
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=full_response,
            paper_ids=[s["paper_id"] for s in sources],
        )
        await self.session_repo.add_message(session_id, assistant_message)
        
        # Send final chunk with metadata
        yield StreamingChatChunk(
            chunk="",
            done=True,
            session_id=session_id,
            sources=sources if include_sources else None,
        )

    def _generate_followup_suggestions(
        self,
        user_message: str,
        assistant_response: str,
    ) -> list[str]:
        """Generate suggested follow-up questions."""
        # Simple heuristic-based suggestions
        # TODO: Use LLM for more intelligent suggestions
        suggestions = []
        
        if "methodology" in assistant_response.lower():
            suggestions.append("Can you explain the methodology in more detail?")
        
        if "limitation" in assistant_response.lower():
            suggestions.append("What are the potential ways to address these limitations?")
        
        if "result" in assistant_response.lower() or "finding" in assistant_response.lower():
            suggestions.append("How do these findings compare to similar research?")
        
        if not suggestions:
            suggestions = [
                "Can you summarize the key takeaways?",
                "What are the practical applications of this research?",
                "Are there any related papers I should look at?",
            ]
        
        return suggestions[:3]

