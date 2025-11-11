"""Tests for retrieval service."""

import pytest

from src.schemas import ClientInput
from src.services import embedder_service, retriever_service
from src.services.kb_loader import DocumentChunk


def test_build_query():
    """Test query building from client input."""
    client = ClientInput(
        age=62,
        state="TX",
        gender="F",
        smoker=False,
        coverage_type="Whole Life",
        desired_coverage=250000,
        health_conditions=["diabetes", "neuropathy"],
    )

    query = retriever_service.build_query(client)

    # Check that key info is in query
    assert "62" in query
    assert "TX" in query
    assert "Whole Life" in query
    assert "smoker: no" in query.lower()
    assert "diabetes" in query.lower()
    assert "neuropathy" in query.lower()


def test_retrieval_with_mock_index():
    """Test retrieval with a small mock index."""
    # Create mock chunks
    chunks = [
        DocumentChunk(
            text="Mutual of Omaha Living Promise Whole Life accepts diabetes for ages 45-85 in Texas",
            source_path="test1.pdf",
            carrier_guess="Mutual of Omaha",
            product_guess="Living Promise",
        ),
        DocumentChunk(
            text="Elco Mutual Golden Eagle Final Expense available in Texas for ages 50-85",
            source_path="test2.pdf",
            carrier_guess="Elco Mutual",
            product_guess="Golden Eagle",
        ),
        DocumentChunk(
            text="Term life insurance for young healthy individuals",
            source_path="test3.pdf",
            carrier_guess="Generic Carrier",
            product_guess="Term",
        ),
    ]

    # Build temporary index
    embedder_service.build_index(chunks)

    # Test retrieval
    client = ClientInput(
        age=62,
        state="TX",
        smoker=False,
        coverage_type="Whole Life",
        health_conditions=["diabetes"],
    )

    results = retriever_service.retrieve(client, top_k=3)

    # Should get results
    assert len(results) > 0
    assert len(results) <= 3

    # Each result should be (metadata, score)
    for metadata, score in results:
        assert isinstance(metadata, dict)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


def test_get_carrier_scores():
    """Test carrier score aggregation."""
    # Mock results
    mock_results = [
        ({"carrier_guess": "Carrier A", "text": "..."}, 0.8),
        ({"carrier_guess": "Carrier A", "text": "..."}, 0.7),
        ({"carrier_guess": "Carrier B", "text": "..."}, 0.9),
    ]

    scores = retriever_service.get_carrier_scores(mock_results)

    # Should have scores for both carriers
    assert "Carrier A" in scores
    assert "Carrier B" in scores

    # Carrier A should have average of 0.8 and 0.7
    assert abs(scores["Carrier A"] - 0.75) < 0.01

    # Carrier B should have 0.9
    assert abs(scores["Carrier B"] - 0.9) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
