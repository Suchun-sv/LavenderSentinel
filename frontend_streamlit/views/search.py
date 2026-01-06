"""Search page view."""

import streamlit as st
from api_client import get_api_client


def render():
    """Render the search page."""
    st.markdown('<h1 class="main-header">🔍 Search Papers</h1>', unsafe_allow_html=True)
    st.markdown("Find papers using natural language queries")
    
    st.divider()
    
    # Search input
    query = st.text_input(
        "Search query",
        placeholder="e.g., transformer attention mechanisms, climate change machine learning",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        top_k = st.selectbox("Results", [10, 20, 50], index=0)
    with col2:
        source_filter = st.selectbox("Source", ["All", "arxiv", "semantic_scholar"], index=0)
    with col3:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    st.divider()
    
    # Perform search
    if search_button and query:
        api = get_api_client()
        
        filters = None
        if source_filter != "All":
            filters = {"sources": [source_filter]}
        
        with st.spinner("Searching..."):
            results = api.semantic_search(query, top_k=top_k, filters=filters)
        
        if results:
            total = results.get("total", 0)
            took_ms = results.get("took_ms", 0)
            
            st.success(f"Found **{total}** papers in {took_ms:.0f}ms")
            
            # Display results
            for result in results.get("results", []):
                paper = result.get("paper", {})
                score = paper.get("similarity_score", 0)
                
                with st.container():
                    # Title with score
                    col_title, col_score = st.columns([4, 1])
                    with col_title:
                        st.markdown(f"### {paper.get('title', 'Untitled')}")
                    with col_score:
                        st.metric("Match", f"{score*100:.1f}%")
                    
                    # Authors
                    authors = paper.get("authors", [])
                    author_names = ", ".join([a.get("name", "") for a in authors[:5]])
                    if len(authors) > 5:
                        author_names += f" +{len(authors) - 5} more"
                    st.caption(f"👤 {author_names}")
                    
                    # Abstract
                    with st.expander("📄 Abstract", expanded=False):
                        st.markdown(paper.get("abstract", "No abstract available"))
                    
                    # Metadata
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.caption(f"📅 {paper.get('published_at', 'Unknown')[:10]}")
                    with col_b:
                        st.caption(f"📂 {paper.get('source', 'Unknown')}")
                    with col_c:
                        url = paper.get("url", "")
                        if url:
                            st.markdown(f"[🔗 View Paper]({url})")
                    
                    # Categories
                    categories = paper.get("categories", [])
                    if categories:
                        badges_html = "".join([f'<span class="badge">{cat}</span>' for cat in categories[:5]])
                        st.markdown(badges_html, unsafe_allow_html=True)
                    
                    # Actions
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("💬 Chat about this", key=f"chat_{paper.get('id')}"):
                            st.session_state.chat_paper_id = paper.get("id")
                            st.session_state.chat_paper_title = paper.get("title")
                            st.info("Go to Chat page to discuss this paper")
                    with col_act2:
                        pdf_url = paper.get("pdf_url")
                        if pdf_url:
                            st.markdown(f"[📥 Download PDF]({pdf_url})")
                    
                    st.divider()
        else:
            st.warning("No results found. Try a different query.")
    
    elif search_button:
        st.warning("Please enter a search query")
    
    # Search tips
    with st.expander("💡 Search Tips"):
        st.markdown("""
        **Effective search queries:**
        - Use natural language: "papers about transformer architecture for NLP"
        - Be specific: "reinforcement learning for robotics manipulation"
        - Combine concepts: "graph neural networks protein folding"
        
        **Filters:**
        - Source: Filter by paper source (arXiv, Semantic Scholar)
        - More filters coming soon (date range, categories, authors)
        """)

