from datetime import datetime, timedelta
from src.crawler import ArxivClient

if __name__ == "__main__":
    crawler = ArxivClient()
    # papers = crawler.search_papers(keywords=["vector database", "RAG", "agent"], date_range=(datetime.now() - timedelta(days=30), datetime.now()))
    papers = crawler.search_papers(keywords=["vector database"], date_range=(datetime.now() - timedelta(days=30), datetime.now()))
    print(papers)