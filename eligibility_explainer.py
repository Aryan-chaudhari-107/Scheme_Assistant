"""
eligibility_explainer.py

Phase 4.4: LLM Explanation Layer.

explain_eligibility(scheme_result, user_profile, language) takes the
ALREADY-DECIDED rule-based verdict from eligibility_checker.py (Phase 4.3)
and asks the LLM to explain it in warm, plain language - in the user's
chosen language, using the same translate_response() machinery from
Module 3.

CRITICAL DESIGN RULE: the LLM never makes or changes the eligibility
decision here. It only explains a decision that was already made by
pure Python rule-checking. The prompt explicitly forbids contradicting
the given verdict, and a lightweight post-generation sanity check flags
(does not silently allow) any explanation that looks like it might have
overridden the verdict, so a human can review it.

Usage:
    python eligibility_explainer.py   # runs built-in test cases
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from rag import client, GEMINI_MODEL  # reuse the same Gemini client/model as the rest of the app
from google.genai import types

EXPLAIN_SYSTEM_PROMPT = """You are explaining a government scheme eligibility result to a user in India.

You are given a VERDICT that has ALREADY been decided by a separate, purely rule-based system.
Your ONLY job is to explain that verdict in warm, clear, plain language. You must NEVER contradict,
soften, or override the given verdict - you are not deciding eligibility, only explaining a decision
someone else already made.

Rules you MUST follow:
1. If VERDICT is "likely_eligible": clearly confirm they likely qualify, and briefly say why (based on the reasons/profile given), in an encouraging tone.
2. If VERDICT is "likely_not_eligible": clearly and kindly explain they likely do NOT qualify, and explain which specific criteria were not met (from the reasons given). Do not soften this into sounding like they might still qualify.
3. If VERDICT is "check_manually": clearly explain that this needs manual/official verification (explain why, from the reasons given), and that we cannot give a confident yes/no ourselves.
4. NEVER state or imply a different verdict than the one given to you.
5. NEVER invent additional eligibility criteria not present in the reasons given.
6. Keep it to 2-4 sentences, friendly and respectful, avoiding bureaucratic jargon.
7. Respond only in the requested language, in natural fluent text.
"""


def _build_explain_prompt(scheme_result: dict, user_profile: dict) -> str:
    reasons_text = "; ".join(scheme_result["reasons"]) if scheme_result["reasons"] else "all checked criteria were met"
    return f"""VERDICT: {scheme_result['status']}
SCHEME NAME: {scheme_result['name']}
REASONS (already determined by rule-based code, do not add to or contradict these): {reasons_text}
USER PROFILE SUMMARY: age {user_profile.get('age')}, annual family income Rs. {user_profile.get('annual_family_income')}, state {user_profile.get('state')}, occupation {user_profile.get('occupation')}.

Write the explanation now."""


# Keyword pairs that would indicate a suspicious contradiction if they appear
# opposite to the verdict - used only as a lightweight safety flag, not a filter.
_POSITIVE_HINTS = ["you are eligible", "you qualify", "you can apply and receive", "you likely qualify"]
_NEGATIVE_HINTS = ["you are not eligible", "you do not qualify", "unfortunately, you do not"]


def _flag_possible_contradiction(status: str, explanation_lower: str) -> bool:
    if status == "likely_not_eligible" and any(p in explanation_lower for p in _POSITIVE_HINTS):
        return True
    if status == "likely_eligible" and any(n in explanation_lower for n in _NEGATIVE_HINTS):
        return True
    return False


def explain_eligibility(scheme_result: dict, user_profile: dict, language: str = "english") -> str:
    """Generate a friendly explanation of an already-decided eligibility verdict.

    scheme_result: {"name": str, "status": "likely_eligible"|"likely_not_eligible"|"check_manually", "reasons": [str, ...]}
    language: "english", "hindi", or "gujarati"
    """
    language_name = language.capitalize() if language.lower() in ("hindi", "gujarati") else "English"

    system_prompt = EXPLAIN_SYSTEM_PROMPT
    if language_name != "English":
        system_prompt += f"\n\nIMPORTANT: Write your entire response in natural, fluent {language_name}, using the correct native script."

    prompt = _build_explain_prompt(scheme_result, user_profile)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=300,
            ),
        )
        explanation = response.text.strip()
    except Exception as e:
        # Fail safe: never invent an explanation if the API call fails - just
        # state the raw verdict plainly instead of guessing.
        explanation = f"({scheme_result['name']}: {scheme_result['status'].replace('_', ' ')} - {'; '.join(scheme_result['reasons']) or 'all criteria met'})"

    if _flag_possible_contradiction(scheme_result["status"], explanation.lower()):
        print(f"  [SAFETY FLAG] Possible contradiction detected for {scheme_result['name']} "
              f"(verdict={scheme_result['status']}) - please review this explanation manually:")
        print(f"  {explanation}")

    return explanation


# --- Phase 4.4 test cases: one explanation per verdict type, in all 3 languages ---

TEST_CASES = [
    {
        "scheme_result": {"name": "PM-KISAN", "status": "likely_eligible", "reasons": []},
        "user_profile": {"age": 35, "annual_family_income": 200000, "state": "Gujarat", "occupation": "Farmer"},
    },
    {
        "scheme_result": {
            "name": "Manav Garima Yojana (Gujarat)",
            "status": "likely_not_eligible",
            "reasons": ["occupation 'Farmer' does not match required 'self-employed/artisan'"],
        },
        "user_profile": {"age": 35, "annual_family_income": 200000, "state": "Gujarat", "occupation": "Farmer"},
    },
    {
        "scheme_result": {
            "name": "National Social Assistance Programme - Old Age Pension (IGNOAPS)",
            "status": "check_manually",
            "reasons": ["Requires BPL/SECC-2011 household verification, not a simple income cutoff a self-reported form can determine."],
        },
        "user_profile": {"age": 65, "annual_family_income": 80000, "state": "Other", "occupation": "Other"},
    },
]


def main():
    print("Testing explain_eligibility() - one case per verdict type, x3 languages...\n")
    for case in TEST_CASES:
        for language in ["english", "hindi", "gujarati"]:
            print("=" * 70)
            print(f"Scheme: {case['scheme_result']['name']}  |  Verdict: {case['scheme_result']['status']}  |  Language: {language}")
            print("-" * 70)
            explanation = explain_eligibility(case["scheme_result"], case["user_profile"], language)
            print(explanation)
            print()


if __name__ == "__main__":
    main()