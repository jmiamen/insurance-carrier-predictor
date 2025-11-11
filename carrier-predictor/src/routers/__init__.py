"""Routers package."""

from .kb import router as kb_router
from .predict import router as predict_router

__all__ = ["predict_router", "kb_router"]
