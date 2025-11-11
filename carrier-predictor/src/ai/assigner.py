"""
Rules-based carrier assignment engine.

Loads YAML product rules from carriers/ directory and performs deterministic
product matching based on client profile.
"""

import glob
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CarrierRule:
    """Represents a single carrier product with eligibility rules."""

    carrier: str
    product: str
    type: str
    synopsis: str
    face_amount: Dict[str, Any]
    issue_ages: Dict[str, Any]
    tobacco_classes: List[str]
    underwriting_type: str
    knockouts: Dict[str, Any]
    eligibility: Dict[str, Any]
    accepted: List[str] = None
    unique_advantages: List[str] = None
    limitations: List[str] = None
    tier_structure: Dict[str, str] = None
    notes: List[str] = None
    sources: List[Dict[str, str]] = None
    state_availability: Dict[str, Any] = None

    def supports_age(self, age: int) -> bool:
        """Check if age is within eligible range."""
        if not age:
            return False

        min_age = self.issue_ages.get('min', 0)
        max_age = self.issue_ages.get('max', 120)

        # Handle age-by-duration rules (e.g., term products)
        if 'by_duration' in self.issue_ages:
            # If we have duration-specific rules, check if ANY duration supports this age
            # Format: {10_year: [18, 60], 15_year: [18, 60], ...}
            for duration_data in self.issue_ages['by_duration'].values():
                if isinstance(duration_data, list) and len(duration_data) == 2:
                    if duration_data[0] <= age <= duration_data[1]:
                        return True
            return False

        return min_age <= age <= max_age

    def supports_face(self, face: int, age: int = None) -> bool:
        """Check if face amount is within eligible range."""
        if not face:
            return False

        # Handle face amount by age (common in term products)
        # Format: {18_45: [50000, 400000], 46_55: [50000, 300000], ...}
        if 'by_age' in self.face_amount:
            if not age:
                return False
            for age_range_key, face_range in self.face_amount['by_age'].items():
                # Parse age range from key like "18_45"
                if '_' in str(age_range_key):
                    parts = str(age_range_key).split('_')
                    if len(parts) == 2:
                        min_age = int(parts[0])
                        max_age = int(parts[1])
                        if min_age <= age <= max_age:
                            if isinstance(face_range, list) and len(face_range) == 2:
                                return face_range[0] <= face <= face_range[1]
            return False

        # Standard min/max
        min_face = self.face_amount.get('min', 0)
        max_face = self.face_amount.get('max', float('inf'))
        return min_face <= face <= max_face

    def passes_knockouts(self, profile: Dict[str, Any]) -> bool:
        """
        Check if profile passes knockout questions (strict disqualifiers).

        Returns True if eligible (no knockouts triggered), False if disqualified.
        """
        if not self.knockouts:
            return True

        # Handle different knockout structures
        for key, value in self.knockouts.items():
            if key in ['any', 'premier_plus', 'standard_graded']:
                # List of knockout conditions
                if isinstance(value, list):
                    for knockout in value:
                        if isinstance(knockout, dict):
                            # Each knockout is a dict like {hospice_care: true}
                            for condition, required_value in knockout.items():
                                if profile.get(condition) == required_value:
                                    return False
                elif isinstance(value, str) and value == "No health questions":
                    # GI products with no knockouts
                    continue

        return True

    def passes_health(self, profile: Dict[str, Any]) -> bool:
        """
        Check if profile meets health, driving, and felony requirements.

        Returns True if eligible, False otherwise.
        """
        if not self.eligibility:
            return True

        # Build chart (height/weight)
        if 'build' in self.eligibility:
            # For now, assume build is acceptable
            # In production, you'd implement actual build chart logic
            pass

        # Driving record
        if 'driving' in self.eligibility:
            driving_rules = self.eligibility['driving']

            # DUI lookback
            if 'dui_years_lookback' in driving_rules:
                lookback = driving_rules['dui_years_lookback']
                recent_duis = profile.get('dui_count_recent', 0)
                if recent_duis > driving_rules.get('max_dui_total', 0):
                    return False

            # Major violations
            if 'max_major_violations' in driving_rules:
                if profile.get('major_violations', 0) > driving_rules['max_major_violations']:
                    return False

        # Felony lookback
        if 'felony_lookback_years' in self.eligibility:
            if profile.get('felony_within_lookback', False):
                return False

        # Hazardous avocation
        if not self.eligibility.get('avocation_hazardous', True):
            if profile.get('hazardous_avocation', False):
                return False

        # Aviation
        if not self.eligibility.get('aviation', True):
            if profile.get('aviation_activity', False):
                return False

        # Nicotine/non-tobacco check
        if not self.eligibility.get('nicotine_non_tobacco_allowed', True):
            if profile.get('nicotine_use') and not profile.get('tobacco_use'):
                # Using nicotine but not tobacco (e.g., vaping) - not allowed
                return False

        return True

    def score(self, profile: Dict[str, Any]) -> float:
        """
        Calculate deterministic score for this product given the profile.

        Higher score = better match.

        Scoring factors:
        - Product type match (FE vs Term vs WL vs IUL)
        - Face amount fit (prefer products where requested amount is mid-range)
        - Age fit (prefer products where age is mid-range)
        - Underwriting leniency (Simplified > Full Medical, GI for impaired)
        - Tobacco class support
        """
        score = 0.0

        # 1. Product type match (40 points)
        desired_type = profile.get('coverage_type', '')
        if desired_type.lower() in self.type.lower():
            score += 40
        elif 'final expense' in self.type.lower() and desired_type.lower() in ['whole life', 'wl']:
            score += 30  # FE is a type of WL

        # 2. Face amount fit (20 points)
        requested_face = profile.get('desired_coverage', 0)
        if requested_face:
            min_face = self.face_amount.get('min', 0)
            max_face = self.face_amount.get('max', float('inf'))

            if isinstance(max_face, dict):
                # Handle by_age structures
                max_face = float('inf')

            if min_face <= requested_face <= max_face:
                # Calculate how centered the request is in the range
                midpoint = (min_face + max_face) / 2
                distance_from_mid = abs(requested_face - midpoint)
                max_distance = (max_face - min_face) / 2

                if max_distance > 0:
                    centrality = 1 - (distance_from_mid / max_distance)
                    score += 20 * centrality
                else:
                    score += 20

        # 3. Age fit (15 points)
        age = profile.get('age', 0)
        if age:
            min_age = self.issue_ages.get('min', 0)
            max_age = self.issue_ages.get('max', 120)

            if min_age <= age <= max_age:
                # Prefer products where age is in middle of range
                midpoint = (min_age + max_age) / 2
                distance_from_mid = abs(age - midpoint)
                max_distance = (max_age - min_age) / 2

                if max_distance > 0:
                    centrality = 1 - (distance_from_mid / max_distance)
                    score += 15 * centrality
                else:
                    score += 15

        # 4. Underwriting match (15 points)
        # Prefer simpler underwriting for impaired cases
        has_conditions = bool(profile.get('medical_conditions'))

        if 'Guaranteed Issue' in self.underwriting_type:
            if has_conditions:
                score += 15  # GI is great for impaired
            else:
                score += 5   # GI is okay for healthy (but not optimal)
        elif 'Simplified' in self.underwriting_type:
            score += 12  # Simplified is good for most cases
        elif 'Full Medical' in self.underwriting_type:
            if not has_conditions:
                score += 15  # Full medical is best for healthy
            else:
                score += 8   # Full medical okay for minor conditions

        # 5. Tobacco class support (10 points)
        is_tobacco = profile.get('smoker', False)
        tobacco_classes = [tc.lower() for tc in self.tobacco_classes]

        if is_tobacco and any('tobacco' in tc for tc in tobacco_classes):
            score += 10
        elif not is_tobacco and any('nontobacco' in tc or 'non-tobacco' in tc for tc in tobacco_classes):
            score += 10

        # 6. Multi-tier bonus (5 points)
        # Products with tier fallback are more likely to accept
        if self.tier_structure:
            score += 5

        # 7. State availability (bonus)
        state = profile.get('state', '')
        if self.state_availability:
            if self.state_availability.get('all_states', False):
                exceptions = self.state_availability.get('except', [])
                if state not in exceptions:
                    score += 3

        return score


