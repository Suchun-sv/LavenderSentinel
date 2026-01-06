"""Chat page view with RAG support."""

import streamlit as st
from api_client import get_api_client


def render():
    """Render the chat page."""
    st.markdown('<h1 class="main-header">💬 AI Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Ask questions about papers in your collection")
    
    st.divider()
    
    api = get_api_client()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = None
    if "paper_context" not in st.session_state:
        st.session_state.paper_context = []
    
    # Sidebar for paper context
    with st.sidebar:
        st.markdown("### 📚 Paper Context")
        st.caption("Papers the AI will reference")
        
        # Show selected papers
        if st.session_state.paper_context:
            for paper_id in st.session_state.paper_context:
                paper_title = st.session_state.get(f"paper_title_{paper_id}", paper_id[:8])
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"📄 {paper_title[:30]}...")
                with col2:
                    if st.button("❌", key=f"remove_{paper_id}"):
                        st.session_state.paper_context.remove(paper_id)
                        st.rerun()
        else:
            st.info("No papers selected. Search and add papers to get better answers.")
        
        if st.button("🗑️ Clear Context", use_container_width=True):
            st.session_state.paper_context = []
            st.rerun()
        
        st.divider()
        
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_session_id = None
            st.rerun()
    
    # Check if coming from paper selection
    if "chat_paper_id" in st.session_state and st.session_state.chat_paper_id:
        paper_id = st.session_state.chat_paper_id
        if paper_id not in st.session_state.paper_context:
            st.session_state.paper_context.append(paper_id)
            if "chat_paper_title" in st.session_state:
                st.session_state[f"paper_title_{paper_id}"] = st.session_state.chat_paper_title
        st.session_state.chat_paper_id = None
        st.session_state.chat_paper_title = None
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            ### 👋 Hello! I'm your AI Research Assistant
            
            I can help you:
            - **Understand papers** - Explain complex concepts in simple terms
            - **Compare research** - Analyze similarities and differences
            - **Find insights** - Identify key findings and methodologies
            - **Answer questions** - About any paper in your collection
            
            **Try asking:**
            - "What are the main contributions of this paper?"
            - "Explain the methodology used"
            - "How does this compare to other approaches?"
            - "What are the limitations mentioned?"
            """)
        
        # Display messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant", avatar="🌿"):
                    st.markdown(content)
                    
                    # Show sources if available
                    sources = message.get("sources", [])
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.caption(f"**{source.get('title', 'Unknown')}**")
                                st.caption(f"_{source.get('excerpt', '')[:150]}..._")
    
    # Chat input
    if prompt := st.chat_input("Ask about your papers..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("Thinking..."):
                response = api.send_chat_message(
                    message=prompt,
                    session_id=st.session_state.chat_session_id,
                    paper_context=st.session_state.paper_context if st.session_state.paper_context else None
                )
                
                if response:
                    # Update session ID
                    st.session_state.chat_session_id = response.get("session_id")
                    
                    # Get message content
                    message_data = response.get("message", {})
                    content = message_data.get("content", "Sorry, I couldn't generate a response.")
                    sources = response.get("sources", [])
                    
                    st.markdown(content)
                    
                    # Show sources
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.caption(f"**{source.get('title', 'Unknown')}**")
                                st.caption(f"_{source.get('excerpt', '')[:150]}..._")
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "sources": sources
                    })
                    
                    # Show follow-up suggestions
                    followups = response.get("suggested_followups", [])
                    if followups:
                        st.markdown("**Suggested questions:**")
                        cols = st.columns(len(followups))
                        for i, followup in enumerate(followups):
                            with cols[i]:
                                if st.button(followup, key=f"followup_{i}", use_container_width=True):
                                    st.session_state.next_message = followup
                                    st.rerun()
                else:
                    st.error("Failed to get response from AI. Make sure the backend is running.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Sorry, I encountered an error. Please try again."
                    })
    
    # Handle follow-up click
    if "next_message" in st.session_state and st.session_state.next_message:
        next_msg = st.session_state.next_message
        st.session_state.next_message = None
        st.session_state.messages.append({"role": "user", "content": next_msg})
        st.rerun()

