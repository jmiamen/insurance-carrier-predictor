"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import kb_router, predict_router
from .services import embedder_service, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Carrier Predictor API (Rules Engine)")

    # NOTE: Legacy RAG/FAISS system no longer loaded on startup
    # The new rules-based engine (/recommend) doesn't require embeddings
    # Legacy /recommend-carriers endpoint still available for backward compatibility

    yield

    # Shutdown
    logger.info("Shutting down Carrier Predictor API")


# Create FastAPI app
app = FastAPI(
    title="Carrier Predictor API",
    description="Deterministic, rules-based life insurance carrier recommendation engine",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict_router, tags=["Predictions"])
app.include_router(kb_router, tags=["Knowledge Base"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "carrier-predictor",
        "version": "1.0.0",
    }


# Serve frontend static files if they exist
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_path.exists():
    logger.info(f"Serving frontend from {frontend_path}")
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend_routes(full_path: str):
        """Serve frontend for all routes (SPA routing)"""
        # Check if it's an API endpoint
        if full_path.startswith(("health", "recommend", "recommend-carriers", "kb/", "docs", "redoc", "openapi.json")):
            return None

        # Try to serve the file if it exists
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise serve index.html for SPA routing
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    async def root() -> dict:
        """Root endpoint with API info.

        Returns:
            API information
        """
        return {
            "service": "Carrier Predictor API",
            "version": "2.0.0",
            "description": "Deterministic, rules-based carrier recommendation engine",
            "primary_endpoint": "/recommend",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "recommend": "/recommend (PRIMARY - rules-based)",
                "recommend_legacy": "/recommend-carriers (DEPRECATED - RAG-based)",
                "ingest": "/kb/ingest (legacy)",
                "kb_status": "/kb/status (legacy)",
            },
        }
