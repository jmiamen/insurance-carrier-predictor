"""
Carrier portal URLs and contact information for agent quoting.

This module contains direct links to carrier agent portals and e-application systems.
"""

CARRIER_PORTALS = {
    "Elco Mutual": {
        "name": "Elco Mutual Life & Annuity",
        "portal_url": "https://elcomutual.com/agent-portal",
        "eapp_url": "https://elcomutual.com/e-app",
        "phone": "800-323-4656",
        "logo_filename": "elco-mutual.svg"
    },
    "Mutual of Omaha": {
        "name": "Mutual of Omaha",
        "portal_url": "https://www.mutualofomaha.com/agent",
        "eapp_url": "https://www.mutualofomaha.com/agent/apply",
        "phone": "800-775-6000",
        "logo_filename": "mutual-of-omaha.svg"
    },
    "Legal & General America": {
        "name": "Legal & General America",
        "portal_url": "https://www.lgamerica.com/agents",
        "eapp_url": "https://www.lgamerica.com/agents/eapp",
        "phone": "800-638-8428",
        "logo_filename": "legal-general-america.svg"
    },
    "Transamerica": {
        "name": "Transamerica",
        "portal_url": "https://www.transamerica.com/individual/life-insurance/agent-center",
        "eapp_url": "https://www.transamerica.com/individual/life-insurance/agent-center/eapp",
        "phone": "800-797-2643",
        "logo_filename": "transamerica.svg"
    },
    "Corebridge Financial": {
        "name": "Corebridge Financial",
        "portal_url": "https://www.corebridgefinancial.com/producers",
        "eapp_url": "https://www.corebridgefinancial.com/producers/eapp",
        "phone": "877-244-5263",
        "logo_filename": "corebridge-financial.svg"
    },
    "SBLI": {
        "name": "SBLI",
        "portal_url": "https://www.sbli.com/agents",
        "eapp_url": "https://www.sbli.com/agents/apply",
        "phone": "888-867-4662",
        "logo_filename": "sbli.svg"
    },
    "United Home Life": {
        "name": "United Home Life Insurance Company",
        "portal_url": "https://uhlic.com/agent-portal",
        "eapp_url": "https://uhlic.com/agent-portal/eapp",
        "phone": "877-894-5432",
        "logo_filename": "united-home-life.svg"
    },
    "Kansas City Life": {
        "name": "Kansas City Life Insurance Company",
        "portal_url": "https://www.kclife.com/agents",
        "eapp_url": "https://www.kclife.com/agents/eapp",
        "phone": "800-234-2KC",
        "logo_filename": "kansas-city-life.svg"
    }
}


def get_portal_info(carrier_name: str) -> dict:
    """
    Get portal information for a carrier.

    Args:
        carrier_name: Carrier name (case-insensitive partial match)

    Returns:
        Dict with portal_url, eapp_url, phone, logo_filename
        Returns empty dict with None values if not found
    """
    carrier_name_lower = carrier_name.lower()

    for carrier_key, info in CARRIER_PORTALS.items():
        if carrier_key.lower() in carrier_name_lower or carrier_name_lower in carrier_key.lower():
            return info

    # Not found - return empty dict
    return {
        "name": carrier_name,
        "portal_url": None,
        "eapp_url": None,
        "phone": None,
        "logo_filename": None
    }
