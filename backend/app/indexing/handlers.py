"""Vector search handlers using CocoIndex and Qdrant."""

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
    SearchParams,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.paper import PaperWithSimilarity
from app.models.search import SearchFilters


class VectorSearchHandler:
    """Handler for vector similarity search operations."""

    def __init__(self) -> None:
        self._client: Optional[QdrantClient] = None
        self._embedder: Optional[SentenceTransformer] = None

    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        return self._client

    @property
    def embedder(self) -> SentenceTransformer:
        """Get or create sentence transformer model."""
        if self._embedder is None:
            self._embedder = SentenceTransformer(settings.embedding_model)
        return self._embedder

    async def ensure_collection(self) -> None:
        """Ensure the vector collection exists."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if settings.qdrant_collection not in collection_names:
            self.client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

    def _build_filter(self, filters: Optional[SearchFilters]) -> Optional[Filter]:
        """Build Qdrant filter from search filters."""
        if not filters:
            return None

        conditions = []

        if filters.categories:
            for category in filters.categories:
                conditions.append(
                    FieldCondition(
                        key="categories",
                        match=MatchValue(value=category),
                    )
                )

        if filters.sources:
            for source in filters.sources:
                conditions.append(
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source),
                    )
                )

        if not conditions:
            return None

        return Filter(should=conditions) if len(conditions) > 1 else Filter(must=conditions)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[SearchFilters] = None,
    ) -> list[dict]:
        """
        Perform semantic search on papers.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional search filters
            
        Returns:
            List of search results with paper IDs and scores
        """
        # Generate query embedding
        query_vector = self.embedder.encode(query).tolist()

        # Build filter
        qdrant_filter = self._build_filter(filters)

        # Search
        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False,
            ),
        )

        return [
            {
                "paper_id": hit.payload.get("paper_id", hit.id),
                "score": hit.score,
                "chunk_text": hit.payload.get("text", ""),
            }
            for hit in results
        ]

    async def find_similar(
        self,
        paper_id: str,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Find papers similar to a given paper.
        
        Args:
            paper_id: Source paper ID
            top_k: Number of similar papers to return
            
        Returns:
            List of similar papers with scores
        """
        # Get the paper's vector
        points = self.client.retrieve(
            collection_name=settings.qdrant_collection,
            ids=[paper_id],
            with_vectors=True,
        )

        if not points:
            return []

        paper_vector = points[0].vector

        # Search for similar papers, excluding the source paper
        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=paper_vector,
            limit=top_k + 1,  # +1 to account for the source paper
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False,
            ),
        )

        # Filter out the source paper
        return [
            {
                "paper_id": hit.payload.get("paper_id", hit.id),
                "score": hit.score,
            }
            for hit in results
            if hit.payload.get("paper_id", hit.id) != paper_id
        ][:top_k]

    async def get_context_for_rag(
        self,
        query: str,
        paper_ids: Optional[list[str]] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Get relevant context chunks for RAG.
        
        Args:
            query: User query
            paper_ids: Optional list of paper IDs to search within
            top_k: Number of chunks to return
            
        Returns:
            List of relevant text chunks with metadata
        """
        query_vector = self.embedder.encode(query).tolist()

        # Build filter for specific papers
        qdrant_filter = None
        if paper_ids:
            conditions = [
                FieldCondition(
                    key="paper_id",
                    match=MatchValue(value=pid),
                )
                for pid in paper_ids
            ]
            qdrant_filter = Filter(should=conditions)

        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        return [
            {
                "paper_id": hit.payload.get("paper_id", hit.id),
                "text": hit.payload.get("text", ""),
                "title": hit.payload.get("title", ""),
                "score": hit.score,
            }
            for hit in results
        ]


# Global handler instance
vector_search_handler = VectorSearchHandler()

