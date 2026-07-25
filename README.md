# Scheme Assistant — Multilingual AI Assistant for Government Schemes

A RAG-based assistant that answers questions about Indian government
welfare schemes in **English, Hindi, and Gujarati**, plus a rule-based
eligibility checker so users get factual, non-hallucinated answers about
whether they actually qualify — not just a chatbot guessing.

## Problem Statement

Millions of eligible citizens miss out on government schemes because
information is scattered across dozens of official websites, written in
bureaucratic language, and rarely available in their own language.
Scheme Assistant makes scheme information conversational, multilingual,
and grounded strictly in real scheme data — it will tell you clearly when
it doesn't know something, rather than guessing.

## Live Demo

Run locally with `streamlit run src/app.py` (see Setup below). Screenshots
of all 3 screens are in [`/screenshots`](./screenshots).

## Architecture

```
                         ┌─────────────────────────┐
                         │   User types a question  │
                         │   (English / Hindi /      │
                         │    Gujarati, incl.        │
                         │    transliterated input)  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │  translate.py                    │
                    │  detect language + translate      │
                    │  question -> English               │
                    └────────────┬─────────────────────┘
                                 │  English question
                                 ▼
                    ┌─────────────────────────────────┐
                    │  ChromaDB vector search            │
                    │  (build_index.py / rag.py)          │
                    │  -> top-k relevant scheme documents │
                    └────────────┬─────────────────────┘
                                 │  retrieved scheme context
                                 ▼
                    ┌─────────────────────────────────┐
                    │  Gemini (rag.py)                  │
                    │  answers ONLY from retrieved       │
                    │  context, in the user's original    │
                    │  language, in ONE call (no separate │
                    │  translate-out step)                │
                    └────────────┬─────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │  Answer + source scheme + link      │
                    │  shown in Streamlit chat UI          │
                    └─────────────────────────────────┘


         ── Eligibility Checker (separate path) ──

  User fills 11-field form (age, income, state, occupation, etc.)
                    │
                    ▼
  eligibility_checker.py  -->  100% rule-based, deterministic Python.
  (NO LLM involved in the       Loops through all 24 schemes' structured
   actual eligibility decision)  eligibility_rules and classifies each as
                    │            likely_eligible / likely_not_eligible /
                    │            check_manually (schemes needing external
                    │            SECC/BPL verification)
                    ▼
  eligibility_explainer.py  -->  LLM explains the ALREADY-DECIDED verdict
  (LLM here ONLY explains,        in warm, plain language, in the user's
   never decides)                 chosen language. Explicitly forbidden
                                   from contradicting the verdict.
```

**Why this split?** Answering "what is PM-KISAN" is a language-understanding
task, well suited to an LLM. Answering "am I eligible for PM-KISAN" is a
factual yes/no question with real consequences — that decision is made by
plain, testable Python code, and the LLM is only ever used afterward to
explain that decision in friendly language, never to make it.

## Stack

- **Backend logic:** Python
- **Vector search:** ChromaDB (local persistent store, `all-MiniLM-L6-v2` embeddings)
- **LLM + translation:** Google Gemini API (`gemini-3.1-flash-lite`) — switched from
  the original Claude API plan due to free-tier cost constraints during development
- **Frontend:** Streamlit
- **Data handling:** pandas

## Project Structure

```
scheme-assistant/
├── data/
│   ├── schemes/                        # one JSON per scheme + schema README
│   └── schemes.json                    # consolidated dataset (generated)
├── src/
│   ├── load_data.py                    # consolidate scheme JSONs
│   ├── validate_data.py                # schema + link validation
│   ├── build_index.py                  # build ChromaDB collection
│   ├── test_retrieval.py               # retrieval-only quality tests
│   ├── rag.py                          # retrieval + Gemini RAG answer (English + multilingual)
│   ├── translate.py                    # detect + translate in/out
│   └── app.py                          # Streamlit UI (all 3 screens)
├── eligibility_questionnaire_design.md # Phase 4.1 design doc
├── update_eligibility_rules.py         # one-time script: encodes rules into scheme JSONs
├── eligibility_checker.py              # 100% rule-based matching, no LLM
├── eligibility_explainer.py            # LLM explains (never decides) eligibility verdicts
├── translation_strategy.md             # Phase 3.1 architecture decision doc
├── tests/                              # all test scripts + result logs
├── .streamlit/config.toml              # theme
├── .env.example
└── requirements.txt
```

## Setup

1. **Clone and enter the repo**
   ```
   git clone https://github.com/Aryan-chaudhari-107/Scheme_Assistant.git
   cd Scheme_Assistant
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Add your API key**
   Copy `.env.example` to `.env` and add your Gemini API key (free at
   [aistudio.google.com](https://aistudio.google.com)):
   ```
   GEMINI_API_KEY=your-key-here
   ```

5. **Build the vector index** (first run downloads a small embedding model, ~1-2 min)
   ```
   python src/load_data.py
   python src/build_index.py
   ```

6. **Run the app**
   ```
   streamlit run src/app.py
   ```

## Screenshots

_(See `/screenshots` folder — Home, Chat, and Eligibility Checker screens)_

## Data

24 real, verified Indian government schemes across 8 categories
(Agriculture, Health, Housing, Education, Women & Child, Finance/Pension,
Employment/MSME, Labour), including 5 Gujarat state-specific schemes.
Every scheme has a working official source link, validated automatically.

## Roadmap

Version 1 (this repo) covers multilingual chat + RAG + rule-based
eligibility checking. Planned next: a Personalized Scheme Finder with
match scoring, scheme comparison, document checklists, and eventually
OCR document upload and voice support — see project notes for the full
roadmap.