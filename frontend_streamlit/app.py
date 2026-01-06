"""
LavenderSentinel - Streamlit Frontend
A simple Python-based UI for the academic paper management system.
"""

import streamlit as st
from pages_config import setup_page_config

# Setup page configuration
setup_page_config()

# Import pages
from views import home, search, papers, chat

# Sidebar navigation
st.sidebar.title("🌿 LavenderSentinel")
st.sidebar.markdown("*Your reliable sentinel for academic literature*")
st.sidebar.divider()

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🔍 Search", "📚 Papers", "💬 Chat"],
    label_visibility="collapsed"
)

st.sidebar.divider()

# Info box
st.sidebar.info(
    "**Tip:** Use the Chat page to ask questions about papers in your collection."
)

# Route to pages
if page == "🏠 Home":
    home.render()
elif page == "🔍 Search":
    search.render()
elif page == "📚 Papers":
    papers.render()
elif page == "💬 Chat":
    chat.render()

# Footer
st.sidebar.divider()
st.sidebar.caption("LavenderSentinel v0.1.0")

