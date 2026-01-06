"""Repository layer for database operations."""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PaperORM, UserORM, ChatSessionORM, PaperSummaryORM
from app.models.paper import Paper, PaperCreate, PaperUpdate, Author
from app.models.chat import ChatSession, ChatMessage


class PaperRepository:
    """Repository for paper database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, paper: PaperCreate) -> PaperORM:
        """Create a new paper."""
        db_paper = PaperORM(
            external_id=paper.external_id,
            title=paper.title,
            abstract=paper.abstract,
            authors=[author.model_dump() for author in paper.authors],
            keywords=paper.keywords,
            categories=paper.categories,
            source=paper.source,
            url=str(paper.url),
            pdf_url=str(paper.pdf_url) if paper.pdf_url else None,
            published_at=paper.published_at,
        )
        self.session.add(db_paper)
        await self.session.flush()
        return db_paper

    async def get_by_id(self, paper_id: str) -> Optional[PaperORM]:
        """Get a paper by ID."""
        result = await self.session.execute(
            select(PaperORM).where(PaperORM.id == paper_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Optional[PaperORM]:
        """Get a paper by external ID."""
        result = await self.session.execute(
            select(PaperORM).where(PaperORM.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        source: Optional[str] = None,
        categories: Optional[list[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Sequence[PaperORM]:
        """Get papers with optional filters."""
        query = select(PaperORM)

        conditions = []
        if source:
            conditions.append(PaperORM.source == source)
        if date_from:
            conditions.append(PaperORM.published_at >= date_from)
        if date_to:
            conditions.append(PaperORM.published_at <= date_to)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(PaperORM.published_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, paper_id: str, paper_update: PaperUpdate) -> Optional[PaperORM]:
        """Update a paper."""
        db_paper = await self.get_by_id(paper_id)
        if not db_paper:
            return None

        update_data = paper_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if field in ("url", "pdf_url"):
                    value = str(value)
                setattr(db_paper, field, value)

        await self.session.flush()
        return db_paper

    async def delete(self, paper_id: str) -> bool:
        """Delete a paper."""
        db_paper = await self.get_by_id(paper_id)
        if not db_paper:
            return False
        await self.session.delete(db_paper)
        return True

    async def count(self) -> int:
        """Get total paper count."""
        result = await self.session.execute(select(func.count(PaperORM.id)))
        return result.scalar_one()

    async def exists(self, external_id: str) -> bool:
        """Check if a paper exists by external ID."""
        result = await self.session.execute(
            select(func.count(PaperORM.id)).where(
                PaperORM.external_id == external_id
            )
        )
        return result.scalar_one() > 0

    async def get_papers_without_summary(self, limit: int = 10) -> Sequence[PaperORM]:
        """Get papers that don't have a summary yet."""
        result = await self.session.execute(
            select(PaperORM)
            .where(PaperORM.summary.is_(None))
            .order_by(PaperORM.collected_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def update_summary(
        self,
        paper_id: str,
        summary: str,
        key_points: list[str],
    ) -> Optional[PaperORM]:
        """Update paper summary."""
        db_paper = await self.get_by_id(paper_id)
        if not db_paper:
            return None

        db_paper.summary = summary
        db_paper.key_points = key_points
        db_paper.summary_generated_at = datetime.utcnow()

        await self.session.flush()
        return db_paper

    def orm_to_model(self, paper_orm: PaperORM) -> Paper:
        """Convert ORM model to Pydantic model."""
        return Paper(
            id=paper_orm.id,
            external_id=paper_orm.external_id,
            title=paper_orm.title,
            abstract=paper_orm.abstract,
            authors=[Author(**a) for a in paper_orm.authors],
            keywords=paper_orm.keywords,
            categories=paper_orm.categories,
            source=paper_orm.source,
            url=paper_orm.url,
            pdf_url=paper_orm.pdf_url,
            published_at=paper_orm.published_at,
            collected_at=paper_orm.collected_at,
            updated_at=paper_orm.updated_at,
            summary=paper_orm.summary,
            key_points=paper_orm.key_points,
        )


class ChatSessionRepository:
    """Repository for chat session database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: Optional[str] = None,
        paper_context: Optional[list[str]] = None,
    ) -> ChatSessionORM:
        """Create a new chat session."""
        db_session = ChatSessionORM(
            user_id=user_id,
            paper_context=paper_context or [],
            messages=[],
        )
        self.session.add(db_session)
        await self.session.flush()
        return db_session

    async def get_by_id(self, session_id: str) -> Optional[ChatSessionORM]:
        """Get a chat session by ID."""
        result = await self.session.execute(
            select(ChatSessionORM).where(ChatSessionORM.id == session_id)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        session_id: str,
        message: ChatMessage,
    ) -> Optional[ChatSessionORM]:
        """Add a message to a chat session."""
        db_session = await self.get_by_id(session_id)
        if not db_session:
            return None

        messages = list(db_session.messages)
        messages.append(message.model_dump(mode="json"))
        db_session.messages = messages
        db_session.updated_at = datetime.utcnow()

        await self.session.flush()
        return db_session

    async def get_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ChatSessionORM]:
        """Get chat sessions for a user."""
        result = await self.session.execute(
            select(ChatSessionORM)
            .where(ChatSessionORM.user_id == user_id)
            .order_by(ChatSessionORM.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_title(
        self,
        session_id: str,
        title: str,
    ) -> Optional[ChatSessionORM]:
        """Update session title."""
        db_session = await self.get_by_id(session_id)
        if not db_session:
            return None

        db_session.title = title
        await self.session.flush()
        return db_session

    async def delete(self, session_id: str) -> bool:
        """Delete a chat session."""
        db_session = await self.get_by_id(session_id)
        if not db_session:
            return False
        await self.session.delete(db_session)
        return True

    def orm_to_model(self, session_orm: ChatSessionORM) -> ChatSession:
        """Convert ORM model to Pydantic model."""
        return ChatSession(
            id=session_orm.id,
            title=session_orm.title,
            messages=[ChatMessage(**m) for m in session_orm.messages],
            paper_context=session_orm.paper_context,
            created_at=session_orm.created_at,
            updated_at=session_orm.updated_at,
        )

