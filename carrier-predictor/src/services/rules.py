"""Rules engine for carrier eligibility."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from ..schemas import ClientInput
from .config import settings
from .logging_setup import logger


class CarrierRules:
    """Container for carrier and product rules."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize carrier rules.

        Args:
            data: Raw carrier data from YAML
        """
        self.name = data.get("name", "")
        self.states: Set[str] = set(data.get("states", []))
        self.portal_url: Optional[str] = data.get("portal_url")
        self.products: Dict[str, Dict[str, Any]] = data.get("products", {})

    def is_state_eligible(self, state: str) -> bool:
        """Check if carrier operates in state.

        Args:
            state: State code

        Returns:
            True if eligible
        """
        if not self.states:
            return True  # If no states specified, assume all states
        return state.upper() in self.states

    def get_eligible_products(
        self, coverage_type: str, age: int, smoker: bool, health_conditions: List[str]
    ) -> List[str]:
        """Get eligible products for client criteria.

        Args:
            coverage_type: Type of coverage desired
            age: Client age
            smoker: Smoker status
            health_conditions: List of health conditions

        Returns:
            List of eligible product names
        """
        eligible = []

        for product_name, product_data in self.products.items():
            if self._is_product_eligible(
                product_data, coverage_type, age, smoker, health_conditions
            ):
                eligible.append(product_name)

        return eligible

    def _is_product_eligible(
        self,
        product_data: Dict[str, Any],
        coverage_type: str,
        age: int,
        smoker: bool,
        health_conditions: List[str],
    ) -> bool:
        """Check if a product is eligible.

        Args:
            product_data: Product configuration
            coverage_type: Coverage type
            age: Client age
            smoker: Smoker status
            health_conditions: Health conditions

        Returns:
            True if eligible
        """
        # Check product type
        product_type = product_data.get("type", "")
        if product_type and coverage_type.lower() not in product_type.lower():
            return False

        # Check age band
        min_age = product_data.get("min_age", 0)
        max_age = product_data.get("max_age", 120)
        if not (min_age <= age <= max_age):
            return False

        # Check smoker acceptance
        smoker_ok = product_data.get("smoker", True)
        if smoker and not smoker_ok:
            return False

        # Check health tolerance
        health_tolerance = product_data.get("health_tolerance", [])
        if health_conditions and health_tolerance:
            # Check if any health conditions are in tolerance list
            tolerances_lower = [h.lower() for h in health_tolerance]
            has_match = any(
                cond.lower() in " ".join(tolerances_lower) for cond in health_conditions
            )
            # If product specifies tolerance, at least one condition should match
            # If no match, it's not necessarily disqualifying (graceful degradation)

        return True


class RulesEngine:
    """Engine for evaluating carrier eligibility rules."""

    def __init__(self):
        """Initialize rules engine."""
        self.carriers: Dict[str, CarrierRules] = {}
        self.load_rules()

    def load_rules(self) -> None:
        """Load carrier rules from YAML file."""
        yaml_path = Path(settings.carriers_yaml_path)

        if not yaml_path.exists():
            logger.warning(f"Carriers YAML not found: {yaml_path}")
            self.carriers = {}
            return

        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                logger.warning("Empty carriers YAML")
                self.carriers = {}
                return

            # Parse carriers
            self.carriers = {}
            for carrier_name, carrier_data in data.items():
                carrier_data["name"] = carrier_name
                self.carriers[carrier_name] = CarrierRules(carrier_data)

            logger.info(f"Loaded rules for {len(self.carriers)} carriers")

        except Exception as e:
            logger.error(f"Error loading carriers YAML: {e}")
            self.carriers = {}

    def get_eligible_carriers(self, client_input: ClientInput) -> Dict[str, List[str]]:
        """Get eligible carriers and products for a client.

        Args:
            client_input: Client input schema

        Returns:
            Dictionary mapping carrier names to lists of eligible product names
        """
        eligible = {}

        for carrier_name, carrier_rules in self.carriers.items():
            # Check state eligibility
            if not carrier_rules.is_state_eligible(client_input.state):
                continue

            # Get eligible products
            products = carrier_rules.get_eligible_products(
                coverage_type=client_input.coverage_type,
                age=client_input.age,
                smoker=client_input.smoker,
                health_conditions=client_input.health_conditions,
            )

            if products:
                eligible[carrier_name] = products

        logger.info(f"Found {len(eligible)} eligible carriers for client")
        return eligible

    def get_carrier_portal(self, carrier_name: str) -> Optional[str]:
        """Get portal URL for a carrier.

        Args:
            carrier_name: Carrier name

        Returns:
            Portal URL if available
        """
        carrier = self.carriers.get(carrier_name)
        if carrier:
            return carrier.portal_url
        return None

    def reload(self) -> None:
        """Reload rules from file."""
        self.load_rules()


# Global rules engine instance
rules_engine = RulesEngine()
