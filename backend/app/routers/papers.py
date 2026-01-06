"""Paper management API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.db.database import DbSession
from app.db.repositories import PaperRepository
from app.models.paper import Paper, PaperCreate, PaperUpdate


router = APIRouter()


class PaperListResponse(BaseModel):
    """Response model for paper list."""

    papers: list[Paper]
    total: int
    page: int
    page_size: int


class PaperStatsResponse(BaseModel):
    """Response model for paper statistics."""

    total_papers: int
    papers_with_summary: int
    sources: dict[str, int]


@router.get("", response_model=PaperListResponse)
async def list_papers(
    db: DbSession,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    date_from: Optional[datetime] = Query(default=None, description="Filter from date"),
    date_to: Optional[datetime] = Query(default=None, description="Filter to date"),
) -> PaperListResponse:
    """
    List papers with pagination and optional filters.
    """
    repo = PaperRepository(db)
    
    skip = (page - 1) * page_size
    papers_orm = await repo.get_all(
        skip=skip,
        limit=page_size,
        source=source,
        date_from=date_from,
        date_to=date_to,
    )
    
    total = await repo.count()
    papers = [repo.orm_to_model(p) for p in papers_orm]
    
    return PaperListResponse(
        papers=papers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=PaperStatsResponse)
async def get_paper_stats(db: DbSession) -> PaperStatsResponse:
    """
    Get paper collection statistics.
    """
    repo = PaperRepository(db)
    total = await repo.count()
    
    # TODO: Implement proper stats queries
    return PaperStatsResponse(
        total_papers=total,
        papers_with_summary=0,
        sources={},
    )


@router.get("/{paper_id}", response_model=Paper)
async def get_paper(
    paper_id: str,
    db: DbSession,
) -> Paper:
    """
    Get a specific paper by ID.
    """
    repo = PaperRepository(db)
    paper_orm = await repo.get_by_id(paper_id)
    
    if not paper_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {paper_id} not found",
        )
    
    return repo.orm_to_model(paper_orm)


@router.post("", response_model=Paper, status_code=status.HTTP_201_CREATED)
async def create_paper(
    paper: PaperCreate,
    db: DbSession,
) -> Paper:
    """
    Create a new paper entry.
    """
    repo = PaperRepository(db)
    
    # Check if paper already exists
    if await repo.exists(paper.external_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Paper with external ID {paper.external_id} already exists",
        )
    
    paper_orm = await repo.create(paper)
    return repo.orm_to_model(paper_orm)


@router.patch("/{paper_id}", response_model=Paper)
async def update_paper(
    paper_id: str,
    paper_update: PaperUpdate,
    db: DbSession,
) -> Paper:
    """
    Update a paper's information.
    """
    repo = PaperRepository(db)
    paper_orm = await repo.update(paper_id, paper_update)
    
    if not paper_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {paper_id} not found",
        )
    
    return repo.orm_to_model(paper_orm)


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: str,
    db: DbSession,
) -> None:
    """
    Delete a paper.
    """
    repo = PaperRepository(db)
    deleted = await repo.delete(paper_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {paper_id} not found",
        )


@router.post("/{paper_id}/summarize", response_model=Paper)
async def generate_paper_summary(
    paper_id: str,
    db: DbSession,
) -> Paper:
    """
    Generate AI summary for a paper.
    """
    repo = PaperRepository(db)
    paper_orm = await repo.get_by_id(paper_id)
    
    if not paper_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {paper_id} not found",
        )
    
    # TODO: Integrate with summarizer service
    # For now, return the paper as-is
    return repo.orm_to_model(paper_orm)

