"""
update_eligibility_rules.py

Phase 4.2: Eligibility Rule Encoding.

One-time script: patches the eligibility_rules object in every scheme
JSON file in data/schemes/ with the expanded field set decided in Phase
4.1 (gender, social_category, marital_status, owns_pucca_house_excluded,
income_tax_payer_excluded, requires_girl_child_under_10,
requires_pregnant_or_recent_mother), plus complex_manual_check flags for
schemes whose real eligibility depends on external government database
verification (SECC/BPL status) rather than simple structured fields.

Existing min_age/max_age/max_income/occupation/state values are kept as
they already were - only new fields are added, nothing is removed.

Run this ONCE. Safe to re-run (idempotent - just overwrites with the same
values again).

Usage:
    python update_eligibility_rules.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCHEMES_DIR = REPO_ROOT / "data" / "schemes"

# New fields to merge into each scheme's existing eligibility_rules object.
# Fields not mentioned for a scheme default to: gender="any",
# social_category="any", marital_status="any", owns_pucca_house_excluded=False,
# income_tax_payer_excluded=False, requires_girl_child_under_10=False,
# requires_pregnant_or_recent_mother=False, complex_manual_check=False.
RULE_UPDATES = {
    "atal-pension-yojana": {"income_tax_payer_excluded": True},
    "ayushman-bharat-pmjay": {
        "max_income": 120000,  # corrected: was a monthly figure (10,000) mistakenly stored as annual
        "complex_manual_check": True,
        "complex_reason": "True eligibility is based on SECC 2011 deprivation category, not simply annual income. Income is used here only as a rough proxy.",
    },
    "e-shram": {"income_tax_payer_excluded": True},
    "ganga-swaroop-yojana": {"gender": "female", "marital_status": "widowed"},
    "gujarat-post-matric-scholarship": {"social_category": ["SC", "ST", "OBC/SEBC", "EBC", "NT-DNT", "Minority"]},
    "manav-garima-yojana": {"social_category": ["SC", "NT-DNT"]},
    "mukhyamantri-gruh-yojana": {"owns_pucca_house_excluded": True},
    "nsap-old-age-pension": {
        "complex_manual_check": True,
        "complex_reason": "Requires BPL/SECC-2011 household verification, not a simple income cutoff a self-reported form can determine.",
    },
    "nsp-post-matric-scholarship": {"social_category": ["SC", "ST", "OBC", "EBC"]},
    "nsp-pre-matric-scholarship": {"social_category": ["SC", "ST", "OBC"]},
    "pm-kisan": {"income_tax_payer_excluded": True},
    "pm-matru-vandana-yojana": {"gender": "female", "requires_pregnant_or_recent_mother": True},
    "pm-ujjwala-yojana": {"gender": "female"},
    "pmay-gramin": {
        "complex_manual_check": True,
        "complex_reason": "Requires appearance in SECC 2011 / Awaas+ survey data verified by the gram sabha - not determinable from self-reported fields alone.",
    },
    "pmay-urban": {"owns_pucca_house_excluded": True},
    "sukanya-samriddhi-yojana": {"requires_girl_child_under_10": True},
    "vahli-dikri-yojana": {"requires_girl_child_under_10": True},
    # All other schemes (atal-pension-yojana already covered above; the rest
    # get only the shared defaults below, no scheme-specific overrides needed):
}

DEFAULTS = {
    "gender": "any",
    "social_category": "any",
    "marital_status": "any",
    "owns_pucca_house_excluded": False,
    "income_tax_payer_excluded": False,
    "requires_girl_child_under_10": False,
    "requires_pregnant_or_recent_mother": False,
    "complex_manual_check": False,
    "complex_reason": None,
}


def main():
    files = sorted(SCHEMES_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No JSON files found in {SCHEMES_DIR}")

    updated = 0
    flagged_complex = []

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scheme_id = data["scheme_id"]
        rules = data.get("eligibility_rules", {})

        # Merge: start from defaults, keep existing min_age/max_age/max_income/
        # occupation/state as-is, then apply any scheme-specific overrides.
        merged = {**DEFAULTS, **rules}
        merged.update(RULE_UPDATES.get(scheme_id, {}))

        data["eligibility_rules"] = merged

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        updated += 1
        if merged.get("complex_manual_check"):
            flagged_complex.append(scheme_id)
        print(f"Updated {scheme_id} ({file_path.name})")

    print()
    print(f"Total schemes updated: {updated}")
    print(f"Flagged as complex (manual verification needed): {flagged_complex}")


if __name__ == "__main__":
    main()