"""
tests/test_english_pipeline.py

Phase 2.5: English Pipeline Testing & Refinement.

Stress-tests the full RAG pipeline (rag.answer_question) with 20 realistic
questions across 3 categories:
  - 8 easy factual questions (single scheme, clear answer expected)
  - 6 comparison-style questions (two related schemes expected in sources)
  - 6 deliberately out-of-scope questions (should trigger a clear refusal,
    not a hallucinated answer)

Auto-checks:
  - Factual/comparison: did the expected scheme_id(s) appear in the
    returned sources?
  - Out-of-scope: does the answer contain refusal language instead of
    inventing scheme details?

Writes a full transcript + pass/fail table to tests/english_pipeline_results.md
for the Module 2 deliverable.

Usage:
    python src/../tests/test_english_pipeline.py
    (or, from repo root:)  python -m tests.test_english_pipeline
"""

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from rag import answer_question  # noqa: E402

RESULTS_FILE = REPO_ROOT / "tests" / "english_pipeline_results.md"

REFUSAL_PHRASES = [
    "not contain", "not have", "not available", "no relevant",
    "not cover", "no information", "not covered", "outside the scope",
    "cannot find", "unable to find", "no mention", "there is no",
    "not able to provide", "i am sorry", "i'm sorry", "not include",
]

# Each entry: (category, question, expected_scheme_ids or None for out-of-scope)
TEST_QUESTIONS = [
    # --- Easy factual (8) ---
    ("factual", "What is the benefit under PM-KISAN?", ["pm-kisan"]),
    ("factual", "How much premium do I pay for PM Suraksha Bima Yojana?", ["pm-suraksha-bima-yojana"]),
    ("factual", "What documents are needed for e-Shram registration?", ["e-shram"]),
    ("factual", "What is the maximum loan amount under PM Mudra Yojana?", ["pm-mudra-yojana"]),
    ("factual", "Who is eligible for PM Vishwakarma Yojana?", ["pm-vishwakarma-yojana"]),
    ("factual", "What is the interest rate for Sukanya Samriddhi Yojana?", ["sukanya-samriddhi-yojana"]),
    ("factual", "How do I apply for Ayushman Bharat PMJAY?", ["ayushman-bharat-pmjay"]),
    ("factual", "What is the monthly pension amount under the NSAP old age pension scheme?", ["nsap-old-age-pension"]),

    # --- Comparison-style (6) ---
    ("comparison", "What is the difference between PM Jeevan Jyoti Bima Yojana and PM Suraksha Bima Yojana?",
     ["pm-jeevan-jyoti-bima-yojana", "pm-suraksha-bima-yojana"]),
    ("comparison", "Compare PM Awas Yojana Urban and PM Awas Yojana Gramin.",
     ["pmay-urban", "pmay-gramin"]),
    ("comparison", "What's the difference between the Pre-Matric and Post-Matric National Scholarship schemes?",
     ["nsp-pre-matric-scholarship", "nsp-post-matric-scholarship"]),
    ("comparison", "Should I apply for Atal Pension Yojana or the NSAP old age pension scheme?",
     ["atal-pension-yojana", "nsap-old-age-pension"]),
    ("comparison", "Compare Manav Garima Yojana and PM Vishwakarma Yojana for a Gujarat artisan.",
     ["manav-garima-yojana", "pm-vishwakarma-yojana"]),
    ("comparison", "What's the difference between Sukanya Samriddhi Yojana and Vahli Dikri Yojana for a Gujarat family?",
     ["sukanya-samriddhi-yojana", "vahli-dikri-yojana"]),

    # --- Deliberately out-of-scope (6) ---
    ("out_of_scope", "What is the eligibility for a US student visa?", None),
    ("out_of_scope", "How do I apply for an Indian passport?", None),
    ("out_of_scope", "Is there a government subsidy for buying an electric car?", None),
    ("out_of_scope", "Tell me about unemployment benefits in the USA.", None),
    ("out_of_scope", "What is the eligibility for NASA astronaut recruitment?", None),
    ("out_of_scope", "Is there a government scheme for pet adoption?", None),
]


def check_result(category: str, expected_ids, result: dict) -> bool:
    """Auto-check pass/fail based on category."""
    source_ids = {s["scheme_id"] for s in result["sources"]}
    answer_lower = result["answer"].lower()

    if category in ("factual", "comparison"):
        return all(eid in source_ids for eid in expected_ids)

    if category == "out_of_scope":
        return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

    return False


def main():
    total = len(TEST_QUESTIONS)
    passed = 0
    rows = []

    print(f"Running {total} Phase 2.5 stress-test questions...\n")

    for category, question, expected_ids in TEST_QUESTIONS:
        result = answer_question(question, top_k=7 if category == "comparison" else 3)
        ok = check_result(category, expected_ids, result)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1

        source_ids = [s["scheme_id"] for s in result["sources"]]
        print(f"[{status}] ({category}) {question}")
        print(f"        sources: {source_ids}")
        print(f"        answer preview: {result['answer'][:150]}...")
        print()

        rows.append(
            {
                "category": category,
                "question": question,
                "expected": expected_ids,
                "sources": source_ids,
                "status": status,
                "answer": result["answer"],
            }
        )

        time.sleep(2)  # be gentle on free-tier rate limits

    pass_rate = (passed / total) * 100
    print("=" * 60)
    print(f"Summary: {passed}/{total} passed ({pass_rate:.1f}%)")
    print("Checkpoint requires >= 90%:", "MET" if pass_rate >= 90 else "NOT MET")
    print("=" * 60)

    write_results_file(rows, passed, total, pass_rate)
    print(f"\nFull results written to: {RESULTS_FILE}")


def write_results_file(rows, passed, total, pass_rate):
    RESULTS_FILE.parent.mkdir(exist_ok=True)

    lines = [
        "# Phase 2.5 - English Pipeline Test Results\n",
        f"**Summary: {passed}/{total} passed ({pass_rate:.1f}%)** "
        f"- Checkpoint (>=90%): {'MET' if pass_rate >= 90 else 'NOT MET'}\n",
        "| # | Category | Question | Status | Sources returned |",
        "|---|----------|----------|--------|-------------------|",
    ]
    for i, row in enumerate(rows, start=1):
        lines.append(
            f"| {i} | {row['category']} | {row['question']} | {row['status']} | {', '.join(row['sources']) or '(none)'} |"
        )

    lines.append("\n## Full answers\n")
    for i, row in enumerate(rows, start=1):
        lines.append(f"### {i}. [{row['status']}] ({row['category']}) {row['question']}\n")
        lines.append(f"{row['answer']}\n")

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()