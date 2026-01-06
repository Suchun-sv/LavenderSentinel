"""CocoIndex pipeline definitions for paper indexing."""

from typing import Any

import cocoindex

from app.config import settings


@cocoindex.flow_def(name="paper_indexing")
def paper_indexing_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    CocoIndex flow for paper indexing.
    
    This pipeline:
    1. Reads papers from PostgreSQL database
    2. Combines title and abstract for embedding
    3. Chunks the text if needed
    4. Generates embeddings using sentence-transformers
    5. Stores vectors in Qdrant for semantic search
    """
    # Source: Read papers from PostgreSQL
    papers = flow_builder.add_source(
        cocoindex.sources.Postgres(
            connection_url=settings.cocoindex_database_url,
            table_name="papers",
            primary_key_column="id",
            columns=["id", "title", "abstract", "authors", "keywords", "categories"],
        )
    )
    
    # Transform: Create full text for embedding
    with data_scope["papers"].row() as paper:
        # Combine title and abstract for better semantic representation
        paper["full_text"] = cocoindex.functions.Format(
            template="Title: {title}\n\nAbstract: {abstract}\n\nKeywords: {keywords}",
            title=paper["title"],
            abstract=paper["abstract"],
            keywords=cocoindex.functions.Join(paper["keywords"], separator=", "),
        )
    
    # Split into chunks (for long abstracts)
    chunks = paper["full_text"].transform(
        cocoindex.functions.SplitRecursively(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " "],
        )
    )
    
    # Generate embeddings
    embeddings = chunks.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model=settings.embedding_model,
        )
    )
    
    # Store in Qdrant vector database
    flow_builder.add_target(
        cocoindex.targets.Qdrant(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=settings.qdrant_collection,
            vector_field="embedding",
            dimension=settings.embedding_dimension,
        ),
        embeddings,
    )


@cocoindex.flow_def(name="paper_summary_indexing")
def paper_summary_indexing_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    CocoIndex flow for indexing paper summaries.
    
    This pipeline indexes AI-generated summaries for enhanced search.
    """
    # Source: Read paper summaries from PostgreSQL
    summaries = flow_builder.add_source(
        cocoindex.sources.Postgres(
            connection_url=settings.cocoindex_database_url,
            table_name="paper_summaries",
            primary_key_column="id",
            columns=["id", "paper_id", "summary", "key_points", "methodology", "findings"],
        )
    )
    
    # Transform: Create full text for embedding
    with data_scope["summaries"].row() as summary:
        summary["full_text"] = cocoindex.functions.Format(
            template="Summary: {summary}\n\nKey Points: {key_points}\n\nMethodology: {methodology}\n\nFindings: {findings}",
            summary=summary["summary"],
            key_points=cocoindex.functions.Join(summary["key_points"], separator="; "),
            methodology=summary["methodology"],
            findings=summary["findings"],
        )
    
    # Generate embeddings
    embeddings = summary["full_text"].transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model=settings.embedding_model,
        )
    )
    
    # Store in Qdrant with different collection
    flow_builder.add_target(
        cocoindex.targets.Qdrant(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=f"{settings.qdrant_collection}_summaries",
            vector_field="embedding",
            dimension=settings.embedding_dimension,
        ),
        embeddings,
    )


class PaperIndexer:
    """Utility class for managing paper indexing operations."""

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        """Initialize CocoIndex with registered flows."""
        if self._initialized:
            return

        cocoindex.init(
            database_url=settings.cocoindex_database_url,
        )
        
        # Register flows
        cocoindex.register_flow(paper_indexing_flow)
        cocoindex.register_flow(paper_summary_indexing_flow)
        
        self._initialized = True

    async def run_indexing(self, flow_name: str = "paper_indexing") -> dict[str, Any]:
        """Run the indexing pipeline."""
        if not self._initialized:
            self.initialize()

        # Run the flow
        result = await cocoindex.run_flow_async(flow_name)
        
        return {
            "flow": flow_name,
            "status": "completed",
            "records_processed": result.records_processed if hasattr(result, 'records_processed') else 0,
        }

    async def update_index(self) -> dict[str, Any]:
        """Update the index incrementally with new papers."""
        if not self._initialized:
            self.initialize()

        # Run incremental update
        result = await cocoindex.update_flow_async("paper_indexing")
        
        return {
            "flow": "paper_indexing",
            "status": "updated",
            "records_processed": result.records_processed if hasattr(result, 'records_processed') else 0,
        }


def setup_cocoindex() -> PaperIndexer:
    """Setup and return the paper indexer."""
    indexer = PaperIndexer()
    indexer.initialize()
    return indexer


# Global indexer instance
paper_indexer = PaperIndexer()

