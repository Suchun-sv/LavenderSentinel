"""Paper collection service for fetching papers from various sources."""

from datetime import datetime
from typing import AsyncGenerator, Optional

import arxiv
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories import PaperRepository
from app.models.paper import Author, PaperCreate


class PaperCollector:
    """Service for collecting papers from various academic sources."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.repo = PaperRepository(db_session)
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()

    async def collect_from_arxiv(
        self,
        keywords: list[str],
        max_results: int = 100,
        categories: Optional[list[str]] = None,
    ) -> AsyncGenerator[PaperCreate, None]:
        """
        Collect papers from arXiv based on keywords.
        
        Args:
            keywords: Search keywords
            max_results: Maximum number of papers to fetch
            categories: Optional arXiv categories to filter (e.g., ["cs.CL", "cs.LG"])
            
        Yields:
            PaperCreate objects for new papers
        """
        # Build search query
        query_parts = []
        
        # Add keyword search
        keyword_query = " OR ".join(f'all:"{kw}"' for kw in keywords)
        query_parts.append(f"({keyword_query})")
        
        # Add category filter
        if categories:
            cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
            query_parts.append(f"({cat_query})")
        
        query = " AND ".join(query_parts)
        
        # Create arXiv client and search
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=min(max_results, settings.arxiv_max_results),
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        # Fetch and process results
        for result in client.results(search):
            # Check if paper already exists
            arxiv_id = result.entry_id.split("/")[-1]
            if await self.repo.exists(arxiv_id):
                continue
            
            # Extract authors
            authors = [
                Author(name=author.name)
                for author in result.authors
            ]
            
            # Extract categories
            paper_categories = list(result.categories) if result.categories else []
            
            # Create paper
            paper = PaperCreate(
                external_id=arxiv_id,
                title=result.title,
                abstract=result.summary,
                authors=authors,
                keywords=keywords,  # Use search keywords as paper keywords
                categories=paper_categories,
                source="arxiv",
                url=result.entry_id,
                pdf_url=result.pdf_url,
                published_at=result.published,
            )
            
            yield paper

    async def collect_from_semantic_scholar(
        self,
        keywords: list[str],
        max_results: int = 100,
        year_from: Optional[int] = None,
    ) -> AsyncGenerator[PaperCreate, None]:
        """
        Collect papers from Semantic Scholar.
        
        Args:
            keywords: Search keywords
            max_results: Maximum number of papers to fetch
            year_from: Filter papers from this year onwards
            
        Yields:
            PaperCreate objects for new papers
        """
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        query = " ".join(keywords)
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "paperId,title,abstract,authors,year,url,openAccessPdf,fieldsOfStudy",
        }
        
        if year_from:
            params["year"] = f"{year_from}-"
        
        try:
            response = await self.http_client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for paper_data in data.get("data", []):
                paper_id = paper_data.get("paperId")
                if not paper_id:
                    continue
                
                # Check if paper already exists
                if await self.repo.exists(paper_id):
                    continue
                
                # Extract authors
                authors = [
                    Author(name=a.get("name", "Unknown"))
                    for a in paper_data.get("authors", [])
                ]
                
                # Get PDF URL if available
                pdf_url = None
                open_access = paper_data.get("openAccessPdf")
                if open_access:
                    pdf_url = open_access.get("url")
                
                # Create paper
                paper = PaperCreate(
                    external_id=paper_id,
                    title=paper_data.get("title", "Untitled"),
                    abstract=paper_data.get("abstract", ""),
                    authors=authors,
                    keywords=keywords,
                    categories=paper_data.get("fieldsOfStudy", []),
                    source="semantic_scholar",
                    url=paper_data.get("url", f"https://www.semanticscholar.org/paper/{paper_id}"),
                    pdf_url=pdf_url,
                    published_at=datetime(paper_data.get("year", 2024), 1, 1),
                )
                
                yield paper
                
        except httpx.HTTPError as e:
            # Log error but don't raise - allow other sources to continue
            print(f"Error fetching from Semantic Scholar: {e}")

    async def collect_and_save(
        self,
        keywords: list[str],
        sources: Optional[list[str]] = None,
        max_results_per_source: int = 100,
    ) -> dict[str, int]:
        """
        Collect papers from specified sources and save to database.
        
        Args:
            keywords: Search keywords
            sources: List of sources to collect from (default: all)
            max_results_per_source: Max papers per source
            
        Returns:
            Dictionary with count of papers collected per source
        """
        if sources is None:
            sources = ["arxiv", "semantic_scholar"]
        
        results = {}
        
        if "arxiv" in sources:
            count = 0
            async for paper in self.collect_from_arxiv(keywords, max_results_per_source):
                await self.repo.create(paper)
                count += 1
            results["arxiv"] = count
        
        if "semantic_scholar" in sources:
            count = 0
            async for paper in self.collect_from_semantic_scholar(keywords, max_results_per_source):
                try:
                    await self.repo.create(paper)
                    count += 1
                except Exception:
                    # Skip papers that fail to save (e.g., duplicates)
                    pass
            results["semantic_scholar"] = count
        
        return results


async def run_collection_task(
    db_session: AsyncSession,
    keywords: list[str],
) -> dict[str, int]:
    """
    Run paper collection task.
    
    This function can be called from Celery tasks or scheduled jobs.
    """
    collector = PaperCollector(db_session)
    try:
        return await collector.collect_and_save(keywords)
    finally:
        await collector.close()

