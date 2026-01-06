"""Home page view."""

import streamlit as st
from api_client import get_api_client


def render():
    """Render the home page."""
    # Header
    st.markdown('<h1 class="main-header">🌿 LavenderSentinel</h1>', unsafe_allow_html=True)
    st.markdown("**Your reliable sentinel for academic literature**")
    
    st.divider()
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to LavenderSentinel
        
        Automatically collect, index, and summarize research papers.
        Deep dive into any topic with AI-powered conversation.
        
        **Features:**
        - 📚 **Automatic Paper Collection** - Fetch from arXiv, Semantic Scholar
        - 🔍 **Semantic Search** - Find papers using natural language
        - 🤖 **AI Summarization** - Get concise summaries
        - 💬 **RAG-powered Chat** - Ask questions about your papers
        """)
        
        # Quick actions
        st.markdown("#### Quick Actions")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🔍 Search Papers", use_container_width=True):
                st.session_state.page = "search"
                st.rerun()
        with col_b:
            if st.button("📚 Browse Papers", use_container_width=True):
                st.session_state.page = "papers"
                st.rerun()
        with col_c:
            if st.button("💬 Start Chat", use_container_width=True):
                st.session_state.page = "chat"
                st.rerun()
    
    with col2:
        # Stats
        st.markdown("#### 📊 Collection Stats")
        
        api = get_api_client()
        stats = api.get_paper_stats()
        
        if stats:
            st.metric("Total Papers", stats.get("total_papers", 0))
            st.metric("With Summary", stats.get("papers_with_summary", 0))
        else:
            st.info("Connect to backend to see stats")
    
    st.divider()
    
    # Recent papers preview
    st.markdown("### 📄 Recent Papers")
    
    papers_data = api.list_papers(page=1, page_size=5)
    papers = papers_data.get("papers", [])
    
    if papers:
        for paper in papers:
            with st.container():
                st.markdown(f"**{paper.get('title', 'Untitled')}**")
                
                # Authors
                authors = paper.get("authors", [])
                author_names = ", ".join([a.get("name", "") for a in authors[:3]])
                if len(authors) > 3:
                    author_names += f" +{len(authors) - 3} more"
                st.caption(author_names)
                
                # Abstract preview
                abstract = paper.get("abstract", "")
                if len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                st.markdown(f"_{abstract}_")
                
                # Categories
                categories = paper.get("categories", [])
                if categories:
                    badges_html = "".join([f'<span class="badge">{cat}</span>' for cat in categories[:3]])
                    st.markdown(badges_html, unsafe_allow_html=True)
                
                st.divider()
    else:
        st.info("No papers in collection yet. Start by collecting some papers!")
    
    # Backend status
    with st.expander("🔌 Backend Status"):
        health = api.health_check()
        if health:
            st.success(f"✅ Connected - {health.get('status', 'unknown')}")
            st.json(health)
        else:
            st.error("❌ Cannot connect to backend")
            st.markdown("""
            Make sure the backend is running:
            ```bash
            docker compose up -d
            ```
            """)

