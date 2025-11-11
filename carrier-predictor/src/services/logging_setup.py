"""PHI-safe logging configuration."""

import hashlib
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from .config import settings

# Context variable for request ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class PHISafeFormatter(logging.Formatter):
    """Custom formatter that ensures PHI is not logged."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with request ID."""
        req_id = request_id_ctx.get()
        if req_id:
            record.request_id = f"[{req_id}]"
        else:
            record.request_id = ""
        return super().format(record)


def setup_logging() -> None:
    """Configure logging with PHI-safe settings."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Custom formatter
    formatter = PHISafeFormatter(
        fmt="%(asctime)s - %(levelname)s - %(request_id)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]


def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    request_id_ctx.set(request_id)


def redact_phi(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact PHI from data dictionary for logging.

    Args:
        data: Dictionary that may contain PHI

    Returns:
        Sanitized dictionary safe for logging
    """
    redacted = data.copy()

    # Redact health conditions - only log count
    if "health_conditions" in redacted:
        conditions = redacted["health_conditions"]
        if isinstance(conditions, list):
            redacted["health_conditions"] = f"<{len(conditions)} conditions>"
        else:
            redacted["health_conditions"] = "<redacted>"

    # Redact notes
    if "notes" in redacted and redacted["notes"]:
        redacted["notes"] = f"<{len(redacted['notes'])} chars>"

    # Hash PII fields if present
    pii_fields = ["first_name", "last_name", "email", "phone"]
    for field in pii_fields:
        if field in redacted and redacted[field]:
            # Hash with first 4 chars visible
            value = str(redacted[field])
            hashed = hashlib.sha256(value.encode()).hexdigest()[:8]
            redacted[field] = f"{value[:2]}...{hashed}"

    return redacted


# Initialize logging on import
setup_logging()

# Export logger
logger = logging.getLogger("carrier_predictor")
