"""Portal URL mapping service."""

import json
from pathlib import Path
from typing import Dict, Optional

from .config import settings
from .logging_setup import logger


class PortalService:
    """Service for managing carrier portal URLs."""

    def __init__(self) -> None:
        """Initialize portal service."""
        self.portals: Dict[str, str] = {}
        self.load_portals()

    def load_portals(self) -> None:
        """Load portal links from JSON file."""
        try:
            path = Path(settings.portal_links_json_path)
            if path.exists():
                with open(path, "r") as f:
                    self.portals = json.load(f)
                logger.info(f"Loaded {len(self.portals)} portal links from {path}")
            else:
                logger.warning(f"Portal links file not found: {path}")
                self.portals = {}
        except Exception as e:
            logger.error(f"Error loading portal links: {e}")
            self.portals = {}

    def get_portal_url(self, carrier_name: str) -> Optional[str]:
        """Get portal URL for a carrier.

        Args:
            carrier_name: Name of the carrier (case-insensitive)

        Returns:
            Portal URL if found, None otherwise
        """
        # Try exact match first
        if carrier_name in self.portals:
            return self.portals[carrier_name]

        # Try case-insensitive match
        carrier_lower = carrier_name.lower()
        for key, value in self.portals.items():
            if key.lower() == carrier_lower:
                return value

        # Try partial match (carrier name contains key or vice versa)
        for key, value in self.portals.items():
            if key.lower() in carrier_lower or carrier_lower in key.lower():
                return value

        logger.debug(f"No portal URL found for carrier: {carrier_name}")
        return None

    def reload(self) -> None:
        """Reload portal links from file."""
        self.load_portals()


# Global portal service instance
portal_service = PortalService()
