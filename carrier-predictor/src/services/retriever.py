"""Retrieval service for similarity search."""

from typing import List, Tuple

import numpy as np

from ..schemas import ClientInput
from .config import settings
from .embedder import embedder_service
from .logging_setup import logger


class RetrieverService:
    """Service for retrieving similar documents from the index."""

    def __init__(self):
        """Initialize retriever service."""
        self.top_k = settings.top_k

    def build_query(self, client_input: ClientInput) -> str:
        """Build a query string from client input.

        Args:
            client_input: Client input schema

        Returns:
            Query string for embedding
        """
        parts = [
            f"Age: {client_input.age}",
            f"State: {client_input.state}",
            f"Coverage: {client_input.coverage_type}",
        ]

        if client_input.desired_coverage:
            parts.append(f"Amount: ${client_input.desired_coverage}")

        if client_input.gender:
            parts.append(f"Gender: {client_input.gender}")

        parts.append(f"Smoker: {'yes' if client_input.smoker else 'no'}")

        if client_input.health_conditions:
            conditions_str = ", ".join(client_input.health_conditions)
            parts.append(f"Health: {conditions_str}")

        if client_input.notes:
            parts.append(client_input.notes)

        query = " ".join(parts)
        return query

    def retrieve(
        self, client_input: ClientInput, top_k: int = None
    ) -> List[Tuple[dict, float]]:
        """Retrieve top-k similar documents for a client.

        Args:
            client_input: Client input schema
            top_k: Number of results to retrieve (defaults to config value)

        Returns:
            List of tuples (metadata, similarity_score)
        """
        if embedder_service.index is None:
            logger.warning("No index loaded, attempting to load from disk")
            if not embedder_service.load_index():
                logger.error("Failed to load index")
                return []

        k = top_k or self.top_k
        k = min(k, embedder_service.index.ntotal)  # Don't exceed available vectors

        # Build query
        query = self.build_query(client_input)
        logger.debug(f"Query: {query[:200]}...")

        # Embed query
        query_embedding = embedder_service.embed_texts([query])[0]
        query_embedding = np.array([query_embedding]).astype("float32")

        # Search index
        distances, indices = embedder_service.index.search(query_embedding, k)

        # Collect results with metadata
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(embedder_service.metadata):
                metadata = embedder_service.metadata[idx]
                # Convert L2 distance to similarity score (0-1, higher is better)
                # Using exponential decay: sim = exp(-distance)
                similarity = float(np.exp(-dist))
                results.append((metadata, similarity))

        logger.info(f"Retrieved {len(results)} results for query")
        return results

    def get_carrier_scores(self, results: List[Tuple[dict, float]]) -> dict:
        """Aggregate retrieval scores by carrier.

        Args:
            results: List of (metadata, similarity) tuples

        Returns:
            Dictionary mapping carrier names to average similarity scores
        """
        carrier_scores = {}
        carrier_counts = {}

        for metadata, similarity in results:
            carrier = metadata.get("carrier_guess", "").strip()
            if carrier:
                if carrier not in carrier_scores:
                    carrier_scores[carrier] = 0.0
                    carrier_counts[carrier] = 0
                carrier_scores[carrier] += similarity
                carrier_counts[carrier] += 1

        # Average scores
        for carrier in carrier_scores:
            if carrier_counts[carrier] > 0:
                carrier_scores[carrier] /= carrier_counts[carrier]

        return carrier_scores


# Global retriever service instance
retriever_service = RetrieverService()
