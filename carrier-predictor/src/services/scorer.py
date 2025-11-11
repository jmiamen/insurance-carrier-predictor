"""Scoring service for carrier recommendations."""

from typing import Dict, List, Optional, Tuple

from ..schemas import ClientInput, Recommendation
from .config import settings
from .logging_setup import logger
from .portals import portal_service
from .retriever import retriever_service
from .rules import rules_engine

# Optional OpenAI
try:
    from openai import OpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class ScorerService:
    """Service for scoring carrier/product combinations."""

    def __init__(self):
        """Initialize scorer service."""
        self.use_openai = settings.enable_openai_scoring and settings.openai_api_key
        self.openai_client = None

        if self.use_openai:
            if HAS_OPENAI:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI scoring enabled")
            else:
                logger.warning("OpenAI enabled but library not installed")
                self.use_openai = False

    def score_candidates(
        self, client_input: ClientInput
    ) -> List[Tuple[str, str, float, str]]:
        """Score all candidate carriers/products.

        Args:
            client_input: Client input

        Returns:
            List of tuples: (carrier, product, confidence, reason)
        """
        # Get rule-based eligible carriers
        eligible = rules_engine.get_eligible_carriers(client_input)

        if not eligible:
            logger.info("No rule-based eligible carriers found")
            # Fall back to retrieval-based candidates
            return self._score_retrieval_only(client_input)

        # Get retrieval scores
        retrieval_results = retriever_service.retrieve(client_input)
        retrieval_scores = retriever_service.get_carrier_scores(retrieval_results)

        # Score each carrier/product combination
        scored_candidates = []

        for carrier, products in eligible.items():
            for product in products:
                score, reason = self._score_combination(
                    carrier=carrier,
                    product=product,
                    client_input=client_input,
                    retrieval_scores=retrieval_scores,
                    retrieval_results=retrieval_results,
                )
                scored_candidates.append((carrier, product, score, reason))

        return scored_candidates

    def _score_combination(
        self,
        carrier: str,
        product: str,
        client_input: ClientInput,
        retrieval_scores: Dict[str, float],
        retrieval_results: List[Tuple[dict, float]],
    ) -> Tuple[float, str]:
        """Score a single carrier/product combination.

        Args:
            carrier: Carrier name
            product: Product name
            client_input: Client input
            retrieval_scores: Retrieval scores by carrier
            retrieval_results: Raw retrieval results

        Returns:
            Tuple of (confidence_score, reason)
        """
        # Base score
        score = 0.5
        reasons = []

        # Product type match
        carrier_rules = rules_engine.carriers.get(carrier)
        if carrier_rules and product in carrier_rules.products:
            product_data = carrier_rules.products[product]
            product_type = product_data.get("type", "")

            if client_input.coverage_type.lower() in product_type.lower():
                score += 0.2
                reasons.append(f"{client_input.coverage_type} product match")

        # State eligibility (already checked, so add points)
        if carrier_rules and carrier_rules.is_state_eligible(client_input.state):
            score += 0.1
            reasons.append(f"{client_input.state} eligible")

        # Age band (already checked, so add points)
        if carrier_rules and product in carrier_rules.products:
            product_data = carrier_rules.products[product]
            min_age = product_data.get("min_age", 0)
            max_age = product_data.get("max_age", 120)
            if min_age <= client_input.age <= max_age:
                score += 0.1
                reasons.append(f"age band {min_age}–{max_age}")

        # Smoker tolerance
        if carrier_rules and product in carrier_rules.products:
            product_data = carrier_rules.products[product]
            smoker_ok = product_data.get("smoker", True)
            if client_input.smoker and smoker_ok:
                score += 0.05
                reasons.append("smoker accepted")
            elif not client_input.smoker:
                score += 0.05
                reasons.append("non-smoker")

        # Health tolerance
        if client_input.health_conditions and carrier_rules:
            if product in carrier_rules.products:
                product_data = carrier_rules.products[product]
                health_tolerance = product_data.get("health_tolerance", [])
                if health_tolerance:
                    tolerances_lower = [h.lower() for h in health_tolerance]
                    matched_conditions = []
                    for cond in client_input.health_conditions:
                        if any(cond.lower() in t for t in tolerances_lower):
                            matched_conditions.append(cond)
                    if matched_conditions:
                        # Cap at +0.2
                        health_boost = min(0.2, len(matched_conditions) * 0.1)
                        score += health_boost
                        reasons.append(
                            f"accepts {', '.join(matched_conditions[:2])}"
                            + (" + more" if len(matched_conditions) > 2 else "")
                        )

        # Retrieval score boost
        if carrier in retrieval_scores:
            retrieval_boost = min(0.3, retrieval_scores[carrier] * 0.3)
            score += retrieval_boost
            if retrieval_boost > 0.1:
                reasons.append("strong KB match")

        # Cap score at 1.0
        score = min(1.0, score)

        # Format reason
        reason = "; ".join(reasons) if reasons else "Basic eligibility met"
        reason = reason[:200]  # Truncate to 200 chars

        return score, reason

    def _score_retrieval_only(
        self, client_input: ClientInput
    ) -> List[Tuple[str, str, float, str]]:
        """Fallback scoring using only retrieval (when no rules match).

        Args:
            client_input: Client input

        Returns:
            List of tuples: (carrier, product, confidence, reason)
        """
        retrieval_results = retriever_service.retrieve(client_input, top_k=20)

        # Group by carrier/product
        carrier_products = {}
        for metadata, similarity in retrieval_results:
            carrier = metadata.get("carrier_guess", "Unknown").strip()
            product = metadata.get("product_guess", "Product").strip()

            if not carrier or carrier == "Unknown":
                continue

            key = (carrier, product)
            if key not in carrier_products:
                carrier_products[key] = []
            carrier_products[key].append(similarity)

        # Score each carrier/product
        scored = []
        for (carrier, product), similarities in carrier_products.items():
            avg_sim = sum(similarities) / len(similarities)
            confidence = min(0.9, 0.4 + avg_sim * 0.5)  # Cap at 0.9 for retrieval-only
            reason = f"KB retrieval match (no explicit rules for {client_input.state})"
            scored.append((carrier, product, confidence, reason))

        return scored


class RankerService:
    """Service for ranking recommendations."""

    def rank(
        self, scored_candidates: List[Tuple[str, str, float, str]], top_n: int = 5
    ) -> List[Recommendation]:
        """Rank and convert scored candidates to recommendations.

        Args:
            scored_candidates: List of (carrier, product, confidence, reason)
            top_n: Number of top recommendations to return

        Returns:
            List of Recommendation objects
        """
        # Sort by confidence descending
        sorted_candidates = sorted(scored_candidates, key=lambda x: x[2], reverse=True)

        # Take top N
        top_candidates = sorted_candidates[:top_n]

        # Convert to Recommendation objects
        recommendations = []
        for carrier, product, confidence, reason in top_candidates:
            portal_url = portal_service.get_portal_url(carrier)

            rec = Recommendation(
                carrier=carrier,
                product=product,
                confidence=round(confidence, 2),
                reason=reason,
                portal_url=portal_url,
            )
            recommendations.append(rec)

        logger.info(f"Ranked top {len(recommendations)} recommendations")
        return recommendations


# Global service instances
scorer_service = ScorerService()
ranker_service = RankerService()