def load_rules(carriers_dir: str = "carriers") -> List[CarrierRule]:
    """
    Load all YAML product rules from carriers directory.

    Returns list of CarrierRule objects.
    """
    rules = []

    # Get absolute path
    base_path = Path(__file__).parent.parent.parent / carriers_dir

    # Load all YAML files
    yaml_files = glob.glob(str(base_path / "**/*.yaml"), recursive=True)

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)

                if data:  # Skip empty files
                    rule = CarrierRule(
                        carrier=data.get('carrier', ''),
                        product=data.get('product', ''),
                        type=data.get('type', ''),
                        synopsis=data.get('synopsis', ''),
                        face_amount=data.get('face_amount', {}),
                        issue_ages=data.get('issue_ages', {}),
                        tobacco_classes=data.get('tobacco_classes', []),
                        underwriting_type=data.get('underwriting_type', ''),
                        knockouts=data.get('knockouts', {}),
                        eligibility=data.get('eligibility', {}),
                        accepted=data.get('accepted'),
                        unique_advantages=data.get('unique_advantages'),
                        limitations=data.get('limitations'),
                        tier_structure=data.get('tier_structure'),
                        notes=data.get('notes'),
                        sources=data.get('sources'),
                        state_availability=data.get('state_availability')
                    )
                    rules.append(rule)
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")

    return rules


