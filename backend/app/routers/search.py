"""Search API endpoints."""

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import DbSession
from app.db.repositories import PaperRepository
from app.indexing.handlers import vector_search_handler
from app.models.paper import Paper, PaperWithSimilarity
from app.models.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SimilarPapersRequest,
    SimilarPapersResponse,
)


router = APIRouter()


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db: DbSession,
) -> SearchResponse:
    """
    Perform semantic search on papers using vector similarity.
    
    This endpoint uses the CocoIndex-powered vector database to find
    papers that are semantically similar to the query.
    """
    start_time = time.perf_counter()
    
    # Search vectors
    search_results = await vector_search_handler.search(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
    )
    
    # Fetch full paper data
    repo = PaperRepository(db)
    results = []
    
    for result in search_results:
        paper_orm = await repo.get_by_id(result["paper_id"])
        if paper_orm:
            paper = repo.orm_to_model(paper_orm)
            paper_with_score = PaperWithSimilarity(
                **paper.model_dump(),
                similarity_score=result["score"],
            )
            results.append(SearchResult(
                paper=paper_with_score,
                highlights=[result.get("chunk_text", "")],
            ))
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        took_ms=elapsed_ms,
    )


@router.get("/keyword", response_model=SearchResponse)
async def keyword_search(
    db: DbSession,
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    top_k: int = Query(default=10, ge=1, le=100, description="Number of results"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
) -> SearchResponse:
    """
    Perform keyword-based search on papers.
    
    This is a simpler search that looks for exact keyword matches
    in paper titles, abstracts, and keywords.
    """
    start_time = time.perf_counter()
    
    # TODO: Implement proper keyword search with PostgreSQL full-text search
    # For now, using semantic search as fallback
    search_results = await vector_search_handler.search(
        query=q,
        top_k=top_k,
    )
    
    repo = PaperRepository(db)
    results = []
    
    for result in search_results:
        paper_orm = await repo.get_by_id(result["paper_id"])
        if paper_orm:
            paper = repo.orm_to_model(paper_orm)
            paper_with_score = PaperWithSimilarity(
                **paper.model_dump(),
                similarity_score=result["score"],
            )
            results.append(SearchResult(
                paper=paper_with_score,
                highlights=[],
            ))
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
        took_ms=elapsed_ms,
    )


@router.post("/similar", response_model=SimilarPapersResponse)
async def find_similar_papers(
    request: SimilarPapersRequest,
    db: DbSession,
) -> SimilarPapersResponse:
    """
    Find papers similar to a given paper.
    """
    repo = PaperRepository(db)
    
    # Get source paper
    source_paper_orm = await repo.get_by_id(request.paper_id)
    if not source_paper_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {request.paper_id} not found",
        )
    
    source_paper = repo.orm_to_model(source_paper_orm)
    
    # Find similar papers
    similar_results = await vector_search_handler.find_similar(
        paper_id=request.paper_id,
        top_k=request.top_k,
    )
    
    similar_papers = []
    for result in similar_results:
        paper_orm = await repo.get_by_id(result["paper_id"])
        if paper_orm:
            paper = repo.orm_to_model(paper_orm)
            
            # Optionally exclude same authors
            if request.exclude_same_authors:
                source_author_names = {a.name for a in source_paper.authors}
                paper_author_names = {a.name for a in paper.authors}
                if source_author_names & paper_author_names:
                    continue
            
            similar_papers.append(PaperWithSimilarity(
                **paper.model_dump(),
                similarity_score=result["score"],
            ))
    
    return SimilarPapersResponse(
        source_paper=source_paper,
        similar_papers=similar_papers,
        total=len(similar_papers),
    )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial query"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of suggestions"),
) -> dict:
    """
    Get search suggestions based on partial query.
    """
    # TODO: Implement proper suggestions using keyword index
    return {
        "query": q,
        "suggestions": [],
    }

