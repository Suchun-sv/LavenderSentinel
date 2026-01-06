"""Paper summarization service using LLM."""

from datetime import datetime
from typing import Optional

from litellm import acompletion
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repositories import PaperRepository
from app.models.paper import PaperSummary


class SummaryResult(BaseModel):
    """Structured summary result from LLM."""
    
    summary: str
    key_points: list[str]
    methodology: Optional[str] = None
    findings: Optional[str] = None
    limitations: Optional[str] = None


class PaperSummarizer:
    """Service for generating paper summaries using LLM."""

    SUMMARY_PROMPT = """You are an expert academic researcher. Analyze the following research paper and provide a comprehensive summary.

Paper Title: {title}

Abstract:
{abstract}

Please provide:
1. A concise summary (2-3 paragraphs) explaining the paper's main contribution
2. 3-5 key points/takeaways
3. A brief description of the methodology used
4. The main findings/results
5. Any noted limitations

Format your response as JSON with the following structure:
{{
    "summary": "...",
    "key_points": ["...", "...", "..."],
    "methodology": "...",
    "findings": "...",
    "limitations": "..."
}}

Be objective and accurate. Only include information that is clearly stated or directly inferable from the abstract."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.repo = PaperRepository(db_session)

    async def summarize_paper(
        self,
        paper_id: str,
        force: bool = False,
    ) -> Optional[PaperSummary]:
        """
        Generate a summary for a paper.
        
        Args:
            paper_id: ID of the paper to summarize
            force: If True, regenerate even if summary exists
            
        Returns:
            PaperSummary object or None if paper not found
        """
        # Get paper
        paper_orm = await self.repo.get_by_id(paper_id)
        if not paper_orm:
            return None
        
        # Check if summary already exists
        if paper_orm.summary and not force:
            return PaperSummary(
                paper_id=paper_id,
                summary=paper_orm.summary,
                key_points=paper_orm.key_points,
                generated_at=paper_orm.summary_generated_at or datetime.utcnow(),
                model_used=settings.llm_model,
            )
        
        # Generate summary using LLM
        prompt = self.SUMMARY_PROMPT.format(
            title=paper_orm.title,
            abstract=paper_orm.abstract,
        )
        
        try:
            response = await acompletion(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that analyzes academic papers."},
                    {"role": "user", "content": prompt},
                ],
                api_key=settings.llm_api_key.get_secret_value(),
                base_url=settings.llm_base_url,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000,
            )
            
            # Parse response
            import json
            content = response.choices[0].message.content
            result_data = json.loads(content)
            result = SummaryResult(**result_data)
            
            # Update paper in database
            await self.repo.update_summary(
                paper_id=paper_id,
                summary=result.summary,
                key_points=result.key_points,
            )
            
            return PaperSummary(
                paper_id=paper_id,
                summary=result.summary,
                key_points=result.key_points,
                methodology=result.methodology,
                findings=result.findings,
                limitations=result.limitations,
                generated_at=datetime.utcnow(),
                model_used=settings.llm_model,
            )
            
        except Exception as e:
            # Log error and return None
            print(f"Error generating summary for paper {paper_id}: {e}")
            return None

    async def summarize_batch(
        self,
        paper_ids: list[str],
        force: bool = False,
    ) -> list[PaperSummary]:
        """
        Generate summaries for multiple papers.
        
        Args:
            paper_ids: List of paper IDs to summarize
            force: If True, regenerate even if summaries exist
            
        Returns:
            List of PaperSummary objects
        """
        summaries = []
        for paper_id in paper_ids:
            summary = await self.summarize_paper(paper_id, force)
            if summary:
                summaries.append(summary)
        return summaries

    async def summarize_pending(
        self,
        limit: int = 10,
    ) -> list[PaperSummary]:
        """
        Generate summaries for papers that don't have one yet.
        
        Args:
            limit: Maximum number of papers to process
            
        Returns:
            List of generated PaperSummary objects
        """
        # Get papers without summaries
        papers = await self.repo.get_papers_without_summary(limit)
        
        summaries = []
        for paper in papers:
            summary = await self.summarize_paper(paper.id)
            if summary:
                summaries.append(summary)
        
        return summaries

