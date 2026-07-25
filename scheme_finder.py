"""
scheme_finder.py

Version 2.0: Personalized Scheme Finder.

Builds on top of eligibility_checker.py WITHOUT modifying it (v1's
eligibility_checker.py stays exactly as tested/committed). This adds:

1. CATEGORIES - maps a user-facing category ("Farmer", "Student", "Woman",
   etc.) to just the profile fields actually relevant to that category, so
   the UI can ask a shorter, more relevant question set instead of all 11
   fields every time.

2. find_schemes(category, answers) - runs a WEIGHTED match score per
   scheme (0-100%) instead of a flat likely_eligible/not verdict:
   - Hard disqualifiers (age/state/gender/pucca-house-exclusion/etc. that
     are ACTUALLY ANSWERED) still cause an instant 0% - no partial credit
     for genuinely failing a real criterion.
   - Fields the user WASN'T asked about (because they're outside their
     category) default to a neutral "not counted against them" value,
     and are listed separately so the UI can be transparent that those
     weren't checked.
   - check_manually schemes are still kept separate, never given a score.

This is still 100% deterministic Python - no LLM involved in scoring.

Usage:
    python scheme_finder.py   # runs example searches for 3 categories
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCHEMES_JSON = REPO_ROOT / "data" / "schemes.json"

from eligibility_checker import _occupation_matches, _social_category_matches  # noqa: E402


# --- Category -> relevant fields mapping ------------------------------------
# Only these fields are asked/considered for each category. Everything else
# defaults to a neutral value (see NEUTRAL_DEFAULTS) and is flagged as
# "not checked" rather than silently assumed true or false.
CATEGORIES = {
    "Farmer": {
        "description": "Agricultural landholders and farming families",
        "fields": ["age", "annual_family_income", "state", "is_income_tax_payer"],
        "fixed_occupation": "Farmer",
    },
    "Student": {
        "description": "School and college students seeking scholarships",
        "fields": ["age", "annual_family_income", "state", "social_category"],
        "fixed_occupation": "Student",
    },
    "Woman": {
        "description": "Women-focused schemes (maternity, girl child, widow support)",
        "fields": ["age", "annual_family_income", "state", "marital_status",
                    "has_girl_child_under_10", "is_pregnant_or_recent_mother"],
        "fixed_gender": "Female",
    },
    "Senior Citizen": {
        "description": "Pension and old-age welfare schemes",
        "fields": ["age", "annual_family_income", "state"],
    },
    "MSME / Business Owner": {
        "description": "Small business, artisan, and self-employment schemes",
        "fields": ["age", "annual_family_income", "state", "occupation", "social_category"],
    },
    "General": {
        "description": "See everything - asks all 11 questions (same as the full Eligibility Checker)",
        "fields": ["age", "annual_family_income", "state", "occupation", "gender",
                    "social_category", "marital_status", "owns_pucca_house",
                    "is_income_tax_payer", "has_girl_child_under_10", "is_pregnant_or_recent_mother"],
    },
}

NEUTRAL_DEFAULTS = {
    "age": None, "annual_family_income": None, "state": "Other",
    "occupation": "Other", "gender": "Other", "social_category": "General",
    "marital_status": "Married", "owns_pucca_house": False,
    "is_income_tax_payer": False, "has_girl_child_under_10": False,
    "is_pregnant_or_recent_mother": False,
}


def build_profile_from_category(category: str, answers: dict) -> tuple[dict, set]:
    """Merge category-specific answers with neutral defaults for unasked fields.

    Returns (profile, unchecked_fields) where unchecked_fields is the set of
    field names NOT actually asked for this category - used to be transparent
    in the UI about what wasn't verified.
    """
    config = CATEGORIES[category]
    profile = dict(NEUTRAL_DEFAULTS)
    profile.update(answers)

    if "fixed_occupation" in config:
        profile["occupation"] = config["fixed_occupation"]
    if "fixed_gender" in config:
        profile["gender"] = config["fixed_gender"]

    asked_fields = set(config["fields"])
    if "fixed_occupation" in config:
        asked_fields.add("occupation")
    if "fixed_gender" in config:
        asked_fields.add("gender")

    all_fields = set(NEUTRAL_DEFAULTS.keys())
    unchecked_fields = all_fields - asked_fields

    return profile, unchecked_fields


def _score_scheme(profile: dict, unchecked_fields: set, scheme: dict) -> dict:
    """Weighted match score for one scheme against a (possibly partial) profile.

    IMPORTANT: a relevant criterion that was NOT asked (because it's outside
    the user's chosen category) is NOT silently skipped - it's counted as
    "unverified" and pulls the score below 100%, with the specific unverified
    criteria listed so the UI can be transparent ("this scheme also requires
    X, which we didn't ask about in the Woman category"). This prevents a
    scheme like Manav Garima Yojana (requires artisan occupation + SC/NT-DNT
    category) from falsely showing as a 100% match just because those two
    fields weren't part of the current category's question set.

    Any check involving an ANSWERED field that fails is still a hard
    disqualifier -> score 0, no partial credit.
    """
    rules = scheme["eligibility_rules"]

    if rules.get("complex_manual_check"):
        return {"score": None, "status": "check_manually", "matched": [], "unverified": [], "unchecked": sorted(unchecked_fields)}

    # (label, field_name, is_relevant, would_pass_if_checked_or_None)
    checks = []
    is_child_scheme = rules.get("requires_girl_child_under_10", False)

    if not is_child_scheme and (rules.get("min_age") is not None or rules.get("max_age") is not None):
        passed = None
        if profile["age"] is not None:
            passed = True
            if rules.get("min_age") is not None and profile["age"] < rules["min_age"]:
                passed = False
            if rules.get("max_age") is not None and profile["age"] > rules["max_age"]:
                passed = False
        checks.append(("Age within range", "age", passed))

    if rules.get("max_income") is not None:
        passed = None
        if profile["annual_family_income"] is not None:
            passed = profile["annual_family_income"] <= rules["max_income"]
        checks.append(("Income within limit", "annual_family_income", passed))

    if rules.get("occupation", "any") != "any":
        passed = None if "occupation" in unchecked_fields else _occupation_matches(profile["occupation"], rules["occupation"])
        checks.append(("Occupation matches", "occupation", passed))

    scheme_state = rules.get("state", "All India")
    if scheme_state != "All India":
        passed = None if "state" in unchecked_fields else profile["state"].strip().lower() == scheme_state.strip().lower()
        checks.append((f"State is {scheme_state}", "state", passed))

    if rules.get("gender", "any") != "any":
        passed = None if "gender" in unchecked_fields else profile["gender"].strip().lower() == rules["gender"].strip().lower()
        checks.append(("Gender matches", "gender", passed))

    if rules.get("social_category", "any") != "any":
        passed = None if "social_category" in unchecked_fields else _social_category_matches(profile.get("social_category", "General"), rules["social_category"])
        checks.append(("Social category matches", "social_category", passed))

    if rules.get("marital_status", "any") != "any":
        passed = None if "marital_status" in unchecked_fields else profile.get("marital_status", "").strip().lower() == rules["marital_status"].strip().lower()
        checks.append(("Marital status matches", "marital_status", passed))

    if rules.get("owns_pucca_house_excluded"):
        passed = None if "owns_pucca_house" in unchecked_fields else not profile.get("owns_pucca_house")
        checks.append(("Does not already own a pucca house", "owns_pucca_house", passed))

    if rules.get("income_tax_payer_excluded"):
        passed = None if "is_income_tax_payer" in unchecked_fields else not profile.get("is_income_tax_payer")
        checks.append(("Not an income tax payer", "is_income_tax_payer", passed))

    if is_child_scheme:
        passed = None if "has_girl_child_under_10" in unchecked_fields else bool(profile.get("has_girl_child_under_10"))
        checks.append(("Has a girl child under 10", "has_girl_child_under_10", passed))

    if rules.get("requires_pregnant_or_recent_mother"):
        passed = None if "is_pregnant_or_recent_mother" in unchecked_fields else bool(profile.get("is_pregnant_or_recent_mother"))
        checks.append(("Pregnant or recent mother", "is_pregnant_or_recent_mother", passed))

    if not checks:
        return {"score": None, "status": "not_applicable", "matched": [], "unverified": [], "unchecked": sorted(unchecked_fields)}

    # Any CHECKED criterion that failed = hard disqualifier, score 0.
    if any(passed is False for _, _, passed in checks):
        matched = [label for label, _, passed in checks if passed is True]
        return {"score": 0, "status": "not_a_match", "matched": matched, "unverified": [], "unchecked": sorted(unchecked_fields)}

    matched = [label for label, _, passed in checks if passed is True]
    unverified = [label for label, _, passed in checks if passed is None]

    score = round(100 * len(matched) / len(checks))
    status = "match" if score == 100 else "partial_match"

    return {"score": score, "status": status, "matched": matched, "unverified": unverified, "unchecked": sorted(unchecked_fields)}


def find_schemes(category: str, answers: dict) -> dict:
    """Personalized Scheme Finder entry point.

    Returns {"profile_used": dict, "unchecked_fields": [...],
             "matches": [scheme results sorted by score desc, 100% first],
             "check_manually": [...], "not_applicable": [...]}
    """
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category '{category}'. Valid: {list(CATEGORIES.keys())}")

    profile, unchecked_fields = build_profile_from_category(category, answers)

    with open(SCHEMES_JSON, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    matches, check_manually, not_applicable = [], [], []

    for scheme in schemes:
        result = _score_scheme(profile, unchecked_fields, scheme)
        entry = {
            "scheme_id": scheme["scheme_id"],
            "name": scheme["name"],
            "official_link": scheme.get("official_link", ""),
            **result,
        }
        if result["status"] == "check_manually":
            check_manually.append(entry)
        elif result["status"] == "not_applicable":
            not_applicable.append(entry)
        elif result["status"] in ("match", "partial_match") and result["score"] > 0:
            matches.append(entry)
        else:
            # partial_match with score 0 = zero positive signal (only
            # unverified criteria, nothing actually confirmed) - not
            # meaningfully a "match" worth showing, so it's excluded.
            not_applicable.append(entry)

    matches.sort(key=lambda e: e["score"], reverse=True)

    return {
        "profile_used": profile,
        "unchecked_fields": sorted(unchecked_fields),
        "matches": matches,
        "check_manually": check_manually,
        "not_applicable": not_applicable,
    }


# --- Example runs ------------------------------------------------------------

def main():
    examples = [
        ("Farmer", {"age": 35, "annual_family_income": 200000, "state": "Gujarat", "is_income_tax_payer": False}),
        ("Woman", {"age": 26, "annual_family_income": 100000, "state": "Gujarat", "marital_status": "Married",
                     "has_girl_child_under_10": True, "is_pregnant_or_recent_mother": False}),
        ("Student", {"age": 17, "annual_family_income": 200000, "state": "Gujarat", "social_category": "SC"}),
    ]

    for category, answers in examples:
        print("=" * 70)
        print(f"Category: {category}  |  Answers: {answers}")
        result = find_schemes(category, answers)
        print(f"Fields NOT asked (neutral, not counted): {result['unchecked_fields']}")
        print(f"\nMatches ({len(result['matches'])}):")
        for m in result["matches"]:
            print(f"  {m['score']}% - {m['name']}")
            print(f"      matched on: {m['matched']}")
            if m["unverified"]:
                print(f"      NOT verified (outside category): {m['unverified']}")
        print(f"\nCheck manually ({len(result['check_manually'])}): {[m['name'] for m in result['check_manually']]}")
        print()


if __name__ == "__main__":
    main()