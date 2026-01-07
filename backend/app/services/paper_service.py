"""
论文服务

职责:
1. 从 arXiv、Semantic Scholar 采集论文
2. 论文 CRUD 操作
3. 调用 LLM 生成摘要

主要方法:
- collect_from_arxiv(keywords): 从 arXiv 采集
- create_paper(paper_data): 创建论文
- get_paper(paper_id): 获取论文
- generate_summary(paper_id): 生成 AI 摘要
"""

# TODO: 实现论文服务

from abc import ABC
from abc import abstractmethod
from typing import List, Tuple
from datetime import datetime
from app.models.paper import Paper

class PaperSearcher(ABC):

    @abstractmethod
    def parse(self, keywords: List[str], date_range: Tuple[datetime, datetime]) -> List[Paper]:
        """
        Parse papers from the source according to the keywords and date range
        """
        pass

class ArxivPaperSearcher(PaperSearcher):
    """
    Arxiv paper searcher
    """
    def parse(self, keywords: List[str], date_range: Tuple[datetime, datetime]) -> List[Paper]:
        """
        Parse papers from arXiv according to the keywords and date range
        """
        import arxiv
        papers = arxiv.Search(
            query=keywords,
            max_results=100,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
        return [Paper(title=paper.title, abstract=paper.summary, authors=paper.authors, links=paper.links, pdf_url=paper.pdf_url) for paper in papers]