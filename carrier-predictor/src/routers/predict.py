"""Prediction router for carrier recommendations."""

from fastapi import APIRouter, HTTPException

from ..schemas import ClientInput, RecommendationResponse
from ..services import (
    generate_request_id,
    logger,
    ranker_service,
    redact_phi,
    scorer_service,
    set_request_id,
)

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
