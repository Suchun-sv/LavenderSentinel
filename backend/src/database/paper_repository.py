from __future__ import annotations

from typing import List, Optional, Any, Union
from datetime import datetime

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.model.paper import Paper
from src.database.db.session import SessionLocal
from src.database.db.models import PaperRow


class PaperRepository:
    """
    Postgres-only repository for Paper.

    Drop-in replacement for JsonStore with identical semantics.
    All JSONB data stored here is guaranteed to be JSON-serializable.
    """

    # =====================================================
    # Basic CRUD
    # =====================================================

    def save(self, paper: Paper) -> None:
        """
        Insert or update a Paper (full overwrite).
        """
        with SessionLocal() as db:
            row = PaperRow(
                id=paper.id,
                paper=paper.model_dump(mode="json"),  
                title=paper.title,
                created_at=paper.created_at,
                updated_at=datetime.utcnow(),
                arxiv_entry_id=paper.arxiv_entry_id,
                arxiv_published=paper.arxiv_published,
                arxiv_updated=paper.arxiv_updated,
            )
            db.merge(row)
            db.commit()

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get a Paper by id.
        """
        with SessionLocal() as db:
            row = db.get(PaperRow, paper_id)
            if not row:
                return None
            return Paper.model_validate(row.paper)

    def get_all_papers(self) -> List[Paper]:
        """
        Load all papers from database.

        ⚠️ Debug / small dataset only.
        """
        with SessionLocal() as db:
            rows = db.execute(select(PaperRow)).scalars().all()
            return [Paper.model_validate(r.paper) for r in rows]

    # =====================================================
    # Insert-only logic (crawl / ingest)
    # =====================================================

    def insert_new_papers(self, new_papers: List[Paper]) -> List[Paper]:
        """
        Insert only new papers (by Paper.id).
        """
        if not new_papers:
            return []

        paper_ids = [p.id for p in new_papers if p.id]

        with SessionLocal() as db:
            existing_ids = set(
                id_
                for (id_,) in db.execute(
                    select(PaperRow.id).where(PaperRow.id.in_(paper_ids))
                )
            )

            inserted: List[Paper] = []

            for p in new_papers:
                if not p.id or p.id in existing_ids:
                    continue

                row = PaperRow(
                    id=p.id,
                    paper=p.model_dump(mode="json"),
                    title=p.title,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    arxiv_entry_id=p.arxiv_entry_id,
                    arxiv_published=p.arxiv_published,
                    arxiv_updated=p.arxiv_updated,
                )
                db.add(row)
                inserted.append(p)

            db.commit()
            return inserted

    # =====================================================
    # Partial update (enrichment / metadata)
    # =====================================================

    def update_paper_field(self, paper_id: str, field: str, value: Any) -> None:
        """
        Update a single field inside Paper JSON.
        """
        if field not in Paper.model_fields:
            raise ValueError(f"Field '{field}' is not a valid Paper field")

        with SessionLocal() as db:
            row: Optional[PaperRow] = db.get(PaperRow, paper_id)
            if not row:
                return

            paper = dict(row.paper)

            if isinstance(value, datetime):
                value = value.isoformat()

            paper[field] = value
            paper["updated_at"] = datetime.utcnow().isoformat()

            row.paper = paper
            row.updated_at = datetime.utcnow()

            db.commit()

    # =====================================================
    # Pagination & sorting (UI / API)
    # =====================================================

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> List[Paper]:
        """
        List papers with pagination and sorting.
        """
        with SessionLocal() as db:
            query = db.query(PaperRow)

            sort_col = getattr(PaperRow, sort_by, PaperRow.created_at)
            query = (
                query.order_by(sort_col.desc())
                if order == "desc"
                else query.order_by(sort_col.asc())
            )

            rows = (
                query
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return [Paper.model_validate(r.paper) for r in rows]

    # =====================================================
    # Enrichment helpers (daily job)
    # =====================================================

    def list_missing_ai_abstract(self, limit: int = -1) -> List[Paper]:
        """
        List papers without ai_abstract.
        """
        with SessionLocal() as db:
            query = (
                db.query(PaperRow)
                .filter(
                    PaperRow.paper.op("->>")("ai_abstract").is_(None), # JSON null
                )
                .order_by(PaperRow.created_at.asc())
            )

            if limit > 0:
                query = query.limit(limit)

            rows = query.all()
            return [Paper.model_validate(r.paper) for r in rows]
    
    def list_missing_ai_title(self, limit: int = -1) -> List[Paper]:
        """
        List papers without ai_title.
        """
        with SessionLocal() as db:
            query = (
                db.query(PaperRow)
                .filter(PaperRow.paper.op("->>")("ai_title").is_(None))
                .order_by(PaperRow.created_at.asc())
            )

            if limit > 0:
                query = query.limit(limit)

            rows = query.all()
            return [Paper.model_validate(r.paper) for r in rows]
    
    def update_ai_title(self, paper_id: str, ai_title: str, provider: str) -> None:
        """
        Update ai_title and its provider.
        """
        with SessionLocal() as db:
            row = db.get(PaperRow, paper_id)
            if not row:
                return
            row.paper["ai_title"] = ai_title
            row.paper["ai_title_provider"] = provider
            row.updated_at = datetime.utcnow()
            db.commit()

    def update_ai_abstract(
        self,
        paper_id: str,
        ai_abstract: str,
        provider: str,
    ) -> None:
        """
        Update ai_abstract and its provider.
        """
        with SessionLocal() as db:
            row = db.get(PaperRow, paper_id)
            if not row:
                return

            paper = dict(row.paper)
            paper["ai_abstract"] = ai_abstract
            paper["ai_abstract_provider"] = provider
            paper["updated_at"] = datetime.utcnow().isoformat()

            row.paper = paper
            row.updated_at = datetime.utcnow()

            db.commit()

    def list_missing_ai_summary(self, limit: int = 5) -> List[Paper]:
        """
        List papers without ai_summary.
        """
        with SessionLocal() as db:
            rows = (
                db.query(PaperRow)
                .filter(
                    (PaperRow.paper["ai_summary"].is_(None))
                    | (PaperRow.paper.op("->>")("ai_summary") == "")
                )
                .order_by(PaperRow.created_at.asc())
                .limit(limit)
                .all()
            )
            return [Paper.model_validate(r.paper) for r in rows]

    def update_full_text(self, paper_id: str, full_text: str) -> None:
        """
        Update extracted full text.
        """
        self.update_paper_field(paper_id, "full_text", full_text)

    def update_ai_summary(
        self,
        paper_id: str,
        ai_summary: str,
        provider: str,
    ) -> None:
        """
        Update ai_summary and its provider.
        """
        with SessionLocal() as db:
            row = db.get(PaperRow, paper_id)
            if not row:
                return

            paper = dict(row.paper)
            paper["ai_summary"] = ai_summary
            paper["ai_summary_provider"] = provider
            paper["updated_at"] = datetime.utcnow().isoformat()

            row.paper = paper
            row.updated_at = datetime.utcnow()

            db.commit()