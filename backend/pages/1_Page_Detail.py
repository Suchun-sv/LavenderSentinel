import streamlit as st
from datetime import datetime
from pathlib import Path

from src.database.paper_repository import PaperRepository
from src.service.llm_service import (
    init_litellm,
    translate_summary,
    summarize_long_markdown,
    ask_paper_question,
    PaperChatState,
)
from src.service.pdf_parser_service import extract_pdf_markdown
from src.service.pdf_download_service import PdfDownloader
from src.config import Config

from streamlit_pdf_viewer import pdf_viewer


# ======================================================
# Cached singletons
# ======================================================

@st.cache_resource
def get_repo() -> PaperRepository:
    return PaperRepository()


@st.cache_resource
def setup_llm():
    init_litellm()
    return True


# ======================================================
# Page entry
# ======================================================

def main():
    st.set_page_config(
        page_title="Paper Detail – LavenderSentinel",
        layout="wide",
    )

    setup_llm()
    repo = get_repo()

    # ---------- Params ----------
    params = st.query_params
    if "id" not in params:
        st.error("❌ 缺少参数 id")
        st.stop()

    paper_id = params["id"]
    paper = repo.get_paper_by_id(paper_id)

    if not paper:
        st.error("📄 未找到该论文")
        return

    # ---------------- Header ----------------
    st.title(paper.title)
    st.caption(f"ArXiv ID: `{paper.id}`")

    st.divider()

    # ---------------- Layout ----------------
    col_left, col_right = st.columns([2, 2])

    # ======================================================
    # LEFT — PDF VIEWER
    # ======================================================
    with col_left:
        st.subheader("📄 Paper PDF")

        pdf_path = Path(Config.pdf_save_path) / f"{paper.id}.pdf"

        if not pdf_path.exists():
            st.warning("⚠ 当前 PDF 尚未下载")
            if st.button("📥 立即下载 PDF"):
                downloader = PdfDownloader()
                downloader.download_one(
                    f"https://arxiv.org/pdf/{paper.id}.pdf",
                    paper.id,
                )
                st.success("已下载 PDF")
                st.rerun()
        else:
            with st.spinner("⏳ 正在加载 PDF..."):
                pdf_viewer(pdf_path, width=900, height=2000)

    # ======================================================
    # RIGHT — INFO / AI PANEL
    # ======================================================
    with col_right:
        # ---------- Abstract ----------
        st.subheader("📝 原文摘要")
        st.write(paper.abstract)

        st.divider()

        # ---------- AI ABSTRACT ----------
        st.markdown("#### 📘 AI Abstract（翻译摘要）")

        if paper.ai_abstract:
            with st.expander("查看 AI 摘要翻译", expanded=False):
                st.write(paper.ai_abstract)

        if st.button("✨ 生成 / 更新 AI 摘要翻译"):
            translated = translate_summary(paper.abstract)

            repo.update_ai_abstract(
                paper_id=paper.id,
                ai_abstract=translated,
                provider=Config.chat_litellm.model,
            )

            st.success("已更新 AI 摘要")
            st.rerun()

        st.divider()

        # ---------- AI SUMMARY ----------
        st.markdown("#### 📕 AI Full-text Summary")

        if paper.ai_summary:
            with st.expander("查看 AI 全文总结", expanded=False):
                st.write(paper.ai_summary)

        if st.button("🧠 生成 / 更新全文总结"):
            if not pdf_path.exists():
                st.error("❌ 需要 PDF 才能生成全文总结，请先下载")
            else:
                with open(pdf_path, "rb") as f:
                    md = extract_pdf_markdown(f.read())

                repo.update_full_text(paper.id, md)

                summary = summarize_long_markdown(
                    md,
                    language=Config.language,
                )

                repo.update_ai_summary(
                    paper_id=paper.id,
                    ai_summary=summary,
                    provider=Config.chat_litellm.model,
                )

                st.success("已生成全文总结")
                st.rerun()

        st.divider()

        # ---------- CHAT ----------
        st.markdown("#### 💬 Paper Chat Assistant")

        if "chat_state" not in st.session_state:
            st.session_state.chat_state = PaperChatState(
                paper_title=paper.title,
                paper_abstract=paper.ai_abstract or paper.abstract,
                paper_full_summary=paper.ai_summary or "",
            )

        for msg in st.session_state.chat_state.history:
            role_icon = "🧑" if msg["role"] == "user" else "🤖"
            st.markdown(f"**{role_icon} {msg['role']}**: {msg['content']}")

        user_q = st.text_area("你的问题：", key="qa_input")

        if st.button("🚀 发送问题"):
            if not st.session_state.chat_state.paper_full_summary:
                st.error("❌ 需要先生成 AI Summary 才能问答")
            else:
                ask_paper_question(
                    st.session_state.chat_state,
                    user_q,
                    language=Config.language,
                )
                st.rerun()


if __name__ == "__main__":
    main()