"""Knowledge base management router."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..schemas import IngestRequest, IngestResponse
from ..services import embedder_service, generate_request_id, kb_loader, logger, set_request_id

router = APIRouter()


@router.post("/kb/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    """Ingest documents into the knowledge base.

    Args:
        request: Ingest request with directory path

    Returns:
        Number of files and chunks indexed

    Raises:
        HTTPException: If directory doesn't exist or ingestion fails
    """
    # Generate request ID
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(f"Starting knowledge base ingest from: {request.path}")

    # Validate directory
    path = Path(request.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.path}")

    if not path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")

    try:
        # Load documents
        chunks = kb_loader.load_documents(request.path)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No documents found or no text extracted. "
                "Ensure directory contains .pdf, .html, or .txt files.",
            )

        # Count unique files
        unique_files = set(chunk.source_path for chunk in chunks)
        num_files = len(unique_files)

        # Build index
        embedder_service.build_index(chunks)

        # Save index
        embedder_service.save_index()

        logger.info(f"Successfully indexed {num_files} files with {len(chunks)} chunks")

        return IngestResponse(indexed_files=num_files, chunks=len(chunks))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during knowledge base ingest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/kb/status")
async def kb_status() -> dict:
    """Get knowledge base status.

    Returns:
        Status information about the current index
    """
    info = embedder_service.get_index_info()
    return {
        "index_exists": info.get("exists", False),
        "num_vectors": info.get("num_vectors", 0),
        "dimension": info.get("dimension", 0),
        "model_name": info.get("model_name", ""),
    }
