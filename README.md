# Multilingual AI Assistant for Government Schemes

A RAG-based assistant that answers questions about Indian government schemes in **English, Hindi, and Gujarati**, and includes a rule-based eligibility checker so users get factual, non-hallucinated answers about whether they qualify.

## Problem Statement
Millions of eligible citizens miss out on government schemes because information is scattered, bureaucratic, and rarely available in their language. This assistant makes scheme information conversational, multilingual, and personalized.

## Architecture
```
User (EN/HI/GU)
      │
      ▼
[Language Detect + Translate] ──► English query
      │
      ▼
[ChromaDB Vector Search] ──► top-k relevant schemes
      │
      ▼
[Claude API — RAG answer, grounded in retrieved context only]
      │
      ▼
[Translate back to user's language] ──► Answer + source citation

[Eligibility Checker]: user profile → rule-based match per scheme → Claude explains result in chosen language
```

## Stack
- **Backend logic:** Python
- **Vector search:** ChromaDB
- **LLM + translation:** Claude API
- **Frontend:** Streamlit
- **Data handling:** pandas

## Project Structure
```
scheme-assistant/
├── data/
│   └── schemes/          # one JSON per scheme (see data/schemes/README.md for schema)
├── src/
│   ├── load_data.py      # Day 4 — consolidate scheme JSONs
│   ├── build_index.py    # Day 5 — build ChromaDB collection
│   ├── rag.py             # Day 6-7 — retrieval + Claude RAG answer
│   ├── translate.py      # Day 9 — detect + translate in/out
│   ├── eligibility_checker.py  # Day 11 — rule-based matching
│   └── app.py             # Day 13 — Streamlit UI
├── tests/                 # test scripts / question sets from Day 6, 10, 12
├── notebooks/              # scratch/exploration notebooks
├── .streamlit/             # streamlit config (secrets.toml is gitignored)
├── .env.example
└── requirements.txt
```

## Setup
1. Clone the repo:
   ```
   git clone https://github.com/<org-or-user>/scheme-assistant.git
   cd scheme-assistant
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Claude API key.
5. Run the app:
   ```
   streamlit run src/app.py
   ```

## Team Workflow
See [CONTRIBUTING.md](CONTRIBUTING.md) for branching strategy and how the 3 of us split and merge work.

## Roadmap
See [ROADMAP.md](ROADMAP.md) for the full 15-day plan, and [TASKS.md](TASKS.md) for who's doing what.

## Status
🚧 In progress — Day 1 of 15.
