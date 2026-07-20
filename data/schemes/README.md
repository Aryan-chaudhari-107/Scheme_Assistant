# Scheme Data Format

One JSON file per scheme, named `<scheme_id>.json` (e.g. `pm-kisan.json`). Everyone collecting data should follow this exact structure so `load_data.py` works without special-casing.

```json
{
  "scheme_id": "pm-kisan",
  "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
  "category": "Agriculture",
  "ministry": "Ministry of Agriculture and Farmers Welfare",
  "description": "...",
  "benefits": "...",
  "eligibility": ["criterion 1", "criterion 2"],
  "eligibility_rules": {
    "min_age": null,
    "max_age": null,
    "max_income": null,
    "occupation": "any",
    "state": "All India"
  },
  "documents_required": ["doc 1", "doc 2"],
  "how_to_apply": "...",
  "official_link": "https://...",
  "state": "All India"
}
```

Notes:
- `eligibility` is free-text (used for the RAG answer / LLM explanation).
- `eligibility_rules` is structured (used by `eligibility_checker.py` for exact matching — added Day 11, but worth sketching while you have the scheme's details fresh on Days 2-3).
- Keep `official_link` a real, working URL — Day 4 has a script that pings these to confirm.
