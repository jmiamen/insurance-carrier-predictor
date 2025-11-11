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
from .carrier_portals import get_portal_info


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
    riders: List[str] = None  # Available riders/living benefits
    am_best_rating: str = None  # A.M. Best financial strength rating
    typical_premium_tier: str = None  # "low", "medium", "high" for budget comparison

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

        # Build chart (height/weight/BMI validation)
        if 'build' in self.eligibility:
            build_rules = self.eligibility['build']

            # Calculate BMI if height and weight provided
            height_ft = profile.get('height_ft')
            height_in = profile.get('height_in')
            weight = profile.get('weight')
            gender = profile.get('gender', 'M')

            if height_ft and height_in and weight:
                # Convert to metric for BMI calculation
                total_inches = (height_ft * 12) + height_in
                height_meters = total_inches * 0.0254
                weight_kg = weight * 0.453592
                bmi = weight_kg / (height_meters ** 2)

                # Check against max BMI thresholds
                if 'max_bmi' in build_rules:
                    max_bmi = build_rules['max_bmi']

                    # Handle gender-specific BMI limits
                    if isinstance(max_bmi, dict):
                        if gender in max_bmi:
                            if bmi > max_bmi[gender]:
                                return False
                        elif 'standard' in max_bmi:
                            if bmi > max_bmi['standard']:
                                return False
                    elif isinstance(max_bmi, (int, float)):
                        if bmi > max_bmi:
                            return False

                # Check against min/max weight by height if specified
                if 'weight_by_height' in build_rules:
                    height_key = f"{height_ft}_{height_in}"
                    if height_key in build_rules['weight_by_height']:
                        weight_range = build_rules['weight_by_height'][height_key]
                        if isinstance(weight_range, list) and len(weight_range) == 2:
                            if not (weight_range[0] <= weight <= weight_range[1]):
                                return False

        # Medication-specific acceptance
        if 'medications' in self.eligibility:
            medication_rules = self.eligibility['medications']
            profile_meds = profile.get('medications', [])

            # Check if any medications are explicitly rejected
            if 'rejected' in medication_rules:
                for med in profile_meds:
                    if med.lower() in [m.lower() for m in medication_rules['rejected']]:
                        return False

            # Check if required medications are missing (for certain conditions)
            if 'required_for' in medication_rules:
                for condition, required_meds in medication_rules['required_for'].items():
                    # If condition is present, check medications
                    if profile.get(condition, False):
                        has_required = any(
                            med.lower() in [m.lower() for m in profile_meds]
                            for med in required_meds
                        )
                        if required_meds and not has_required:
                            return False

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

        Enhanced GPT-brain-inspired scoring algorithm.
        Higher score = better match.

        Scoring weights (inspired by GPT brain logic):
        - 30% Underwriting Fit (build, health, tobacco, medications)
        - 25% Product Type/Term Structure Fit
        - 20% Riders/Living Benefits Match
        - 15% Face Amount/Budget Alignment
        - 10% Carrier Quality & Multi-tier Flexibility
        """
        score = 0.0

        # === 1. UNDERWRITING FIT (30 points) ===
        uw_fit_score = 0.0

        # Build/BMI fit (10 points)
        height_ft = profile.get('height_ft')
        height_in = profile.get('height_in')
        weight = profile.get('weight')

        if height_ft and height_in and weight:
            total_inches = (height_ft * 12) + height_in
            height_meters = total_inches * 0.0254
            weight_kg = weight * 0.453592
            bmi = weight_kg / (height_meters ** 2)

            # Reward products with lenient build requirements
            if 'build' in self.eligibility and 'max_bmi' in self.eligibility['build']:
                max_bmi = self.eligibility['build']['max_bmi']
                if isinstance(max_bmi, dict):
                    max_bmi = max_bmi.get('standard', 40)

                # More lenient = higher score
                if bmi <= max_bmi * 0.85:  # Well within limits
                    uw_fit_score += 10
                elif bmi <= max_bmi:  # Within limits
                    uw_fit_score += 7
            else:
                uw_fit_score += 10  # No BMI restriction = best

        else:
            uw_fit_score += 10  # No data provided, assume acceptable

        # Health conditions acceptance (10 points)
        medical_conditions = profile.get('medical_conditions', {})
        has_conditions = any(medical_conditions.values()) if isinstance(medical_conditions, dict) else bool(medical_conditions)

        if 'Guaranteed Issue' in self.underwriting_type:
            uw_fit_score += 10 if has_conditions else 6
        elif 'Simplified' in self.underwriting_type:
            uw_fit_score += 9
        elif 'Full Medical' in self.underwriting_type:
            uw_fit_score += 10 if not has_conditions else 7

        # Tobacco fit (5 points)
        tobacco_status = profile.get('tobacco_status', 'non-tobacco' if not profile.get('smoker') else 'tobacco')
        tobacco_classes = [tc.lower() for tc in self.tobacco_classes]

        if tobacco_status == 'tobacco' and any('tobacco' in tc for tc in tobacco_classes):
            uw_fit_score += 5
        elif tobacco_status in ['non-tobacco', 'former'] and any('nontobacco' in tc or 'non-tobacco' in tc for tc in tobacco_classes):
            uw_fit_score += 5

        # Medication acceptance (5 points)
        if 'medications' in self.eligibility:
            uw_fit_score += 3  # Has specific medication rules (more refined)
        else:
            uw_fit_score += 5  # No medication restrictions

        score += uw_fit_score

        # === 2. PRODUCT TYPE/TERM FIT (25 points) ===
        type_score = 0.0
        desired_type = profile.get('coverage_type', '')

        # Exact type match
        if desired_type.lower() in self.type.lower():
            type_score += 20
        elif 'final expense' in self.type.lower() and desired_type.lower() in ['whole life', 'wl']:
            type_score += 18

        # Term duration match (if applicable)
        if 'term' in self.type.lower() and 'term' in desired_type.lower():
            # Check if we have duration-specific rules
            if 'by_duration' in self.issue_ages:
                type_score += 5  # Bonus for multiple duration options

        score += type_score

        # === 3. RIDERS/LIVING BENEFITS (20 points) ===
        rider_score = 0.0
        desired_riders = profile.get('rider_preferences', [])

        if self.riders:
            available_riders_lower = [r.lower() for r in self.riders]

            if desired_riders:
                # Check how many desired riders are available
                matches = sum(1 for r in desired_riders if any(r.lower() in ar for ar in available_riders_lower))
                if len(desired_riders) > 0:
                    rider_score += 20 * (matches / len(desired_riders))
            else:
                # No specific preferences, reward having many riders
                rider_score += min(20, len(self.riders) * 4)
        else:
            # No rider data in YAML, give neutral score
            rider_score += 10

        score += rider_score

        # === 4. FACE AMOUNT/BUDGET ALIGNMENT (15 points) ===
        budget_score = 0.0
        requested_face = profile.get('desired_coverage', 0)

        if requested_face:
            min_face = self.face_amount.get('min', 0)
            max_face = self.face_amount.get('max', float('inf'))

            if isinstance(max_face, dict):
                max_face = float('inf')

            if min_face <= requested_face <= max_face:
                # Centrality scoring (prefer mid-range)
                midpoint = (min_face + max_face) / 2
                distance_from_mid = abs(requested_face - midpoint)
                max_distance = (max_face - min_face) / 2

                if max_distance > 0:
                    centrality = 1 - (distance_from_mid / max_distance)
                    budget_score += 10 * centrality
                else:
                    budget_score += 10

        # Premium tier consideration (5 points)
        if self.typical_premium_tier:
            if self.typical_premium_tier == 'low':
                budget_score += 5
            elif self.typical_premium_tier == 'medium':
                budget_score += 3
            # High tier gets 0 bonus

        score += budget_score

        # === 5. CARRIER QUALITY & FLEXIBILITY (10 points) ===
        quality_score = 0.0

        # A.M. Best rating (5 points)
        if self.am_best_rating:
            rating = self.am_best_rating.upper()
            if 'A++' in rating or 'A+' in rating:
                quality_score += 5
            elif 'A' in rating:
                quality_score += 4
            elif 'B++' in rating or 'B+' in rating:
                quality_score += 3
            else:
                quality_score += 2
        else:
            quality_score += 3  # Unknown rating

        # Multi-tier flexibility (3 points)
        if self.tier_structure:
            quality_score += 3

        # Age fit bonus (2 points) - prefer products targeting client's age range
        age = profile.get('age', 0)
        if age:
            min_age = self.issue_ages.get('min', 0)
            max_age = self.issue_ages.get('max', 120)

            if min_age <= age <= max_age:
                midpoint = (min_age + max_age) / 2
                distance_from_mid = abs(age - midpoint)
                max_distance = (max_age - min_age) / 2

                if max_distance > 0:
                    centrality = 1 - (distance_from_mid / max_distance)
                    quality_score += 2 * centrality

        score += quality_score

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
                        state_availability=data.get('state_availability'),
                        riders=data.get('riders'),
                        am_best_rating=data.get('am_best_rating'),
                        typical_premium_tier=data.get('typical_premium_tier')
                    )
                    rules.append(rule)
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")

    return rules


def assign(profile: Dict[str, Any], rules: Optional[List[CarrierRule]] = None) -> Dict[str, Any]:
    """
    Assign carrier products to a client profile using deterministic rules.

    Args:
        profile: Client profile dict with keys like age, desired_coverage, medical_conditions, etc.
        rules: List of CarrierRule objects (if None, will load from carriers/)

    Returns:
        Dict with:
            - recommendations: List of top 3 eligible products
            - best_match: Highest scoring product
            - budget_options: Products with low premium tier
            - alternatives: Simplified/GI fallback options
    """
    if rules is None:
        rules = load_rules()

    # Prior decline handling - filter out full underwriting if declined before
    prior_decline = profile.get('prior_decline', False)
    prior_decline_carrier = profile.get('prior_decline_carrier', '').lower()

    eligible = []
    all_scored = []  # Keep all products for categorization

    for rule in rules:
        # Skip carrier that previously declined (if specified)
        if prior_decline_carrier and prior_decline_carrier in rule.carrier.lower():
            continue

        # Skip full underwriting if prior decline (unless multi-tier)
        if prior_decline and 'Full Medical' in rule.underwriting_type and not rule.tier_structure:
            continue

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

        # Get portal information for carrier
        portal_info = get_portal_info(rule.carrier)

        product_info = {
            'carrier': rule.carrier,
            'product': rule.product,
            'type': rule.type,
            'score': score,
            'rationale': rationale,
            'underwriting_type': rule.underwriting_type,
            'face_amount_range': f"${rule.face_amount.get('min', 0):,} - ${rule.face_amount.get('max', 0):,}",
            'issue_ages': f"{rule.issue_ages.get('min', 0)}-{rule.issue_ages.get('max', 0)}",
            'notes': rule.notes,
            'riders': rule.riders,
            'am_best_rating': rule.am_best_rating,
            'premium_tier': rule.typical_premium_tier,
            'tier_structure': rule.tier_structure,
            'portal_url': portal_info['portal_url'],
            'eapp_url': portal_info['eapp_url'],
            'phone': portal_info['phone'],
            'logo_filename': portal_info['logo_filename']
        }

        all_scored.append(product_info)
        eligible.append(product_info)

    # Sort by score descending
    eligible.sort(key=lambda x: x['score'], reverse=True)

    # Categorize recommendations (GPT brain style)
    best_match = eligible[0] if eligible else None

    # Budget options: low premium tier products
    budget_options = [p for p in eligible if p.get('premium_tier') == 'low'][:2]

    # Alternatives: Simplified/GI products (fallback options)
    alternatives = [
        p for p in eligible
        if 'Simplified' in p['underwriting_type'] or 'Guaranteed Issue' in p['underwriting_type']
    ][:2]

    return {
        'recommendations': eligible[:3],
        'best_match': best_match,
        'budget_options': budget_options,
        'alternatives': alternatives
    }


def render_response(profile: Dict[str, Any], result: Dict[str, Any]) -> str:
    """
    Format the response for API output with outcome categorization.

    Args:
        profile: Client profile
        result: Dict from assign() with recommendations, best_match, budget_options, alternatives

    Returns:
        Formatted string response
    """
    recommendations = result.get('recommendations', [])

    if not recommendations:
        return "Based on the provided information, we were unable to identify an eligible carrier product at this time. Please review the client's profile or contact underwriting for manual review."

    response = f"Based on {profile.get('first_name', 'the client')}'s profile:\n\n"

    # Best Match section
    best_match = result.get('best_match')
    if best_match:
        response += "### 🏆 BEST MATCH\n\n"
        response += f"**{best_match['carrier']} - {best_match['product']}** ({best_match['type']})\n"
        response += f"- {best_match['rationale']}\n"
        response += f"- Underwriting: {best_match['underwriting_type']}\n"
        response += f"- Face Amount: {best_match['face_amount_range']}\n"
        response += f"- Issue Ages: {best_match['issue_ages']}\n"

        if best_match.get('am_best_rating'):
            response += f"- A.M. Best Rating: {best_match['am_best_rating']}\n"

        if best_match.get('riders'):
            response += f"- Living Benefits: {', '.join(best_match['riders'][:3])}\n"

        if best_match.get('notes'):
            response += f"- Note: {best_match['notes'][0]}\n"

        response += f"- Match Score: {best_match['score']:.1f}/100\n\n"

    # Budget Options
    budget_options = result.get('budget_options', [])
    if budget_options:
        response += "### 💰 BUDGET OPTIONS\n\n"
        for pick in budget_options[:2]:
            response += f"**{pick['carrier']} - {pick['product']}** ({pick['type']})\n"
            response += f"- {pick['rationale']}\n"
            response += f"- Lower premium tier\n"
            response += f"- Match Score: {pick['score']:.1f}/100\n\n"

    # Alternatives (Simplified/GI fallback)
    alternatives = result.get('alternatives', [])
    if alternatives and len(recommendations) > 1:
        response += "### 🧩 ALTERNATIVE OPTIONS\n\n"
        for pick in alternatives[:2]:
            if pick not in [best_match]:  # Don't duplicate best match
                response += f"**{pick['carrier']} - {pick['product']}** ({pick['type']})\n"
                response += f"- {pick['rationale']}\n"
                response += f"- Simplified underwriting (easier placement)\n"
                response += f"- Match Score: {pick['score']:.1f}/100\n\n"

    # All recommendations summary
    if len(recommendations) > 1:
        response += "### 📋 ALL RECOMMENDATIONS\n\n"
        for i, pick in enumerate(recommendations, 1):
            response += f"{i}. {pick['carrier']} - {pick['product']} (Score: {pick['score']:.1f}/100)\n"

    return response
