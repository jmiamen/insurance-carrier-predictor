"""Tests for prediction endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services import embedder_service
from src.services.kb_loader import DocumentChunk

# Create test client
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_index():
    """Setup a test index before running tests."""
    # Create mock chunks
    chunks = [
        DocumentChunk(
            text="Mutual of Omaha Living Promise Whole Life insurance for ages 45-85. "
            "Available in Texas, Florida, Georgia. Accepts controlled diabetes and high blood pressure. "
            "Face amounts from $2,000 to $50,000.",
            source_path="mutual_omaha.pdf",
            carrier_guess="Mutual of Omaha",
            product_guess="Living Promise",
        ),
        DocumentChunk(
            text="Elco Mutual Golden Eagle Final Expense for seniors. Ages 50-85. "
            "Available in Texas, Colorado, Michigan. Accepts diabetes, neuropathy, COPD. "
            "Simplified issue whole life insurance.",
            source_path="elco.pdf",
            carrier_guess="Elco Mutual",
            product_guess="Golden Eagle",
        ),
        DocumentChunk(
            text="Americo Term Life Insurance for ages 18-75. Competitive rates for healthy individuals. "
            "Available in most states including Texas, Florida, California. "
            "Medical exam required for amounts over $250,000.",
            source_path="americo_term.pdf",
            carrier_guess="Americo",
            product_guess="Term",
        ),
    ]

    # Build index
    embedder_service.build_index(chunks)
    yield
    # Cleanup after tests
    embedder_service.index = None
    embedder_service.metadata = []


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "endpoints" in data


def test_recommend_carriers_success():
    """Test successful recommendation request."""
    request_data = {
        "age": 62,
        "state": "TX",
        "gender": "F",
        "smoker": False,
        "coverage_type": "Whole Life",
        "desired_coverage": 250000,
        "health_conditions": ["diabetes", "neuropathy"],
    }

    response = client.post("/recommend-carriers", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)

    # Check if we got at least one recommendation
    if len(data["recommendations"]) > 0:
        rec = data["recommendations"][0]
        assert "carrier" in rec
        assert "product" in rec
        assert "confidence" in rec
        assert "reason" in rec
        assert "portal_url" in rec

        # Confidence should be between 0 and 1
        assert 0.0 <= rec["confidence"] <= 1.0


def test_recommend_carriers_validation():
    """Test input validation."""
    # Invalid age
    invalid_request = {
        "age": 150,
        "state": "TX",
        "smoker": False,
        "coverage_type": "Whole Life",
    }

    response = client.post("/recommend-carriers", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_recommend_carriers_different_coverage_types():
    """Test recommendations for different coverage types."""
    coverage_types = ["Term", "Whole Life", "Final Expense"]

    for coverage_type in coverage_types:
        request_data = {
            "age": 45,
            "state": "TX",
            "smoker": False,
            "coverage_type": coverage_type,
        }

        response = client.post("/recommend-carriers", json=request_data)
        # Should either succeed or return 404 (no matches)
        assert response.status_code in [200, 404]


def test_kb_status():
    """Test knowledge base status endpoint."""
    response = client.get("/kb/status")
    assert response.status_code == 200

    data = response.json()
    assert "index_exists" in data
    assert data["index_exists"] is True  # We created an index in setup


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
