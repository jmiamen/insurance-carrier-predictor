"""Recommendation output schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """Single carrier/product recommendation."""

    carrier: str = Field(..., description="Insurance carrier name")
    product: str = Field(..., description="Specific product name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., max_length=500, description="Human-readable explanation")
    portal_url: Optional[str] = Field(None, description="Agent portal URL")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "carrier": "Mutual of Omaha",
                "product": "Living Promise Whole Life",
                "confidence": 0.91,
                "reason": "Accepts controlled diabetes; TX eligible; age within band 45–85.",
                "portal_url": "https://sales.mutualofomaha.com/agent/login",
            }
        }


class RecommendationResponse(BaseModel):
    """Response containing list of recommendations."""

    recommendations: List[Recommendation] = Field(
        ..., description="Ranked list of carrier/product recommendations"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "carrier": "Mutual of Omaha",
                        "product": "Living Promise Whole Life",
                        "confidence": 0.91,
                        "reason": "Accepts controlled diabetes; TX eligible; age 45–85.",
                        "portal_url": "https://sales.mutualofomaha.com/agent/login",
                    },
                    {
                        "carrier": "Elco Mutual",
                        "product": "Golden Eagle Whole Life",
                        "confidence": 0.88,
                        "reason": "Diabetes tolerance and TX eligibility.",
                        "portal_url": "https://elcomutual.com/agent-portal",
                    },
                ]
            }
        }
