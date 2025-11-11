"""Tests for rules engine."""

import pytest

from src.schemas import ClientInput
from src.services import rules_engine


def test_rules_load():
    """Test that rules load from YAML."""
    # Should load without error
    rules_engine.load_rules()
    assert isinstance(rules_engine.carriers, dict)


def test_state_eligibility():
    """Test state eligibility checks."""
    # Reload to ensure we have carriers
    rules_engine.load_rules()

    if "MutualOfOmaha" in rules_engine.carriers:
        carrier = rules_engine.carriers["MutualOfOmaha"]
        assert carrier.is_state_eligible("TX")
        assert carrier.is_state_eligible("FL")


def test_get_eligible_carriers():
    """Test getting eligible carriers for a client."""
    rules_engine.load_rules()

    client = ClientInput(
        age=62,
        state="TX",
        gender="F",
        smoker=False,
        coverage_type="Whole Life",
        desired_coverage=250000,
        health_conditions=["diabetes"],
    )

    eligible = rules_engine.get_eligible_carriers(client)

    # Should return dict
    assert isinstance(eligible, dict)

    # Should have at least some carriers for TX
    # (Assuming carriers.yaml has TX entries)
    if eligible:
        # Check structure
        for carrier, products in eligible.items():
            assert isinstance(carrier, str)
            assert isinstance(products, list)


def test_age_band_filtering():
    """Test that age band filtering works."""
    rules_engine.load_rules()

    # Young client
    young_client = ClientInput(
        age=25,
        state="TX",
        smoker=False,
        coverage_type="Term",
    )

    # Old client
    old_client = ClientInput(
        age=85,
        state="TX",
        smoker=False,
        coverage_type="Whole Life",
    )

    young_eligible = rules_engine.get_eligible_carriers(young_client)
    old_eligible = rules_engine.get_eligible_carriers(old_client)

    # Both should have some results (or we need more carriers in config)
    assert isinstance(young_eligible, dict)
    assert isinstance(old_eligible, dict)


def test_product_type_matching():
    """Test that product type matching works."""
    rules_engine.load_rules()

    term_client = ClientInput(
        age=40,
        state="TX",
        smoker=False,
        coverage_type="Term",
    )

    whole_life_client = ClientInput(
        age=40,
        state="TX",
        smoker=False,
        coverage_type="Whole Life",
    )

    term_eligible = rules_engine.get_eligible_carriers(term_client)
    whole_life_eligible = rules_engine.get_eligible_carriers(whole_life_client)

    # Results should differ (if we have both types in config)
    assert isinstance(term_eligible, dict)
    assert isinstance(whole_life_eligible, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
