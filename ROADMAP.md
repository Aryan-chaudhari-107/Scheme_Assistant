# Multilingual AI Assistant for Government Schemes
## 15-Day Detailed Execution Roadmap (Zero-to-Demo)

**Stack used in this guide:** Python + FastAPI (backend) + Streamlit (frontend, fast to build) + ChromaDB (vector search) + Claude API (LLM + translation) + pandas (data handling). Swap any tool for an equivalent you're more comfortable with — the *sequence and logic* is what matters.

---

# PHASE 1: FOUNDATION (Days 1-4)
### Goal: Have a clean, accurate, structured scheme database — this is the single most important phase. Everything downstream depends on this being right.

## Day 1: Setup + Scheme Shortlist

**Step 1.1 — Set up your dev environment**
1. Install Python 3.10+ if not already installed
2. Create a project folder: `scheme-assistant/`
3. Create a virtual environment: `python -m venv venv` then activate it
4. Install core packages: `pip install chromadb anthropic pandas streamlit python-dotenv`
5. Get a Claude API key from [console.anthropic.com](https://console.anthropic.com) — set it up in a `.env` file, never hardcode it

**Step 1.2 — Set up version control**
1. Initialize git: `git init`
2. Create a GitHub repo (judges often like seeing commit history — shows real progress over time, not a last-night build)
3. Add a `.gitignore` for `venv/`, `.env`, `__pycache__/`

**Step 1.3 — Pick your 20-25 schemes**
Go through these sources and shortlist schemes. Prioritize ones that are: well-known, high real-world impact, and have clearly documented eligibility rules (avoid vague/discretionary schemes for your MVP).

Sources to browse:
- [myscheme.gov.in](https://www.myscheme.gov.in) — India's official scheme aggregator. Use its category filters (Agriculture, Education, Health, Housing, Women & Child, etc.) to pick a spread across categories
- [india.gov.in/scheme-guidelines](https://www.india.gov.in) — ministry-wise scheme listings
- Gujarat state portal (since local relevance helps): search "Gujarat government schemes portal" — include 3-5 state-specific schemes alongside national ones for that local-relevance angle
- Well-known national schemes to definitely include: PM-KISAN, Ayushman Bharat (PMJAY), PM Awas Yojana, PM Ujjwala Yojana, Sukanya Samriddhi Yojana, National Scholarship Portal schemes, Atal Pension Yojana, PM Fasal Bima Yojana

**Step 1.4 — Create your tracking sheet**
Make a simple spreadsheet (Google Sheets is fine) with columns: Scheme Name | Category | Source URL | Status (Not Started/In Progress/Done). This becomes your Day 2-3 checklist.

**End of Day 1 checkpoint:** Environment works, GitHub repo created, 20-25 schemes shortlisted with source links saved.

---

## Day 2: Data Collection (Part 1)

**Step 2.1 — Design your data schema**
Before collecting data, decide the exact structure every scheme entry will follow. Use this JSON structure (or similar):
```
{
  "scheme_id": "pm-kisan",
  "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
  "category": "Agriculture",
  "ministry": "Ministry of Agriculture and Farmers Welfare",
  "description": "...",
  "benefits": "...",
  "eligibility": ["criterion 1", "criterion 2", "..."],
  "documents_required": ["doc 1", "doc 2"],
  "how_to_apply": "...",
  "official_link": "https://...",
  "state": "All India / Gujarat / etc."
}
```

**Step 2.2 — Collect data for first 8-10 schemes**
For each scheme, visit myscheme.gov.in's dedicated page for that scheme (search the scheme name on the site) and manually extract: description, benefits, eligibility, documents, application process. Cross-check against the scheme's official ministry page when available for accuracy.

**Step 2.3 — Save as you go**
Store each scheme as a JSON file in a `data/schemes/` folder, OR as rows in a single CSV/spreadsheet — whichever you find easier to maintain. Consistency matters more than the exact format.

**End of Day 2 checkpoint:** 8-10 schemes fully documented in your structured format.

---

## Day 3: Data Collection (Part 2)

**Step 3.1 — Collect remaining 10-15 schemes**
Repeat the Day 2 process for the rest of your shortlist. Keep your tracking spreadsheet updated.

**Step 3.2 — Quality pass**
Go back through everything collected so far and check:
- Are eligibility criteria specific and checkable (age, income, occupation, state, category) rather than vague?
- Is every entry's official_link a real, working URL?
- Is language simple (you'll need to translate this later, so avoid overly bureaucratic phrasing where possible)

**End of Day 3 checkpoint:** All 20-25 schemes collected and quality-checked.

---

## Day 4: Data Finalization + Load into Python

**Step 4.1 — Consolidate into one dataset**
Write a small Python script (`load_data.py`) that reads all your scheme JSON/CSV files into a single pandas DataFrame or list of dictionaries. Print it out and eyeball it for errors.

**Step 4.2 — Chunk long fields if needed**
For RAG, very long text fields (like detailed eligibility explanations) work better as their own retrievable "chunk" rather than one giant blob per scheme. For an MVP with only 20-25 schemes, you likely don't need aggressive chunking — one chunk per scheme is usually fine. Keep this simple.

**Step 4.3 — Write a data validation script**
A short script that checks: every scheme has all required fields filled, no empty strings, no broken links (you can even use Python's `requests` library to ping each URL and confirm it returns 200).

**End of Day 4 checkpoint (Phase 1 complete):** A clean, validated `schemes.json` or `schemes.csv` with 20-25 complete, accurate scheme entries. Commit this to GitHub.

---

# PHASE 2: CORE RAG PIPELINE — ENGLISH ONLY (Days 5-8)
### Goal: A working question-answering system in English before adding any language complexity.

## Day 5: Embeddings + Vector Store Setup

**Step 5.1 — Learn the core concept (30 min, worth doing properly)**
Read the [ChromaDB Getting Started guide](https://docs.trychroma.com/getting-started) — it's short and shows the exact pattern you need: add documents, embed them, query by similarity.

**Step 5.2 — Set up ChromaDB**
1. Initialize a persistent Chroma client (so your data survives restarts)
2. Create a collection called `schemes`
3. Write a script `build_index.py` that loops through your `schemes.json` and adds each scheme as a document to the collection, with the scheme_id as metadata (so you can trace answers back to a source)

**Step 5.3 — Test retrieval in isolation**
Before connecting anything else, write a tiny test: query the collection with a plain-English question like "farmer income support scheme" and confirm it returns PM-KISAN as a top result. Test 5-6 different phrasings/questions to make sure retrieval quality is good BEFORE building on top of it.

**End of Day 5 checkpoint:** ChromaDB collection built from your scheme data; retrieval returns sensible results for test queries.

---

## Day 6: Connect the LLM (English RAG, v1)

**Step 6.1 — Write the core RAG prompt**
This is the most important prompt in your whole project. Structure it like this:
```
System: You are a helpful assistant for Indian government schemes.
Answer the user's question using ONLY the information in the CONTEXT below.
If the context does not contain enough information to answer, say clearly
that you don't have verified information on this, and suggest the user
check [official_link]. Never guess or use outside knowledge.

CONTEXT:
{retrieved scheme documents}

QUESTION:
{user question}
```

**Step 6.2 — Wire it together**
Write `rag_pipeline.py`: takes a question → queries ChromaDB for top 2-3 matches → inserts them into the prompt template above → calls the Claude API → returns the answer + which scheme(s) it came from.

Reference: [Anthropic API docs](https://docs.claude.com) for exact request format (messages endpoint).

**Step 6.3 — Test with 15-20 real questions**
Write out a test question list covering: direct questions ("What is PM-KISAN?"), eligibility questions ("Am I eligible if I earn X per year?"), edge cases ("Tell me about [a scheme not in your database]"), and vague questions. Run each one and log the output.

**End of Day 6 checkpoint:** Working English RAG pipeline, tested against 15-20 questions.

---

## Day 7: Refine + Handle Edge Cases

**Step 7.1 — Fix hallucination issues**
Look at your test results from Day 6. Anywhere the model answered confidently about something not in the context, tighten your prompt (be more explicit: "If the scheme is not in the CONTEXT provided, you MUST say you don't have information on it — do not use prior knowledge").

**Step 7.2 — Improve retrieval quality**
If retrieval brought back irrelevant schemes for certain questions, consider: rephrasing your scheme descriptions to include more natural-language synonyms a user might search for, or increasing the number of retrieved chunks from 2 to 3.

**Step 7.3 — Add source citation to output**
Make sure every answer explicitly states which scheme(s) it drew from, plus the official link — this is a key trust/credibility feature for your demo.

**End of Day 7 checkpoint:** Robust English pipeline that handles known-scheme questions well AND gracefully declines unknown-scheme questions.

---

## Day 8: Buffer / Catch-up Day
Use this day to finish anything from Days 5-7 that ran long. If you're ahead of schedule, start early on Day 9's work. (Hackathon builds always run over on at least one phase — having a buffer day built in avoids cascading delays.)

---

# PHASE 3: MULTILINGUAL LAYER (Days 9-10)
### Goal: The same pipeline working in Hindi and Gujarati, not just English.

## Day 9: Add Translation

**Step 9.1 — Decide your translation approach**
Simplest approach (recommended): use the Claude API itself for translation — it's a strong multilingual model. Add a translation step before and after your RAG pipeline rather than building/hosting a separate translation model.

**Step 9.2 — Build the language detection + translate-in step**
Write `translate.py` with two functions:
- `detect_and_translate_to_english(user_text)` — detects language, translates the question to English if needed
- `translate_response(english_text, target_language)` — translates the final answer back

**Step 9.3 — Optional upgrade (if time allows): AI4Bharat IndicTrans2**
If you want to show deeper technical work beyond "just prompting an LLM," look at [AI4Bharat's IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) — an open-source translation model specifically trained for Indian languages. This is a nice-to-have that impresses judges but isn't required; only pursue it if Days 1-8 finished on schedule.

**End of Day 9 checkpoint:** A question typed in Hindi or Gujarati flows through: translate to English → RAG pipeline → translate answer back.

---

## Day 10: Test & Refine Multilingual Pipeline

**Step 10.1 — Test each language thoroughly**
Run your full Day 6 test question list, but now in Hindi and in Gujarati. Check both translation accuracy AND that retrieval still works correctly on translated queries.

**Step 10.2 — Fix language-specific issues**
Common issues to watch for: transliterated text (Hindi typed in English letters — "yojana ke baare mein bataiye"), mixed-language input, translation losing key details (like specific numbers or scheme names). Add handling/testing for at least the transliteration case since it's extremely common in real usage.

**End of Day 10 checkpoint (Phase 3 complete):** Fully working multilingual RAG pipeline in English, Hindi, and Gujarati.

---

# PHASE 4: ELIGIBILITY CHECKER (Days 11-12)
### Goal: A structured feature beyond just Q&A — this differentiates you from "just a chatbot."

## Day 11: Design + Build

**Step 11.1 — Design the eligibility questionnaire**
Decide on a small set of user profile fields that cover most of your schemes' eligibility criteria: age, annual income, occupation/category (farmer/student/senior citizen/etc.), state, gender, category (general/OBC/SC/ST if relevant to schemes you included).

**Step 11.2 — Encode eligibility rules per scheme**
For each of your 20-25 schemes, add a simple structured eligibility rule (e.g., `{"min_age": 60, "max_income": 200000, "occupation": "any"}`) alongside the free-text eligibility description you already have. This lets you do actual rule-based matching rather than relying on the LLM to "guess" eligibility.

**Step 11.3 — Build the matching logic**
Write `eligibility_checker.py`: takes a user profile dict, loops through all schemes, checks their rules, returns a list of "likely eligible," "likely not eligible," and "check manually" (for schemes with criteria too complex to encode simply).

**End of Day 11 checkpoint:** Eligibility rules encoded for all schemes; matching function returns correct results on test profiles.

---

## Day 12: Integrate Eligibility Checker with LLM Layer

**Step 12.1 — Combine rule-based + LLM explanation**
Use the rule-based checker (Step 11.3) to get the yes/no/maybe answer (accurate, no hallucination risk), then use the LLM to generate a friendly natural-language explanation of *why*, in the user's chosen language.

**Step 12.2 — Test edge cases**
Test profiles that are borderline (just above/below an income threshold), profiles that match multiple schemes, and profiles that match none.

**End of Day 12 checkpoint (Phase 4 complete):** Eligibility checker fully working and integrated with the multilingual explanation layer.

---

# PHASE 5: FRONTEND + POLISH (Days 13-14)
### Goal: A clean, demo-ready interface that doesn't distract from the strong backend you built.

## Day 13: Build the Frontend

**Step 13.1 — Set up Streamlit**
Reference: [Streamlit docs — Get Started](https://docs.streamlit.io/get-started). Streamlit lets you build a working UI in pure Python — no separate frontend framework needed, which saves huge time in a hackathon.

**Step 13.2 — Build the core screens**
1. Landing page: brief explainer + language selector (English/Hindi/Gujarati)
2. Chat interface: text input, chat history display, each answer showing its source scheme + official link
3. Eligibility checker: simple form (age, income, occupation, state dropdowns) → results list

**Step 13.3 — Connect frontend to your backend functions**
Wire your Day 6-12 Python functions directly into the Streamlit app (no need for a separate FastAPI layer unless you want one for architectural cleanliness — for a 15-day hackathon, calling functions directly from Streamlit is fine and faster to build).

**End of Day 13 checkpoint:** End-to-end working app: user can chat in 3 languages and use the eligibility checker, all through a UI.

---

## Day 14: Full Integration Testing + Visual Polish

**Step 14.1 — End-to-end test pass**
Go through your entire test question list (Day 6 + Day 10 + Day 12) one final time through the actual UI, not just scripts. Fix anything broken.

**Step 14.2 — Visual polish**
Add a clean color scheme, your project name/logo, loading indicators while the LLM responds, and clear formatting for source citations (e.g., a small "Source: PM-KISAN — Ministry of Agriculture [Official Link]" tag under each answer).

**Step 14.3 — Write your README**
A good GitHub README with a clear problem statement, architecture diagram (even a simple hand-drawn one works), setup instructions, and screenshots. Judges (and any post-hackathon reviewers) often check this.

**End of Day 14 checkpoint:** Fully polished, tested app ready for demo. Everything committed to GitHub.

---

# PHASE 6: DEMO PREP (Day 15)

## Day 15: Rehearsal + Submission

**Step 15.1 — Prepare your fixed demo script**
Don't improvise live queries — pre-select 4-5 questions that reliably showcase: (1) a correct multilingual answer with source citation, (2) the eligibility checker with a clear result, (3) the graceful "I don't have information on this" response for an out-of-database scheme, (4) a quick look at your architecture/code if there's a technical Q&A round.

**Step 15.2 — Prepare a backup**
Record a short screen-capture video of the working demo in case of live wifi/API issues during presentation — a common hackathon failure point. Have it ready to play as backup, don't rely on it as primary.

**Step 15.3 — Rehearse timing**
Run through your demo out loud at least 3 times, timing it to fit your slot (usually 3-5 minutes + Q&A).

**Step 15.4 — Prepare for likely judge questions**
Be ready to explain: "How do you prevent hallucination?" (your RAG grounding + explicit prompt instructions), "How would you scale to more schemes/languages?" (your architecture is designed to extend — new schemes just need new JSON entries, no code changes), "How is this different from just asking ChatGPT?" (grounded in verified official data with citations, plus the rule-based eligibility layer that doesn't rely on LLM guessing for factual eligibility).

**Step 15.5 — Final submission**
Push final code to GitHub, ensure README is complete, submit per hackathon requirements.

---

# Quick Reference: All Resources in One Place

| Purpose | Resource |
|---|---|
| Scheme data source | [myscheme.gov.in](https://www.myscheme.gov.in) |
| Scheme data source | [india.gov.in](https://www.india.gov.in) |
| Vector database | [ChromaDB docs](https://docs.trychroma.com/getting-started) |
| LLM API | [Anthropic Claude API docs](https://docs.claude.com) |
| Frontend | [Streamlit docs](https://docs.streamlit.io/get-started) |
| Indian language translation (stretch) | [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) |
| Voice input (stretch) | OpenAI Whisper (search "openai whisper github") |

---

# The Single Biggest Risk to Watch
Data collection (Days 1-4) is where teams either set themselves up to win or quietly doom the whole project. If you rush it to get to "the fun coding part" faster, you'll spend Days 9-14 debugging bad answers that are actually bad-data problems, not code problems. Protect those first 4 days.
