"""Paper-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class Author(BaseModel):
    """Author information model."""

    name: str = Field(..., min_length=1, max_length=200, description="Author's full name")
    affiliation: Optional[str] = Field(None, max_length=500, description="Author's affiliation")
    email: Optional[str] = Field(None, description="Author's email address")

    model_config = ConfigDict(from_attributes=True)


class PaperBase(BaseModel):
    """Base paper model with common fields."""

    title: str = Field(..., min_length=1, max_length=500, description="Paper title")
    abstract: str = Field(..., min_length=1, description="Paper abstract")
    authors: list[Author] = Field(default_factory=list, description="List of authors")
    keywords: list[str] = Field(default_factory=list, description="Paper keywords")
    categories: list[str] = Field(default_factory=list, description="arXiv categories")
    source: str = Field(..., description="Paper source (arxiv, semantic_scholar, etc.)")
    url: HttpUrl = Field(..., description="URL to the paper page")
    pdf_url: Optional[HttpUrl] = Field(None, description="Direct PDF download URL")


class PaperCreate(PaperBase):
    """Model for creating a new paper."""

    external_id: str = Field(..., description="External ID from source (e.g., arXiv ID)")
    published_at: datetime = Field(..., description="Publication date")


class PaperUpdate(BaseModel):
    """Model for updating an existing paper."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = Field(None, min_length=1)
    keywords: Optional[list[str]] = None
    categories: Optional[list[str]] = None
    pdf_url: Optional[HttpUrl] = None


class Paper(PaperBase):
    """Complete paper model with all fields."""

    id: str = Field(..., description="Internal paper ID (UUID)")
    external_id: str = Field(..., description="External ID from source")
    published_at: datetime = Field(..., description="Publication date")
    collected_at: datetime = Field(..., description="When the paper was collected")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Optional fields that may be populated later
    summary: Optional[str] = Field(None, description="AI-generated summary")
    key_points: list[str] = Field(default_factory=list, description="Key points extracted")

    model_config = ConfigDict(from_attributes=True)


class PaperSummary(BaseModel):
    """AI-generated paper summary model."""

    paper_id: str = Field(..., description="Associated paper ID")
    summary: str = Field(..., description="Generated summary text")
    key_points: list[str] = Field(default_factory=list, description="Key points")
    methodology: Optional[str] = Field(None, description="Methodology summary")
    findings: Optional[str] = Field(None, description="Main findings")
    limitations: Optional[str] = Field(None, description="Noted limitations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(..., description="LLM model used for generation")

    model_config = ConfigDict(from_attributes=True)


class PaperWithSimilarity(Paper):
    """Paper model with similarity score for search results."""

    similarity_score: float = Field(..., ge=0, le=1, description="Cosine similarity score")

