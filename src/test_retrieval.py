"""
test_retrieval.py

Tests ChromaDB retrieval quality BEFORE any LLM is layered on top.
Runs a documented list of plain-English test questions (2 per scheme,
covering different phrasings) against the 'schemes' collection, and
checks whether the expected scheme comes back in the top-3 results.

Checkpoint: at least 90% of test queries must return the correct scheme
in the top-3 results.

Usage:
    python src/test_retrieval.py
"""

from pathlib import Path

import chromadb

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = REPO_ROOT / "chroma_db"
COLLECTION_NAME = "schemes"
TOP_K = 3

# Each tuple: (plain-English question, expected scheme_id)
# Two differently-phrased questions per scheme, covering all 24 schemes.
TEST_QUERIES = [
    ("farmer income support scheme", "pm-kisan"),
    ("money for farmers every year", "pm-kisan"),
    ("crop insurance for farmers", "pm-fasal-bima-yojana"),
    ("compensation for crop damage due to flood", "pm-fasal-bima-yojana"),
    ("solar pump subsidy for farmers", "pm-kusum"),
    ("farmer solar power scheme", "pm-kusum"),
    ("free health insurance for poor families", "ayushman-bharat-pmjay"),
    ("hospital treatment cover scheme", "ayushman-bharat-pmjay"),
    ("government scheme to build house in city", "pmay-urban"),
    ("affordable housing for urban poor", "pmay-urban"),
    ("house building scheme for villages", "pmay-gramin"),
    ("rural housing scheme", "pmay-gramin"),
    ("free gas connection for poor women", "pm-ujjwala-yojana"),
    ("LPG cylinder subsidy scheme", "pm-ujjwala-yojana"),
    ("savings scheme for girl child", "sukanya-samriddhi-yojana"),
    ("investment for daughter's education", "sukanya-samriddhi-yojana"),
    ("cash assistance for pregnant women", "pm-matru-vandana-yojana"),
    ("maternity benefit scheme", "pm-matru-vandana-yojana"),
    ("scholarship for school students SC ST", "nsp-pre-matric-scholarship"),
    ("financial help for young students class 5", "nsp-pre-matric-scholarship"),
    ("scholarship for college students SC", "nsp-post-matric-scholarship"),
    ("financial help higher education backward class", "nsp-post-matric-scholarship"),
    ("pension scheme for unorganised sector workers", "atal-pension-yojana"),
    ("monthly pension after retirement age 60", "atal-pension-yojana"),
    ("zero balance bank account scheme", "pm-jan-dhan-yojana"),
    ("opening bank account for poor people", "pm-jan-dhan-yojana"),
    ("life insurance scheme cheap premium", "pm-jeevan-jyoti-bima-yojana"),
    ("death insurance for bank account holders", "pm-jeevan-jyoti-bima-yojana"),
    ("accident insurance scheme low cost", "pm-suraksha-bima-yojana"),
    ("insurance for accidental death 20 rupees premium", "pm-suraksha-bima-yojana"),
    ("toolkit scheme for artisans and craftsmen", "pm-vishwakarma-yojana"),
    ("support for traditional carpenters blacksmiths", "pm-vishwakarma-yojana"),
    ("loan for small business without collateral", "pm-mudra-yojana"),
    ("business loan scheme for entrepreneurs", "pm-mudra-yojana"),
    ("pension for elderly poor people", "nsap-old-age-pension"),
    ("old age pension scheme BPL", "nsap-old-age-pension"),
    ("registration for unorganised sector workers", "e-shram"),
    ("ID card for daily wage workers", "e-shram"),
    ("toolkit for SC self employment Gujarat", "manav-garima-yojana"),
    ("free equipment scheme scheduled caste Gujarat", "manav-garima-yojana"),
    ("affordable housing scheme Gujarat", "mukhyamantri-gruh-yojana"),
    ("cheap house scheme Gujarat EWS", "mukhyamantri-gruh-yojana"),
    ("financial help for girl child Gujarat", "vahli-dikri-yojana"),
    ("Gujarat scheme for daughters education", "vahli-dikri-yojana"),
    ("widow pension scheme Gujarat", "ganga-swaroop-yojana"),
    ("monthly financial help for widows Gujarat", "ganga-swaroop-yojana"),
    ("Gujarat scholarship for college students SC OBC", "gujarat-post-matric-scholarship"),
    ("financial aid Gujarat student after class 12", "gujarat-post-matric-scholarship"),
]


def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    total = len(TEST_QUERIES)
    passed = 0
    failures = []

    print(f"Running {total} retrieval test queries (top-{TOP_K})...\n")

    for query, expected_id in TEST_QUERIES:
        results = collection.query(query_texts=[query], n_results=TOP_K)
        top_ids = results["ids"][0]
        distances = results["distances"][0]

        hit = expected_id in top_ids
        status = "PASS" if hit else "FAIL"

        if hit:
            passed += 1
        else:
            failures.append((query, expected_id, top_ids))

        ranked = ", ".join(f"{sid} ({dist:.3f})" for sid, dist in zip(top_ids, distances))
        print(f"[{status}] '{query}'")
        print(f"        expected: {expected_id}")
        print(f"        got top-{TOP_K}: {ranked}")

    pass_rate = (passed / total) * 100

    print()
    print("=" * 60)
    print(f"Summary: {passed}/{total} passed ({pass_rate:.1f}%)")
    print("Checkpoint requires >= 90%:", "MET" if pass_rate >= 90 else "NOT MET")
    print("=" * 60)

    if failures:
        print("\nQueries that need attention (revisit scheme description/eligibility text):")
        for query, expected_id, top_ids in failures:
            print(f"  - '{query}' -> expected '{expected_id}', got {top_ids}")


if __name__ == "__main__":
    main()