def assign(profile: Dict[str, Any], rules: Optional[List[CarrierRule]] = None) -> List[Dict[str, Any]]:
    """
    Assign carrier products to a client profile using deterministic rules.

    Args:
        profile: Client profile dict with keys like age, desired_coverage, medical_conditions, etc.
        rules: List of CarrierRule objects (if None, will load from carriers/)

    Returns:
        List of top 3 eligible products, each with carrier, product, score, and rationale.
        Empty list if no products match.
    """
    if rules is None:
        rules = load_rules()

    eligible = []

    for rule in rules:
        # Check eligibility filters
        if not rule.supports_age(profile.get('age', 0)):
            continue

        if not rule.supports_face(profile.get('desired_coverage', 0), profile.get('age', 0)):
            continue

        if not rule.passes_knockouts(profile):
            continue

        if not rule.passes_health(profile):
            continue

        # Calculate score
        score = rule.score(profile)

        # Build rationale
        rationale = f"{rule.synopsis}"
        if rule.unique_advantages:
            rationale += f" • {rule.unique_advantages[0]}"

        eligible.append({
            'carrier': rule.carrier,
            'product': rule.product,
            'type': rule.type,
            'score': score,
            'rationale': rationale,
            'underwriting_type': rule.underwriting_type,
            'face_amount_range': f"${rule.face_amount.get('min', 0):,} - ${rule.face_amount.get('max', 0):,}",
            'issue_ages': f"{rule.issue_ages.get('min', 0)}-{rule.issue_ages.get('max', 0)}",
            'notes': rule.notes
        })

    # Sort by score descending and return top 3
    eligible.sort(key=lambda x: x['score'], reverse=True)
    return eligible[:3]


def render_response(profile: Dict[str, Any], picks: List[Dict[str, Any]]) -> str:
    """
    Format the response for API output.

    Args:
        profile: Client profile
        picks: List of recommended products from assign()

    Returns:
        Formatted string response
    """
    if not picks:
        return "Based on the provided information, we were unable to identify an eligible carrier product at this time. Please review the client's profile or contact underwriting for manual review."

    response = f"Based on {profile.get('first_name', 'the client')}'s profile:\n\n"

    for i, pick in enumerate(picks, 1):
        response += f"{i}. **{pick['carrier']} - {pick['product']}** ({pick['type']})\n"
        response += f"   - {pick['rationale']}\n"
        response += f"   - Underwriting: {pick['underwriting_type']}\n"
        response += f"   - Face Amount: {pick['face_amount_range']}\n"
        response += f"   - Issue Ages: {pick['issue_ages']}\n"

        if pick.get('notes'):
            response += f"   - Note: {pick['notes'][0]}\n"

        response += f"   - Match Score: {pick['score']:.1f}/100\n\n"

    return response
