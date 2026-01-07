from datetime import datetime, timedelta
import asyncio

from src.crawler.arxiv_client import ArxivClient
from src.storage.json_store import JsonStore
from src.service.pdf_download_service import PdfDownloader
from src.service.pdf_parser_service import extract_pdf_markdown
from src.service.llm_service import llm_completion, llm_chat, translate_summary, ask_paper_question, init_litellm, summarize_long_markdown
from src.config import Config



async def main():
    print("🌿 LavenderSentinel — ArXiv Fetch Running...")

    crawler = ArxivClient()

    keywords = ["vector database", "RAG", "agent"]

    # keywords_papers = crawler.search_papers(
    #     keywords=keywords,
    #     # date_range=(datetime.now() - timedelta(days=30), datetime.now())
    # )
    init_litellm()
    store = JsonStore(Config.paper_save_path)
    # downloader = PdfDownloader(Config.pdf_save_path)

    # total_added = 0
    # download_items = []

    # for kw, papers in keywords_papers.items():
    #     added_papers = store.insert_new_papers(papers)
    #     total_added += len(added_papers)

    #     print(f"📌 Keyword='{kw}' Found={len(papers)} New={len(added_papers)}")
    #     download_items.extend([(p.pdf_url, f"{p.id}.pdf") for p in papers if p.pdf_url])

    for paper in store.get_all_papers()[:1]:
        id = paper.id
        if paper.ai_abstract != "":
            continue
        translated_abstract = translate_summary(paper.abstract)
        # print(translated_abstract)
        store.update_paper_field(id, "ai_abstract", translated_abstract)
        store.update_paper_field(id, "ai_abstract_provider", Config.chat_litellm.model)
        store.update_paper_field(id, "updated_at", datetime.now())
        store.get_paper_by_id(id)
        print(paper.ai_abstract)


    # print(f"\n📚 Total new papers = {total_added}")
    # await downloader.download_all(download_items)
    # print("✅ PDF download complete")

    # index the papers
    # pdf_index_flow.update()
    # layout = extract_pdf_layout(open("cache/pdfs/1112.2155.pdf", "rb").read())
    # print(layout)



    for paper in store.get_all_papers()[:1]:
        id = paper.id
        if paper.full_text != "":
            full_text = paper.full_text
        else:
            full_text = extract_pdf_markdown(open(f"cache/pdfs/{id}.pdf", "rb").read())
            store.update_paper_field(id, "full_text", full_text)
            store.update_paper_field(id, "updated_at", datetime.now())
        ai_summary = summarize_long_markdown(full_text, language=Config.language)
        store.update_paper_field(id, "ai_summary", ai_summary)
        store.update_paper_field(id, "ai_summary_provider", Config.chat_litellm.model)
        store.update_paper_field(id, "updated_at", datetime.now())
        store.get_paper_by_id(id)
        print(paper.ai_summary)

if __name__ == "__main__":
    asyncio.run(main())