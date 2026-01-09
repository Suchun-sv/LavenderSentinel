# src/jobs/daily_arxiv.py

"""
Daily ArXiv fetch & enrichment job.

This module contains PURE job logic.
It is safe to be called by:
- APScheduler
- CLI
- Future Prefect / Airflow
"""

import asyncio
import arxiv
from tqdm import tqdm

from src.crawler.arxiv_client import ArxivClient
from src.database.paper_repository import PaperRepository
from src.service.llm_service import (
    init_litellm,
    translate_summary,
    translate_title,
)
from src.config import Config


def run_daily_arxiv_job() -> None:
    """
    Entry point for scheduler.

    NOTE:
    - APScheduler expects a normal sync function
    - Internally we can still use asyncio
    """
    asyncio.run(_run())


async def _run():
    print("🌿 LavenderSentinel — Daily ArXiv Job started")

    # --- Init ---
    init_litellm()
    crawler = ArxivClient()
    repo = PaperRepository()

    keywords = Config.keywords

    print("🔎 Fetching new papers from arXiv...")

    keyword_results = crawler.search_papers(
        keywords=keywords,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    total_inserted = 0

    for kw, papers in keyword_results.items():
        inserted = repo.insert_new_papers(papers)
        total_inserted += len(inserted)
        print(f"📌 keyword='{kw}' fetched={len(papers)} inserted={len(inserted)}")

    print(f"📚 Total new papers inserted: {total_inserted}")

    # ---------- AI title ----------
    if Config.auto_ai_title:
        print("🤖 Generating AI titles...")

        papers = repo.list_missing_ai_title(limit=-1)
        print(f"🔍 Total papers to process for AI title: {len(papers)}")

        for paper in tqdm(papers, desc="Generating AI titles"):
            try:
                translated = translate_title(paper.title)
                repo.update_ai_title(
                    paper_id=paper.id,
                    ai_title=translated,
                    provider=Config.chat_litellm.model,
                )
            except Exception as e:
                print(f"❌ AI title failed: {paper.id} ({e})")

    # ---------- AI abstract ----------
    if Config.auto_ai_abstract:
        print("🤖 Generating AI abstracts...")

        papers = repo.list_missing_ai_abstract(limit=-1)
        print(f"🔍 Total papers to process for AI abstract: {len(papers)}")

        for paper in tqdm(papers, desc="Generating AI abstracts"):
            try:
                translated = translate_summary(paper.abstract)
                repo.update_ai_abstract(
                    paper_id=paper.id,
                    ai_abstract=translated,
                    provider=Config.chat_litellm.model,
                )
            except Exception as e:
                print(f"❌ AI abstract failed: {paper.id} ({e})")

    print("🎉 Daily ArXiv job finished")