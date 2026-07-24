"""
tests/test_eligibility_edge_cases.py

Phase 4.5: Edge Case Testing.

Stress-tests check_eligibility() (Phase 4.3) and explain_eligibility()
(Phase 4.4) against realistic messy/boundary inputs:
  - Borderline age (exactly at min_age/max_age, and just outside)
  - Borderline income (exactly at max_income, and just above)
  - A profile matching MANY schemes at once
  - A profile matching almost NO schemes
  - "check_manually" triggers, confirmed to explain ambiguity honestly
    rather than guessing a yes/no

Writes a full results log to tests/eligibility_edge_case_results.md.

Usage:
    python tests/test_eligibility_edge_cases.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from eligibility_checker import check_eligibility  # noqa: E402
from eligibility_explainer import explain_eligibility  # noqa: E402

RESULTS_FILE = REPO_ROOT / "tests" / "eligibility_edge_case_results.md"

BASE_PROFILE = {
    "age": 30, "annual_family_income": 100000, "state": "Other",
    "occupation": "Other", "gender": "Male", "social_category": "General",
    "marital_status": "Married", "owns_pucca_house": False,
    "is_income_tax_payer": False, "has_girl_child_under_10": False,
    "is_pregnant_or_recent_mother": False,
}


def profile_with(**overrides):
    return {**BASE_PROFILE, **overrides}


def main():
    log = []

    def record(title, detail):
        print(f"\n{'=' * 70}\n{title}\n{'-' * 70}")
        print(detail)
        log.append((title, detail))

    # --- 1. Borderline age: exactly at Atal Pension Yojana's 18-40 range ---
    for age, expected in [(18, "likely_eligible"), (40, "likely_eligible"), (17, "likely_not_eligible"), (41, "likely_not_eligible")]:
        results = check_eligibility(profile_with(age=age))
        actual = results["atal-pension-yojana"]["status"]
        ok = actual == expected
        record(
            f"Borderline age {age} (Atal Pension Yojana, range 18-40)",
            f"Expected: {expected} | Actual: {actual} | {'PASS' if ok else 'FAIL'}\n"
            f"Reasons: {results['atal-pension-yojana']['reasons']}",
        )

    # --- 2. Borderline income: exactly at PMAY-Urban's Rs. 9,00,000 cutoff ---
    for income, expected in [(900000, "likely_eligible"), (900001, "likely_not_eligible")]:
        results = check_eligibility(profile_with(annual_family_income=income, owns_pucca_house=False))
        actual = results["pmay-urban"]["status"]
        ok = actual == expected
        record(
            f"Borderline income Rs. {income:,} (PMAY-Urban, cutoff Rs. 9,00,000)",
            f"Expected: {expected} | Actual: {actual} | {'PASS' if ok else 'FAIL'}\n"
            f"Reasons: {results['pmay-urban']['reasons']}",
        )

    # --- 3. Multi-match profile: general adult, should qualify for several schemes at once ---
    multi_profile = profile_with(age=30, annual_family_income=150000, owns_pucca_house=False)
    results = check_eligibility(multi_profile)
    eligible = [sid for sid, r in results.items() if r["status"] == "likely_eligible"]
    record(
        "Multi-match profile (general adult, age 30, income 1.5L, no pucca house)",
        f"Number of schemes marked likely_eligible: {len(eligible)}\n"
        f"Schemes: {eligible}\n"
        f"{'PASS (matches multiple schemes as expected)' if len(eligible) >= 4 else 'FAIL (expected 4+ matches)'}",
    )

    # --- 4. No/near-no-match profile: high income, wrong state/occupation, owns house, tax payer ---
    no_match_profile = profile_with(
        age=45, annual_family_income=2000000, state="Other", occupation="Government Employee",
        gender="Male", social_category="General", marital_status="Married",
        owns_pucca_house=True, is_income_tax_payer=True,
    )
    results = check_eligibility(no_match_profile)
    eligible = [sid for sid, r in results.items() if r["status"] == "likely_eligible"]
    record(
        "No/near-no-match profile (high income, govt employee, owns house, tax payer)",
        f"Number of schemes marked likely_eligible: {len(eligible)}\n"
        f"Schemes: {eligible}\n"
        f"{'PASS (correctly near-zero matches)' if len(eligible) <= 3 else 'FAIL (expected 0-3 matches)'}\n"
        f"Note: any remaining matches should be genuinely universal, no-restriction schemes (e.g. PM Jan Dhan Yojana), which is correct behavior, not a bug.",
    )

    # --- 5a. check_manually trigger: NSAP (age-eligible senior, no disqualifiers) ---
    senior_profile = profile_with(age=65, annual_family_income=80000, owns_pucca_house=False)
    results = check_eligibility(senior_profile)
    nsap_result = results["nsap-old-age-pension"]
    explanation = explain_eligibility(nsap_result, senior_profile, "english")
    record(
        "check_manually trigger: NSAP Old Age Pension (age 65, otherwise clean profile)",
        f"Status: {nsap_result['status']} | {'PASS' if nsap_result['status'] == 'check_manually' else 'FAIL'}\n"
        f"Explanation: {explanation}\n"
        f"{'PASS (explanation communicates ambiguity, not a guess)' if 'verif' in explanation.lower() or 'manual' in explanation.lower() or 'confirm' in explanation.lower() else 'FLAG FOR REVIEW'}",
    )

    # --- 5b. check_manually trigger: PMAY-Gramin, houseless profile (should be check_manually) ---
    houseless_profile = profile_with(owns_pucca_house=False)
    results = check_eligibility(houseless_profile)
    gramin_result = results["pmay-gramin"]
    record(
        "check_manually trigger: PMAY-Gramin, houseless profile (owns_pucca_house=False)",
        f"Status: {gramin_result['status']} | Expected: check_manually | "
        f"{'PASS' if gramin_result['status'] == 'check_manually' else 'FAIL'}\n"
        f"Reasons: {gramin_result['reasons']}",
    )

    # --- 5c. Regression check for the Phase 4.5 fix: PMAY-Gramin, pucca-house-owning profile (should now be likely_not_eligible, not check_manually) ---
    pucca_owner_profile = profile_with(owns_pucca_house=True)
    results = check_eligibility(pucca_owner_profile)
    gramin_result2 = results["pmay-gramin"]
    record(
        "Regression check (Phase 4.5 fix): PMAY-Gramin, profile OWNS a pucca house",
        f"Status: {gramin_result2['status']} | Expected: likely_not_eligible | "
        f"{'PASS' if gramin_result2['status'] == 'likely_not_eligible' else 'FAIL - fix did not apply, re-run update_eligibility_rules.py'}\n"
        f"Reasons: {gramin_result2['reasons']}",
    )

    write_results_file(log)
    print(f"\n\nFull results written to: {RESULTS_FILE}")


def write_results_file(log):
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    lines = ["# Phase 4.5 - Eligibility Edge Case Test Results\n"]
    for title, detail in log:
        lines.append(f"## {title}\n")
        lines.append(f"```\n{detail}\n```\n")
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()