"""
tests/test_multilingual_pipeline.py

Phase 3.4: Multilingual Testing & Edge Cases.

Runs the FULL pipeline (translate-in -> RAG retrieval -> answer generated
directly in target language) end-to-end, covering:
  - 3 questions in Hindi script (Devanagari)
  - 3 questions in Gujarati script
  - 2 questions in transliterated Hindi (Latin letters)
  - 2 questions in transliterated Gujarati (Latin letters)
  - 2 mixed-language (code-switched Hindi/English) questions
  - 2 deliberately out-of-scope questions (one in Hindi, one in Gujarati)

Auto-checks retrieval correctness (expected scheme_id present in sources)
for the 12 in-scope questions - this works regardless of answer language,
since scheme_id/sources are always in English. The 2 out-of-scope
questions are flagged for manual review (auto-detecting a "refusal" in
Hindi/Gujarati text reliably needs a human read, not a keyword match).

Writes a full transcript to tests/multilingual_test_results.md.

Usage:
    python tests/test_multilingual_pipeline.py
"""

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from rag import answer_question_multilingual  # noqa: E402

RESULTS_FILE = REPO_ROOT / "tests" / "multilingual_test_results.md"

# Each entry: (category, question_text, expected_scheme_id or None for out-of-scope/manual-review)
TEST_QUESTIONS = [
    # --- Hindi script (Devanagari) ---
    ("hindi_script", "पीएम किसान के तहत कितना पैसा मिलता है?", "pm-kisan"),
    ("hindi_script", "आयुष्मान भारत के लिए कौन से दस्तावेज़ चाहिए?", "ayushman-bharat-pmjay"),
    ("hindi_script", "सुकन्या समृद्धि योजना की ब्याज दर क्या है?", "sukanya-samriddhi-yojana"),

    # --- Gujarati script ---
    ("gujarati_script", "પીએમ કિસાન યોજનામાં કેટલા પૈસા મળે છે?", "pm-kisan"),
    ("gujarati_script", "ઉજ્જવલા યોજનાનો લાભ શું છે?", "pm-ujjwala-yojana"),
    ("gujarati_script", "વ્હાલી દીકરી યોજના માટે કોણ પાત્ર છે?", "vahli-dikri-yojana"),

    # --- Transliterated Hindi (Latin letters) ---
    ("transliterated_hindi", "PM Kisan yojana mein kitna paisa milta hai?", "pm-kisan"),
    ("transliterated_hindi", "Ayushman Bharat ke liye kaunse documents chahiye?", "ayushman-bharat-pmjay"),

    # --- Transliterated Gujarati (Latin letters) ---
    ("transliterated_gujarati", "PM Kisan yojanama ketla paisa made chhe?", "pm-kisan"),
    ("transliterated_gujarati", "Ujjwala yojanano labh shu chhe?", "pm-ujjwala-yojana"),

    # --- Mixed-language / code-switched (Hindi+English in one sentence) ---
    ("mixed_language", "PM-KISAN scheme ke under kitna benefit milta hai per year?", "pm-kisan"),
    ("mixed_language", "Mujhe Sukanya Samriddhi Yojana ka interest rate batao please", "sukanya-samriddhi-yojana"),

    # --- Deliberately out-of-scope (manual review - expected None) ---
    ("out_of_scope_hindi", "मंगल ग्रह पर बसने की योजना क्या है?", None),
    ("out_of_scope_gujarati", "અમેરિકામાં નોકરી વિઝા માટે પાત્રતા શું છે?", None),
]


def main():
    total = len(TEST_QUESTIONS)
    auto_checked = 0
    auto_passed = 0
    rows = []

    print(f"Running {total} Phase 3.4 multilingual end-to-end test questions...\n")

    for category, question, expected_id in TEST_QUESTIONS:
        result = answer_question_multilingual(question)
        source_ids = [s["scheme_id"] for s in result["sources"]]

        if expected_id is not None:
            auto_checked += 1
            ok = expected_id in source_ids
            status = "PASS" if ok else "FAIL"
            if ok:
                auto_passed += 1
        else:
            status = "REVIEW"  # out-of-scope: needs a human read of the non-English refusal text

        print(f"[{status}] ({category}) {question}")
        print(f"        detected_language: {result['detected_language']}  |  english_question: {result['english_question']}")
        print(f"        sources: {source_ids}")
        print(f"        answer: {result['answer'][:200]}...")
        print()

        rows.append(
            {
                "category": category,
                "question": question,
                "detected_language": result["detected_language"],
                "english_question": result["english_question"],
                "expected_id": expected_id,
                "sources": source_ids,
                "status": status,
                "answer": result["answer"],
            }
        )

        time.sleep(2)  # be gentle on free-tier rate limits

    pass_rate = (auto_passed / auto_checked * 100) if auto_checked else 0
    print("=" * 60)
    print(f"Auto-checked (in-scope) questions: {auto_passed}/{auto_checked} passed ({pass_rate:.1f}%)")
    print(f"Out-of-scope questions flagged for manual review: {total - auto_checked}")
    print("Checkpoint requires auto-checked >= 90%:", "MET" if pass_rate >= 90 else "NOT MET")
    print("=" * 60)

    write_results_file(rows, auto_passed, auto_checked, pass_rate)
    print(f"\nFull results written to: {RESULTS_FILE}")
    print("\n>>> Please read the 2 [REVIEW] out-of-scope answers above and confirm they refuse")
    print(">>> clearly in Hindi/Gujarati rather than inventing scheme details, then report back.")


def write_results_file(rows, auto_passed, auto_checked, pass_rate):
    RESULTS_FILE.parent.mkdir(exist_ok=True)

    lines = [
        "# Phase 3.4 - Multilingual Pipeline Test Results\n",
        f"**Auto-checked (in-scope) questions: {auto_passed}/{auto_checked} passed ({pass_rate:.1f}%)** "
        f"- Checkpoint (>=90%): {'MET' if pass_rate >= 90 else 'NOT MET'}\n",
        "Out-of-scope questions are marked REVIEW and require a manual read "
        "(refusal-language detection in Hindi/Gujarati isn't reliably automatable "
        "with a simple keyword match).\n",
        "| # | Category | Question | Detected Lang | English Translation | Status | Sources |",
        "|---|----------|----------|----------------|----------------------|--------|---------|",
    ]
    for i, row in enumerate(rows, start=1):
        lines.append(
            f"| {i} | {row['category']} | {row['question']} | {row['detected_language']} | "
            f"{row['english_question']} | {row['status']} | {', '.join(row['sources']) or '(none)'} |"
        )

    lines.append("\n## Full answers\n")
    for i, row in enumerate(rows, start=1):
        lines.append(f"### {i}. [{row['status']}] ({row['category']}) {row['question']}\n")
        lines.append(f"**Detected language:** {row['detected_language']}\n")
        lines.append(f"**English translation:** {row['english_question']}\n")
        lines.append(f"**Answer:**\n\n{row['answer']}\n")

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()