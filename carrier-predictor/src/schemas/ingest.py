"""Ingest request/response schemas."""

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request to ingest documents into knowledge base."""

    path: str = Field(..., description="Directory path containing documents to ingest")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"path": "data/carriers"}}


class IngestResponse(BaseModel):
    """Response from knowledge base ingest operation."""

    indexed_files: int = Field(..., description="Number of files indexed")
    chunks: int = Field(..., description="Total number of text chunks created")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"indexed_files": 15, "chunks": 342}}
