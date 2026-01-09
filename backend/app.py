# app.py
import math
from datetime import datetime

import streamlit as st

from src.config import Config
from src.database.paper_repository import PaperRepository
from src.scheduler.scheduler_service import SchedulerService


# =====================================================
# Global singletons (cached across Streamlit reruns)
# =====================================================

@st.cache_resource
def get_repo() -> PaperRepository:
    """
    Database repository (Postgres).
    """
    return PaperRepository()


@st.cache_resource
def get_scheduler() -> SchedulerService:
    """
    Background scheduler (APScheduler).

    This is started ONCE when Streamlit boots.
    """
    scheduler = SchedulerService()
    scheduler.start()
    return scheduler


# =====================================================
# Helper functions (UI-level logic only)
# =====================================================

def _get_year(paper) -> int | None:
    """
    Try to extract year from paper.
    """
    dt = getattr(paper, "arxiv_published", None)
    if isinstance(dt, datetime):
        return dt.year
    return None


def _get_authors(paper):
    authors = getattr(paper, "authors", None)
    if not authors:
        return []
    return list(authors)


def _filter_papers(papers, search, author_filter, year_range):
    search = (search or "").strip().lower()
    y_min, y_max = year_range if year_range else (None, None)

    filtered = []
    for p in papers:
        # Year filter
        year = _get_year(p)
        if year is not None and y_min is not None and y_max is not None:
            if not (y_min <= year <= y_max):
                continue

        # Author filter
        authors = _get_authors(p)
        if author_filter:
            if not any(a in author_filter for a in authors):
                continue

        # Text search
        if search:
            blob = " ".join([
                p.title or "",
                p.abstract or "",
                " ".join(authors),
            ]).lower()
            if search not in blob:
                continue

        filtered.append(p)

    return filtered


# =====================================================
# Main UI
# =====================================================

def main():
    st.set_page_config(
        page_title="LavenderSentinel – Papers",
        layout="wide",
    )

    st.title("🌿 LavenderSentinel — Paper Library")

    # --- init services ---
    repo = get_repo()
    scheduler = get_scheduler()  # noqa: F841 (intentional side effect)

    # --- load papers from Postgres ---
    papers = repo.list(
        page=1,
        page_size=10_000,  # UI-level fetch; later可改成真正分页
        sort_by="created_at",
        order="desc",
    )

    if not papers:
        st.info("暂无论文，请等待定时任务抓取 arXiv。")
        st.stop()

    # ---------- 搜索 & 筛选 ----------
    with st.container():
        col_search, col_author, col_year = st.columns([2.2, 1.6, 1.6])

        with col_search:
            search = st.text_input(
                "🔍 搜索（标题 / 摘要 / 作者）",
                placeholder="例如：vector database, RAG, transformer...",
            )

        all_authors = sorted(
            {a for p in papers for a in _get_authors(p)}
        )

        with col_author:
            author_filter = st.multiselect(
                "👤 按作者筛选",
                options=all_authors,
                default=[],
            )

        all_years = sorted(
            {y for p in papers if (y := _get_year(p)) is not None}
        )

        if all_years:
            with col_year:
                year_range = st.slider(
                    "📅 按年份范围",
                    min_value=min(all_years),
                    max_value=max(all_years),
                    value=(min(all_years), max(all_years)),
                    step=1,
                )
        else:
            year_range = None

    st.divider()

    # ---------- 过滤 ----------
    filtered = _filter_papers(papers, search, author_filter, year_range)

    total = len(filtered)
    if total == 0:
        st.warning("没有符合条件的论文。")
        st.stop()

    # ---------- 分页 ----------
    with st.sidebar:
        st.markdown("### 📄 列表设置")
        page_size = st.selectbox("每页数量", [5, 10, 20, 50], index=1)
        total_pages = max(1, math.ceil(total / page_size))

        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️") and st.session_state.current_page > 1:
                st.session_state.current_page -= 1
        with col_next:
            if st.button("➡️") and st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
        with col_page:
            st.markdown(
                f"<div style='text-align:center;'>第 {st.session_state.current_page} / {total_pages} 页</div>",
                unsafe_allow_html=True,
            )

    start_idx = (st.session_state.current_page - 1) * page_size
    end_idx = start_idx + page_size
    page_papers = filtered[start_idx:end_idx]

    st.caption(f"共 {total} 篇论文，当前第 {st.session_state.current_page} 页")

    # ---------- 卡片列表 ----------
    cols = st.columns(2)

    for i, p in enumerate(page_papers):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### 📄 {p.title}")
                if p.ai_title:
                    st.caption(f"### 🤖 AI Title: {p.ai_title}")

                meta_bits = []
                year = _get_year(p)
                if year:
                    meta_bits.append(str(year))

                authors = _get_authors(p)
                if authors:
                    meta_bits.append(
                        ", ".join(authors[:3]) + (" ..." if len(authors) > 3 else "")
                    )

                if meta_bits:
                    st.caption(" · ".join(meta_bits))

                # abstract = p.abstract or ""
                preview = p.ai_abstract or p.abstract or ""
                # preview = abstract[:300] + ("…" if len(abstract) > 220 else "")
                st.write(preview or "_(No abstract)_")

                c1, c2 = st.columns([1, 1])
                with c1:
                    st.page_link(
                        "pages/1_Page_Detail.py",
                        label="查看详情",
                        icon="🔍",
                        query_params={"id": p.id},
                    )
                with c2:
                    st.link_button(
                        "📥 PDF",
                        f"https://arxiv.org/pdf/{p.id}.pdf",
                        use_container_width=True,
                    )


if __name__ == "__main__":
    main()