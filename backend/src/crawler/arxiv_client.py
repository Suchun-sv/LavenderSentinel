import arxiv
from ..model.paper import Paper

from typing import List, Dict
from datetime import datetime

class ArxivClient:
    def __init__(self):
        self.arxiv_client = arxiv.Client(
            page_size=100,
            delay_seconds=1,
            num_retries=3,
        )

    def search_papers(self, keywords: List[str], max_results: int = 100, sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate) -> Dict[str, List[Paper]]:
        """
        搜索论文，默认按提交时间排序，确保获取到最新的论文。
        """
        keywords_papers: Dict[str, List[Paper]] = {}
        for keyword in keywords:
            # 如果关键词包含空格且没有引号，则包裹引号以进行精确匹配
            query = keyword
            if " " in keyword and not (keyword.startswith('"') and keyword.endswith('"')):
                query = f'"{keyword}"'
            
            keywords_papers[keyword] = []
            search_query = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_by,   
                sort_order=arxiv.SortOrder.Descending,
            )
            results = self.arxiv_client.results(search_query)
            keywords_papers[keyword].extend([self._arxiv_result_to_paper(result, keyword) for result in results])
        return keywords_papers
    
    def _normalize_arxiv_id(self, arxiv_id: str) -> str:
        import re
        last = arxiv_id.split("/")[-1]

        return re.sub(r"v\d+", "", last)
    
    def _get_pdf_url(self, result: arxiv.Result) -> str:
        for link in result.links:
            if "pdf" in link.href.lower():
                return link.href
        return ""
    
    def _arxiv_result_to_paper(self, result: arxiv.Result, keyword: str) -> Paper:
        return Paper(
            id=self._normalize_arxiv_id(result.entry_id),
            title=result.title,
            abstract=result.summary,
            authors=[author.name for author in result.authors],
            pdf_url=self._get_pdf_url(result),
            keywords=[keyword],
            created_at=str(datetime.utcnow().isoformat()),
            updated_at=str(datetime.utcnow().isoformat()),
            arxiv_entry_id=result.entry_id,
            arxiv_updated=result.updated,
            arxiv_published=result.published,
            arxiv_authors=[author.name for author in result.authors],
            arxiv_links=[link.href for link in result.links],
            arxiv_comment=result.comment,
            arxiv_journal_ref=result.journal_ref,
            arxiv_doi=result.doi,
            arxiv_primary_category=result.primary_category,
            arxiv_categories=result.categories,
        )