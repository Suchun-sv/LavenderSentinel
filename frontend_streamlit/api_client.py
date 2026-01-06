"""API client for backend communication."""

import httpx
from typing import Optional, Any
import streamlit as st

# Backend API URL
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")


class APIClient:
    """Client for communicating with the LavenderSentinel backend."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict[str, Any]:
        """Make an HTTP request to the backend."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"API Error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            st.error(f"Connection Error: {str(e)}")
            return {}
    
    # Papers API
    def list_papers(
        self,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None
    ) -> dict:
        """List papers with pagination."""
        params = {"page": page, "page_size": page_size}
        if source:
            params["source"] = source
        return self._request("GET", "/papers", params=params)
    
    def get_paper(self, paper_id: str) -> dict:
        """Get a single paper by ID."""
        return self._request("GET", f"/papers/{paper_id}")
    
    def get_paper_stats(self) -> dict:
        """Get paper collection statistics."""
        return self._request("GET", "/papers/stats")
    
    # Search API
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None
    ) -> dict:
        """Perform semantic search."""
        data = {
            "query": query,
            "top_k": top_k,
            "include_summary": True
        }
        if filters:
            data["filters"] = filters
        return self._request("POST", "/search/semantic", json=data)
    
    def find_similar_papers(
        self,
        paper_id: str,
        top_k: int = 10
    ) -> dict:
        """Find papers similar to a given paper."""
        data = {"paper_id": paper_id, "top_k": top_k}
        return self._request("POST", "/search/similar", json=data)
    
    # Chat API
    def send_chat_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        paper_context: Optional[list[str]] = None
    ) -> dict:
        """Send a chat message."""
        data = {
            "message": message,
            "include_sources": True
        }
        if session_id:
            data["session_id"] = session_id
        if paper_context:
            data["paper_context"] = paper_context
        return self._request("POST", "/chat", json=data)
    
    def get_chat_session(self, session_id: str) -> dict:
        """Get a chat session."""
        return self._request("GET", f"/chat/sessions/{session_id}")
    
    # Health API
    def health_check(self) -> dict:
        """Check backend health."""
        return self._request("GET", "/health")


# Singleton instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance."""
    return APIClient()


