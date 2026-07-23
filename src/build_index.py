"""
build_index.py

Builds a persistent ChromaDB vector store from the consolidated
data/schemes.json dataset. Creates (or resets) a collection called
'schemes', embedding a combined text blob per scheme so semantic search
can later retrieve the most relevant scheme(s) for a user's question.

Usage:
    python src/build_index.py
"""

import json
from pathlib import Path

import chromadb

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMES_JSON = REPO_ROOT / "data" / "schemes.json"
CHROMA_DB_DIR = REPO_ROOT / "chroma_db"  # persistent on-disk storage
COLLECTION_NAME = "schemes"


def build_document_text(scheme: dict) -> str:
    """Combine the fields that matter for semantic search into one text blob."""
    eligibility = scheme.get("eligibility", [])
    if isinstance(eligibility, list):
        eligibility = " ".join(eligibility)

    documents_required = scheme.get("documents_required", [])
    if isinstance(documents_required, list):
        documents_required = ", ".join(documents_required)

    parts = [
        f"Scheme name: {scheme.get('name', '')}",
        f"Category: {scheme.get('category', '')}",
        f"State: {scheme.get('state', '')}",
        f"Description: {scheme.get('description', '')}",
        f"Benefits: {scheme.get('benefits', '')}",
        f"Eligibility: {eligibility}",
        f"Documents required: {documents_required}",
        f"How to apply: {scheme.get('how_to_apply', '')}",
    ]
    return "\n".join(parts)


def main():
    if not SCHEMES_JSON.exists():
        raise FileNotFoundError(
            f"{SCHEMES_JSON} not found. Run `python src/load_data.py` first "
            "to generate the consolidated dataset."
        )

    with open(SCHEMES_JSON, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    print(f"Loaded {len(schemes)} schemes from {SCHEMES_JSON}")

    # Persistent client so the index survives restarts (writes to chroma_db/ on disk)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    # Reset the collection each run so re-running this script is always safe
    # and never leaves stale/duplicate entries behind.
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing '{COLLECTION_NAME}' collection (rebuilding fresh)")

    collection = client.create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []

    for scheme in schemes:
        scheme_id = scheme["scheme_id"]
        ids.append(scheme_id)
        documents.append(build_document_text(scheme))
        metadatas.append(
            {
                "scheme_id": scheme_id,
                "name": scheme.get("name", ""),
                "category": scheme.get("category", ""),
                "state": scheme.get("state", ""),
                "official_link": scheme.get("official_link", ""),
            }
        )

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    count = collection.count()
    print(f"Collection '{COLLECTION_NAME}' now contains {count} documents")

    if count == len(schemes):
        print(f"SUCCESS: document count matches scheme count ({count})")
    else:
        print(f"WARNING: expected {len(schemes)} documents but found {count}")


if __name__ == "__main__":
    main()