"""Papers listing page view."""

import streamlit as st
from api_client import get_api_client


def render():
    """Render the papers page."""
    st.markdown('<h1 class="main-header">📚 Papers Collection</h1>', unsafe_allow_html=True)
    st.markdown("Browse all papers in your collection")
    
    st.divider()
    
    api = get_api_client()
    
    # Filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        page_size = st.selectbox("Per page", [10, 20, 50], index=1)
    with col2:
        source_filter = st.selectbox("Source", ["All", "arxiv", "semantic_scholar"], index=0)
    
    # Initialize page in session state
    if "papers_page" not in st.session_state:
        st.session_state.papers_page = 1
    
    # Fetch papers
    source = source_filter if source_filter != "All" else None
    papers_data = api.list_papers(
        page=st.session_state.papers_page,
        page_size=page_size,
        source=source
    )
    
    papers = papers_data.get("papers", [])
    total = papers_data.get("total", 0)
    total_pages = (total + page_size - 1) // page_size
    
    # Stats
    st.info(f"📊 Showing {len(papers)} of {total} papers (Page {st.session_state.papers_page}/{max(1, total_pages)})")
    
    st.divider()
    
    # Papers list
    if papers:
        for paper in papers:
            with st.container():
                # Title
                st.markdown(f"### {paper.get('title', 'Untitled')}")
                
                # Authors
                authors = paper.get("authors", [])
                author_names = ", ".join([a.get("name", "") for a in authors[:5]])
                if len(authors) > 5:
                    author_names += f" +{len(authors) - 5} more"
                st.caption(f"👤 {author_names}")
                
                # Abstract (expandable)
                abstract = paper.get("abstract", "")
                with st.expander("📄 Abstract"):
                    st.markdown(abstract)
                
                # Summary if available
                summary = paper.get("summary")
                if summary:
                    with st.expander("🤖 AI Summary"):
                        st.markdown(summary)
                        key_points = paper.get("key_points", [])
                        if key_points:
                            st.markdown("**Key Points:**")
                            for point in key_points:
                                st.markdown(f"- {point}")
                
                # Metadata row
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.caption(f"📅 {paper.get('published_at', 'Unknown')[:10]}")
                with col_b:
                    st.caption(f"📂 {paper.get('source', 'Unknown')}")
                with col_c:
                    url = paper.get("url", "")
                    if url:
                        st.markdown(f"[🔗 Source]({url})")
                with col_d:
                    pdf_url = paper.get("pdf_url")
                    if pdf_url:
                        st.markdown(f"[📥 PDF]({pdf_url})")
                
                # Categories
                categories = paper.get("categories", [])
                if categories:
                    badges_html = "".join([f'<span class="badge">{cat}</span>' for cat in categories])
                    st.markdown(badges_html, unsafe_allow_html=True)
                
                # Keywords
                keywords = paper.get("keywords", [])
                if keywords:
                    st.caption(f"🏷️ Keywords: {', '.join(keywords[:5])}")
                
                # Actions
                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if st.button("💬 Chat", key=f"chat_{paper.get('id')}", use_container_width=True):
                        st.session_state.chat_paper_id = paper.get("id")
                        st.session_state.chat_paper_title = paper.get("title")
                        st.success(f"Added to chat context: {paper.get('title')[:50]}...")
                with col_act2:
                    if st.button("🔍 Similar", key=f"similar_{paper.get('id')}", use_container_width=True):
                        st.session_state.show_similar = paper.get("id")
                with col_act3:
                    if st.button("📝 Summary", key=f"summary_{paper.get('id')}", use_container_width=True):
                        st.info("Summary generation coming soon!")
                
                st.divider()
        
        # Pagination
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("← Previous", disabled=st.session_state.papers_page <= 1, use_container_width=True):
                st.session_state.papers_page -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<center>Page {st.session_state.papers_page} of {max(1, total_pages)}</center>", unsafe_allow_html=True)
        with col_next:
            if st.button("Next →", disabled=st.session_state.papers_page >= total_pages, use_container_width=True):
                st.session_state.papers_page += 1
                st.rerun()
    
    else:
        st.warning("No papers found in collection")
        st.markdown("""
        ### Getting Started
        
        Papers will appear here once they are collected. You can:
        1. Configure keywords in settings to auto-collect papers
        2. Use the API to add papers programmatically
        3. Import papers from arXiv or Semantic Scholar
        """)
    
    # Show similar papers modal
    if "show_similar" in st.session_state and st.session_state.show_similar:
        paper_id = st.session_state.show_similar
        with st.expander("🔍 Similar Papers", expanded=True):
            similar_data = api.find_similar_papers(paper_id, top_k=5)
            similar_papers = similar_data.get("similar_papers", [])
            
            if similar_papers:
                for sp in similar_papers:
                    score = sp.get("similarity_score", 0)
                    st.markdown(f"**{sp.get('title')}** ({score*100:.1f}% similar)")
                    st.caption(sp.get("abstract", "")[:200] + "...")
            else:
                st.info("No similar papers found")
            
            if st.button("Close"):
                st.session_state.show_similar = None
                st.rerun()

