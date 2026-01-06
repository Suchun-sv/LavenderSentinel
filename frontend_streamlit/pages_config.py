"""Page configuration for Streamlit app."""

import streamlit as st


def setup_page_config():
    """Setup Streamlit page configuration."""
    st.set_page_config(
        page_title="LavenderSentinel",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/yourusername/LavenderSentinel",
            "Report a bug": "https://github.com/yourusername/LavenderSentinel/issues",
            "About": "# LavenderSentinel\nYour reliable sentinel for academic literature."
        }
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --lavender-primary: #8b5cf6;
            --lavender-secondary: #a78bfa;
            --lavender-light: #ede9fe;
        }
        
        /* Header styling */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #8b5cf6, #6d28d9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        /* Card styling */
        .paper-card {
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            transition: box-shadow 0.2s;
        }
        
        .paper-card:hover {
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            background-color: #ede9fe;
            color: #6d28d9;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Chat message styling */
        .user-message {
            background-color: #8b5cf6;
            color: white;
            padding: 1rem;
            border-radius: 1rem;
            margin: 0.5rem 0;
        }
        
        .assistant-message {
            background-color: #f3f4f6;
            padding: 1rem;
            border-radius: 1rem;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

