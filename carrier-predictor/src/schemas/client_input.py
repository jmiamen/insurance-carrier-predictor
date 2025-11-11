"""Client input schema with validation."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ClientInput(BaseModel):
    """Request schema for carrier recommendations."""

    age: int = Field(..., ge=0, le=120, description="Client age")
    state: str = Field(..., min_length=2, max_length=2, description="US state (2-letter code)")
    gender: Optional[Literal["M", "F", "X"]] = Field(None, description="Gender")
    smoker: bool = Field(..., description="Tobacco user status")
    coverage_type: Literal[
        "Term", "Whole Life", "IUL", "Final Expense", "Universal Life", "Variable Life"
    ] = Field(..., description="Type of coverage desired")
    desired_coverage: Optional[int] = Field(
        None, ge=1000, description="Desired death benefit amount"
    )
    health_conditions: List[str] = Field(
        default_factory=list, description="List of health conditions"
    )
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    @field_validator("state")
    @classmethod
    def normalize_state(cls, v: str) -> str:
        """Normalize state to uppercase."""
        return v.strip().upper()

    @field_validator("coverage_type")
    @classmethod
    def normalize_coverage_type(cls, v: str) -> str:
        """Normalize coverage type."""
        return v.strip()

    @field_validator("health_conditions", mode="before")
    @classmethod
    def normalize_conditions(cls, v: List[str]) -> List[str]:
        """Normalize health conditions to lowercase and strip whitespace."""
        if not v:
            return []
        return [condition.strip().lower() for condition in v if condition.strip()]

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, v: Optional[str]) -> Optional[str]:
        """Normalize gender to uppercase."""
        if v:
            return v.strip().upper()
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "age": 62,
                "state": "TX",
                "gender": "F",
                "smoker": False,
                "coverage_type": "Whole Life",
                "desired_coverage": 250000,
                "health_conditions": ["diabetes", "neuropathy"],
                "notes": "Client prefers lower premium options",
            }
        }
