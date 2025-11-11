"""Prediction router for carrier recommendations."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..schemas import ClientInput, RecommendationResponse
from ..services import (
    generate_request_id,
    logger,
    ranker_service,
    redact_phi,
    scorer_service,
    set_request_id,
)
from ..ai.assigner import load_rules, assign, render_response

router = APIRouter()


@router.post("/recommend-carriers", response_model=RecommendationResponse)
async def recommend_carriers(client_input: ClientInput) -> RecommendationResponse:
    """Get carrier/product recommendations for a client.

    Args:
        client_input: Client profile and requirements

    Returns:
        Ranked list of carrier/product recommendations

    Raises:
        HTTPException: If no recommendations can be generated
    """
    # Generate request ID for logging
    request_id = generate_request_id()
    set_request_id(request_id)

    # Log request (PHI-safe)
    safe_data = redact_phi(client_input.model_dump())
    logger.info(f"Received recommendation request: {safe_data}")

    try:
        # Score candidates
        scored_candidates = scorer_service.score_candidates(client_input)

        if not scored_candidates:
            logger.warning("No recommendations found for client")
            raise HTTPException(
                status_code=404,
                detail="No suitable carriers found for the provided criteria. "
                "Try adjusting coverage type, state, or other requirements.",
            )

        # Rank and format
        recommendations = ranker_service.rank(scored_candidates, top_n=5)

        logger.info(f"Returning {len(recommendations)} recommendations")

        return RecommendationResponse(recommendations=recommendations)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal error generating recommendations"
        )


@router.post("/recommend")
async def recommend_rules_based(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Get carrier/product recommendations using rules-based engine.

    This endpoint uses deterministic YAML-based rules instead of RAG/AI inference.

    Args:
        profile: Client profile dict with keys:
            - age (int): Client age
            - desired_coverage (int): Face amount desired
            - coverage_type (str): Type (Term, WL, FE, IUL)
            - smoker (bool): Tobacco use
            - state (str): State abbreviation
            - medical_conditions (dict): Medical history
            - first_name (str, optional): Client first name
            - ... and other eligibility fields

    Returns:
        Dict with:
            - recommendations: List of top 3 products
            - explanation: Formatted response text
            - fallback_triggered: Boolean indicating if no match found

    Example:
        {
            "age": 65,
            "desired_coverage": 15000,
            "coverage_type": "Final Expense",
            "smoker": false,
            "state": "TX",
            "medical_conditions": {"diabetes": true}
        }
    """
    # Generate request ID for logging
    request_id = generate_request_id()
    set_request_id(request_id)

    # Log request (PHI-safe)
    safe_data = redact_phi(profile)
    logger.info(f"Received rules-based recommendation request: {safe_data}")

    try:
        # Load rules and run assignment
        rules = load_rules()
        logger.info(f"Loaded {len(rules)} product rules")

        picks = assign(profile, rules)

        fallback_triggered = len(picks) == 0

        # Format response
        explanation = render_response(profile, picks)

        logger.info(
            f"Returning {len(picks)} recommendations "
            f"(fallback_triggered={fallback_triggered})"
        )

        return {
            "recommendations": picks,
            "explanation": explanation,
            "fallback_triggered": fallback_triggered,
            "request_id": request_id,
        }

    except Exception as e:
        logger.error(f"Error generating rules-based recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal error generating recommendations"
        )
