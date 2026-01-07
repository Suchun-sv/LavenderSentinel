"""
SQLAlchemy ORM 模型

定义的表:
- papers: 论文表 (id, title, abstract, authors, ...)
- chat_sessions: 对话会话表
- paper_summaries: AI 摘要表

注意: 这些是数据库表模型，不是 Pydantic 模型
"""


# app/db/models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    func,
    JSON,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# --------- Paper 表 --------- #

class Paper(Base):
    """
    papers: 论文表

    存放结构化元数据，向量本身存 Qdrant, 只在这里保留 collection / point_id 做关联。
    """
    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # 比如 arxiv_id / DOI / 自己的 external key
    external_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        unique=True,
        nullable=True,
        index=True,
        doc="外部ID，如 arxiv_id / DOI / internal key",
    )

    title: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        index=True,
    )

    abstract: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # 作者列表，简单用 JSON 存 ["A. Author", "B. Author", ...]
    authors: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="arxiv",  # arxiv / openreview / custom
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    # —— Qdrant 相关信息（向量本身不在 Postgres）——
    qdrant_collection: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Qdrant collection 名称，用于定位向量库",
    )

    qdrant_point_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="在 Qdrant 中的 point_id，用字符串存（可用 UUID 字符串）",
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 关系：一个 Paper 对应多个摘要 / 多个会话
    summaries: Mapped[List["PaperSummary"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )


# --------- ChatSession 表 --------- #

class ChatSession(Base):
    """
    chat_sessions: 对话会话表

    一次“和某篇论文聊天”的会话就是一条记录。
    后续可以扩展 chat_messages 表来存每一条消息。
    """
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # 如果有用户系统，这里可以挂 user_id（暂时用字符串占位）
    user_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        doc="可选：用户ID（如有用户系统的话）",
    )

    paper_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("papers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        doc="会话标题，方便在前端展示/选择",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Redis 相关的 key 可以在代码层约定，不需要写入 DB
    # 例如: f"chat_ctx:{chat_session_id}" → 存在 Redis 里

    paper: Mapped[Optional["Paper"]] = relationship(
        back_populates="chat_sessions",
    )


# --------- PaperSummary 表 --------- #

class PaperSummary(Base):
    """
    paper_summaries: AI 摘要表

    同一篇 paper 可以有多种摘要（不同粒度、不同语言、不同模型）。
    """
    __tablename__ = "paper_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    paper_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 摘要类型：例如 one_line / short / detailed / method / contribution ...
    summary_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="short",
    )

    # 语言：en / zh / ...
    language: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="en",
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="生成该摘要的 LLM/模型名称",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="summaries",
    )
