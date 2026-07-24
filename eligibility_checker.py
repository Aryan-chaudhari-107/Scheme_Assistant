"""
eligibility_checker.py

Phase 4.3: Matching Logic.

check_eligibility(user_profile) loops through every scheme in
data/schemes.json and classifies each into one of three buckets:
  - "likely_eligible"     : passes every structured rule check
  - "likely_not_eligible" : fails at least one hard rule check
  - "check_manually"      : passes every checkable rule, BUT the scheme is
                             flagged complex_manual_check (Phase 4.2) -
                             e.g. depends on SECC/BPL database verification
                             we cannot determine from a self-reported form

This is 100% deterministic Python - NO LLM call happens in this file.
That's intentional: eligibility is a factual yes/no question with real
consequences, so it must never be at risk of an LLM hallucinating a
wrong threshold or inventing a criterion.

Usage:
    python eligibility_checker.py   # runs 6 hand-verified test profiles
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCHEMES_JSON = REPO_ROOT / "data" / "schemes.json"

# Maps a user profile's occupation dropdown value to the set of scheme
# `occupation` strings it should be considered compatible with, on top of
# "any" (which every occupation always matches).
OCCUPATION_COMPATIBILITY = {
    "farmer": {"farmer"},
    "artisan/craftsperson": {"artisan/craftsperson", "self-employed/artisan"},
    "small business owner/entrepreneur": {"small business owner/entrepreneur", "self-employed/artisan"},
    "student": {"student"},
    "unorganised sector worker": {"unorganised sector worker"},
    "homemaker": set(),
    "government employee": set(),
    "other": set(),
}


def _occupation_matches(user_occupation: str, scheme_occupation: str) -> bool:
    if scheme_occupation == "any":
        return True
    user_key = user_occupation.strip().lower()
    compatible = OCCUPATION_COMPATIBILITY.get(user_key, set())
    return scheme_occupation.strip().lower() in compatible


def _social_category_matches(user_category: str, scheme_category) -> bool:
    if scheme_category == "any":
        return True
    if isinstance(scheme_category, list):
        return user_category.strip().upper() in [c.strip().upper() for c in scheme_category]
    return user_category.strip().upper() == str(scheme_category).strip().upper()


def evaluate_scheme(profile: dict, scheme: dict) -> dict:
    """Evaluate one scheme's eligibility_rules against one user profile.

    Returns {"status": ..., "reasons": [list of failed/flagged criteria]}
    """
    rules = scheme["eligibility_rules"]
    reasons = []

    # For schemes about a family member (e.g. girl child under 10), the
    # applicant's own age/gender is not what min_age/max_age refers to -
    # skip the applicant age check for those, and check the flag instead.
    is_child_scheme = rules.get("requires_girl_child_under_10", False)

    if not is_child_scheme:
        if rules.get("min_age") is not None and profile["age"] < rules["min_age"]:
            reasons.append(f"age {profile['age']} is below minimum age {rules['min_age']}")
        if rules.get("max_age") is not None and profile["age"] > rules["max_age"]:
            reasons.append(f"age {profile['age']} is above maximum age {rules['max_age']}")

    if rules.get("max_income") is not None and profile["annual_family_income"] > rules["max_income"]:
        reasons.append(f"income {profile['annual_family_income']} exceeds limit {rules['max_income']}")

    if not _occupation_matches(profile["occupation"], rules.get("occupation", "any")):
        reasons.append(f"occupation '{profile['occupation']}' does not match required '{rules.get('occupation')}'")

    scheme_state = rules.get("state", "All India")
    if scheme_state != "All India" and profile["state"].strip().lower() != scheme_state.strip().lower():
        reasons.append(f"scheme is state-specific to {scheme_state}, but applicant is in {profile['state']}")

    if rules.get("gender", "any") != "any" and profile["gender"].strip().lower() != rules["gender"].strip().lower():
        reasons.append(f"scheme requires gender '{rules['gender']}'")

    if not _social_category_matches(profile.get("social_category", "General"), rules.get("social_category", "any")):
        reasons.append(f"social category '{profile.get('social_category')}' not in required categories {rules.get('social_category')}")

    if rules.get("marital_status", "any") != "any" and profile.get("marital_status", "").strip().lower() != rules["marital_status"].strip().lower():
        reasons.append(f"scheme requires marital status '{rules['marital_status']}'")

    if rules.get("owns_pucca_house_excluded") and profile.get("owns_pucca_house"):
        reasons.append("scheme excludes applicants who already own a pucca house")

    if rules.get("income_tax_payer_excluded") and profile.get("is_income_tax_payer"):
        reasons.append("scheme excludes income tax payers")

    if is_child_scheme and not profile.get("has_girl_child_under_10"):
        reasons.append("scheme requires a girl child under 10 in the family")

    if rules.get("requires_pregnant_or_recent_mother") and not profile.get("is_pregnant_or_recent_mother"):
        reasons.append("scheme requires the applicant to be pregnant or a recent mother")

    if reasons:
        return {"status": "likely_not_eligible", "reasons": reasons}

    if rules.get("complex_manual_check"):
        return {"status": "check_manually", "reasons": [rules.get("complex_reason", "Requires manual/official verification.")]}

    return {"status": "likely_eligible", "reasons": []}


def check_eligibility(user_profile: dict) -> dict:
    """Loop through all schemes and classify each for this user profile.

    Returns: {scheme_id: {"name": ..., "status": ..., "reasons": [...]}}
    """
    with open(SCHEMES_JSON, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    results = {}
    for scheme in schemes:
        result = evaluate_scheme(user_profile, scheme)
        results[scheme["scheme_id"]] = {
            "name": scheme["name"],
            "status": result["status"],
            "reasons": result["reasons"],
        }
    return results


# --- Phase 4.3 checkpoint: 6 hand-verified test profiles -------------------

TEST_PROFILES = [
    {
        "label": "1. Ramesh - Gujarat farmer, 35, income 2L, SC, not tax payer",
        "profile": {
            "age": 35, "annual_family_income": 200000, "state": "Gujarat",
            "occupation": "Farmer", "gender": "Male", "social_category": "SC",
            "marital_status": "Married", "owns_pucca_house": False,
            "is_income_tax_payer": False, "has_girl_child_under_10": False,
            "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "pm-kisan": "likely_eligible",
            "atal-pension-yojana": "likely_eligible",
            "mukhyamantri-gruh-yojana": "likely_eligible",
            "manav-garima-yojana": "likely_not_eligible",  # occupation mismatch (farmer, not artisan)
            "ayushman-bharat-pmjay": "likely_not_eligible",  # income exceeds proxy threshold
        },
    },
    {
        "label": "2. Priya - Gujarat mother with young daughter, 26, income 1L",
        "profile": {
            "age": 26, "annual_family_income": 100000, "state": "Gujarat",
            "occupation": "Homemaker", "gender": "Female", "social_category": "General",
            "marital_status": "Married", "owns_pucca_house": False,
            "is_income_tax_payer": False, "has_girl_child_under_10": True,
            "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "sukanya-samriddhi-yojana": "likely_eligible",
            "vahli-dikri-yojana": "likely_eligible",
            "pm-matru-vandana-yojana": "likely_not_eligible",  # not pregnant/recent mother
            "ganga-swaroop-yojana": "likely_not_eligible",  # not widowed
        },
    },
    {
        "label": "3. Fatima - Gujarat widow, 30, income 1L",
        "profile": {
            "age": 30, "annual_family_income": 100000, "state": "Gujarat",
            "occupation": "Other", "gender": "Female", "social_category": "General",
            "marital_status": "Widowed", "owns_pucca_house": False,
            "is_income_tax_payer": False, "has_girl_child_under_10": False,
            "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "ganga-swaroop-yojana": "likely_eligible",
            "pm-jeevan-jyoti-bima-yojana": "likely_eligible",
        },
    },
    {
        "label": "4. Arjun - Gujarat SC student, 17, family income 2L",
        "profile": {
            "age": 17, "annual_family_income": 200000, "state": "Gujarat",
            "occupation": "Student", "gender": "Male", "social_category": "SC",
            "marital_status": "Unmarried", "owns_pucca_house": False,
            "is_income_tax_payer": False, "has_girl_child_under_10": False,
            "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "gujarat-post-matric-scholarship": "likely_eligible",
            "nsp-post-matric-scholarship": "likely_eligible",
            "pm-vishwakarma-yojana": "likely_not_eligible",  # occupation + age mismatch
        },
    },
    {
        "label": "5. Suresh - senior citizen, 65, Other state, income 80k",
        "profile": {
            "age": 65, "annual_family_income": 80000, "state": "Other",
            "occupation": "Other", "gender": "Male", "social_category": "General",
            "marital_status": "Married", "owns_pucca_house": True,
            "is_income_tax_payer": False, "has_girl_child_under_10": False,
            "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "nsap-old-age-pension": "check_manually",  # passes age check, but flagged complex (SECC/BPL)
            "atal-pension-yojana": "likely_not_eligible",  # age exceeds 40 max
            "pm-suraksha-bima-yojana": "likely_eligible",
        },
    },
    {
        "label": "6. Neha - Other state business owner, 28, income 5L",
        "profile": {
            "age": 28, "annual_family_income": 500000, "state": "Other",
            "occupation": "Small Business Owner/Entrepreneur", "gender": "Female",
            "social_category": "General", "marital_status": "Unmarried",
            "owns_pucca_house": False, "is_income_tax_payer": True,
            "has_girl_child_under_10": False, "is_pregnant_or_recent_mother": False,
        },
        "expected": {
            "pm-mudra-yojana": "likely_eligible",
            "manav-garima-yojana": "likely_not_eligible",  # state mismatch (Gujarat only)
            "mukhyamantri-gruh-yojana": "likely_not_eligible",  # state mismatch
        },
    },
]


def run_tests():
    total_checks = 0
    passed_checks = 0

    print(f"Running {len(TEST_PROFILES)} hand-verified test profiles...\n")

    for case in TEST_PROFILES:
        print("=" * 70)
        print(case["label"])
        results = check_eligibility(case["profile"])

        for scheme_id, expected_status in case["expected"].items():
            actual = results[scheme_id]["status"]
            total_checks += 1
            ok = actual == expected_status
            if ok:
                passed_checks += 1
            status_tag = "PASS" if ok else "FAIL"
            print(f"  [{status_tag}] {scheme_id}: expected={expected_status}, actual={actual}")
            if not ok:
                print(f"         reasons: {results[scheme_id]['reasons']}")
        print()

    print("=" * 70)
    print(f"Summary: {passed_checks}/{total_checks} individual scheme checks passed")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()