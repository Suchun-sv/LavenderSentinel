"""Search-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.paper import Paper, PaperWithSimilarity


class SearchFilters(BaseModel):
    """Filters for paper search."""

    categories: Optional[list[str]] = Field(None, description="Filter by categories")
    keywords: Optional[list[str]] = Field(None, description="Filter by keywords")
    sources: Optional[list[str]] = Field(None, description="Filter by sources")
    date_from: Optional[datetime] = Field(None, description="Filter papers from this date")
    date_to: Optional[datetime] = Field(None, description="Filter papers until this date")
    authors: Optional[list[str]] = Field(None, description="Filter by author names")


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    filters: Optional[SearchFilters] = Field(None, description="Optional search filters")
    include_summary: bool = Field(default=False, description="Include AI summary in results")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query": "transformer attention mechanism",
            "top_k": 10,
            "filters": {
                "categories": ["cs.CL", "cs.LG"],
                "date_from": "2023-01-01T00:00:00Z"
            }
        }
    })


class SearchResult(BaseModel):
    """Individual search result."""

    paper: PaperWithSimilarity
    highlights: list[str] = Field(default_factory=list, description="Matching text highlights")
    
    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Search response model."""

    query: str = Field(..., description="Original query")
    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    total: int = Field(..., description="Total number of results")
    took_ms: float = Field(..., description="Search duration in milliseconds")

    model_config = ConfigDict(from_attributes=True)


class SimilarPapersRequest(BaseModel):
    """Request for finding similar papers."""

    paper_id: str = Field(..., description="Source paper ID")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of similar papers")
    exclude_same_authors: bool = Field(default=False, description="Exclude papers by same authors")


class SimilarPapersResponse(BaseModel):
    """Response for similar papers query."""

    source_paper: Paper
    similar_papers: list[PaperWithSimilarity]
    total: int

