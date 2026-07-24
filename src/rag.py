"""
rag.py

Phase 2.3: Core RAG prompt engineering.
Phase 2.4: LLM Integration - End-to-End Answer (retrieval + generation wired together).

Defines the system prompt that grounds Gemini's answers strictly in
retrieved scheme context, with an explicit fallback when context is
insufficient. `answer_question()` is the Phase 2.4 entry point: it queries
the ChromaDB 'schemes' collection built in Phase 2.1, formats the retrieved
documents as CONTEXT, calls Gemini, and returns the answer plus the source
scheme(s)/official_link(s) actually used for citation.

Model choice: gemini-3.1-flash-lite is used as the PRIMARY model (not just
a fallback). Flash-Lite variants get a much larger free-tier daily request
quota than the full Flash models, which matters a lot when you're running
repeated test batches during development on a free API key.

Usage:
    python src/rag.py                 # Phase 2.4 end-to-end test (real retrieval)
    python src/rag.py --prompt-only   # Phase 2.3 hardcoded-context test
"""

import os
import re
import sys
import time
from pathlib import Path

import chromadb
from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = REPO_ROOT / "chroma_db"
COLLECTION_NAME = "schemes"
DEFAULT_TOP_K = 5

# Flash-Lite as primary: much higher free-tier daily quota than full Flash models.
GEMINI_MODEL = "gemini-3.1-flash-lite"
MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 5

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about Indian government welfare schemes.

RULES YOU MUST FOLLOW:
1. Answer ONLY using the information provided in the CONTEXT section below. Do not use any outside knowledge about government schemes, even if you believe you know the answer.
2. If the CONTEXT does not contain enough information to answer the QUESTION, say so clearly and directly. Do not guess, do not make up eligibility criteria, benefit amounts, or application steps.
3. When the context is insufficient, tell the user to check the scheme's official_link (included in the context) for authoritative, up-to-date information.
4. When you do answer, always mention which scheme(s) your answer is based on by name, and mention the official_link so the user can verify and apply.
5. Be concise, warm, and clear. Avoid legal or bureaucratic jargon where possible.
6. Never invent a scheme, benefit amount, deadline, or document requirement that is not explicitly present in the CONTEXT.
"""


def build_prompt(context: str, question: str) -> str:
    """Format the CONTEXT and QUESTION into the user message sent to Gemini."""
    return f"""CONTEXT:
{context}

QUESTION:
{question}"""


def _extract_retry_delay(error: errors.ClientError, default: float) -> float:
    """Pull the server-suggested retry delay (in seconds) out of a 429 error, if present."""
    try:
        match = re.search(r"retry in ([\d.]+)s", str(error))
        if match:
            return float(match.group(1)) + 1  # small buffer
    except Exception:
        pass
    return default


def ask_gemini(context: str, question: str, system_prompt: str = None) -> str:
    """Send one grounded question to Gemini and return the answer text.

    system_prompt defaults to the English-only SYSTEM_PROMPT; pass a
    different one (e.g. from build_multilingual_system_prompt) to get
    an answer generated directly in another language.

    - 503 (ServerError, temporary overload): short retry with fixed backoff.
    - 429 (ClientError, quota/rate limit exceeded): retry using the server's
      OWN suggested wait time (parsed from the error message) instead of a
      fixed 5s, since quota resets can take much longer than a transient hiccup.
    - Any other error: fails fast with a clear message, no silent fallback
      to a different, un-audited model.
    """
    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=build_prompt(context, question),
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=1024,
                ),
            )
            return response.text
        except errors.ServerError as e:
            last_error = e
            print(f"  [retry {attempt}/{MAX_RETRIES}] {GEMINI_MODEL} unavailable (503), waiting {DEFAULT_RETRY_DELAY_SECONDS}s...")
            time.sleep(DEFAULT_RETRY_DELAY_SECONDS)
        except errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                delay = _extract_retry_delay(e, default=30)
                last_error = e
                print(f"  [retry {attempt}/{MAX_RETRIES}] quota/rate limit hit (429), waiting {delay:.0f}s...")
                time.sleep(delay)
            else:
                # Not a quota issue (e.g. bad request, invalid key) - fail fast, don't retry blindly.
                raise RuntimeError(f"Gemini API client error (non-retryable): {e}") from e

    raise RuntimeError(
        f"Gemini API still unavailable after {MAX_RETRIES} attempts (likely daily quota exhausted). "
        f"Last error: {last_error}"
    ) from last_error


# --- Phase 2.4: retrieval + end-to-end answer function ---------------------

_collection = None  # lazy singleton, so re-importing rag.py doesn't reopen the DB


def _get_collection():
    global _collection
    if _collection is None:
        client_db = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        _collection = client_db.get_collection(name=COLLECTION_NAME)
    return _collection


def retrieve_context(question: str, top_k: int = DEFAULT_TOP_K):
    """Query the 'schemes' ChromaDB collection for the top_k most relevant schemes.

    Returns a tuple: (context_text, sources) where sources is a list of dicts
    with scheme_id/name/official_link, one per retrieved scheme, in rank order.
    """
    collection = _get_collection()
    results = collection.query(query_texts=[question], n_results=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_blocks = []
    sources = []
    for doc_text, meta in zip(documents, metadatas):
        context_blocks.append(f"{doc_text}\nofficial_link: {meta.get('official_link', '')}")
        sources.append(
            {
                "scheme_id": meta.get("scheme_id", ""),
                "name": meta.get("name", ""),
                "official_link": meta.get("official_link", ""),
            }
        )

    context_text = "\n\n".join(context_blocks)
    return context_text, sources


def answer_question(question: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Phase 2.4 entry point: retrieve -> prompt -> generate -> cite.

    Returns a dict: {"answer": str, "sources": [{"scheme_id", "name", "official_link"}, ...]}
    """
    try:
        context_text, sources = retrieve_context(question, top_k=top_k)
    except Exception as e:
        return {
            "answer": (
                "Sorry, I couldn't search the scheme database right now "
                f"({type(e).__name__}). Please try again in a moment."
            ),
            "sources": [],
        }

    if not context_text.strip():
        return {
            "answer": (
                "I don't have verified information on this in my current database. "
                "Please check myscheme.gov.in for the most up-to-date details."
            ),
            "sources": [],
        }

    try:
        answer_text = ask_gemini(context_text, question)
    except Exception as e:
        return {
            "answer": (
                "Sorry, I'm having trouble reaching the AI service right now "
                f"({type(e).__name__}). Please try again shortly."
            ),
            "sources": sources,
        }

    return {"answer": answer_text, "sources": sources}


# --- Phase 3.4: multilingual entry point (translate-in -> RAG -> answer directly in target language) ---

LANGUAGE_DISPLAY_NAMES = {
    "hindi": "Hindi",
    "hinglish": "Hindi",       # transliterated Hindi -> answer in proper Hindi (Devanagari)
    "gujarati": "Gujarati",
    "gujlish": "Gujarati",     # transliterated Gujarati -> answer in proper Gujarati script
    "english": "English",
    "unknown": "English",
}


def build_multilingual_system_prompt(target_language_name: str) -> str:
    """Extend the base SYSTEM_PROMPT with a target-language instruction,
    while keeping every grounding/refusal rule identical to the English version.
    """
    if target_language_name == "English":
        return SYSTEM_PROMPT

    return SYSTEM_PROMPT + f"""

ADDITIONAL LANGUAGE INSTRUCTION:
Respond entirely in natural, fluent {target_language_name}, using the correct native script
(Devanagari for Hindi, Gujarati script for Gujarati) - even if the user's original question
was typed in English letters (transliterated).
However, you MUST still preserve exactly, unchanged, in their original form:
- All official scheme names (e.g. "PM-KISAN", "Pradhan Mantri Awas Yojana")
- All numbers, amounts, percentages, and dates (e.g. "Rs. 6,000", "60%", "18-40 years")
- All URLs/official_links, character-for-character
Only translate the surrounding explanation, not these specific elements.
"""


def answer_question_multilingual(user_text: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Phase 3.4 entry point: detect language -> translate question to English
    -> retrieve -> generate the answer DIRECTLY in the user's language (single
    LLM call, per the Phase 3.1 decision - no separate translate-out step).

    Returns a dict: {"answer": str, "sources": [...], "detected_language": str,
    "english_question": str}
    """
    from translate import detect_and_translate_to_english, translate_response  # local import avoids a circular import at module load time

    detection = detect_and_translate_to_english(user_text)
    english_question = detection["english_translation"]
    detected_language = detection["detected_language"]
    target_language_name = LANGUAGE_DISPLAY_NAMES.get(detected_language, "English")

    try:
        context_text, sources = retrieve_context(english_question, top_k=top_k)
    except Exception as e:
        return {
            "answer": (
                "Sorry, I couldn't search the scheme database right now "
                f"({type(e).__name__}). Please try again in a moment."
            ),
            "sources": [],
            "detected_language": detected_language,
            "english_question": english_question,
        }

    if not context_text.strip():
        fallback = (
            "I don't have verified information on this in my current database. "
            "Please check myscheme.gov.in for the most up-to-date details."
        )
        if target_language_name != "English":
            fallback = translate_response(fallback, target_language_name.lower())
        return {
            "answer": fallback,
            "sources": [],
            "detected_language": detected_language,
            "english_question": english_question,
        }

    system_prompt = build_multilingual_system_prompt(target_language_name)

    try:
        answer_text = ask_gemini(context_text, english_question, system_prompt=system_prompt)
    except Exception as e:
        return {
            "answer": (
                "Sorry, I'm having trouble reaching the AI service right now "
                f"({type(e).__name__}). Please try again shortly."
            ),
            "sources": sources,
            "detected_language": detected_language,
            "english_question": english_question,
        }

    return {
        "answer": answer_text,
        "sources": sources,
        "detected_language": detected_language,
        "english_question": english_question,
    }


# --- Phase 2.4 test harness: 10 real questions through full retrieval+LLM --

E2E_TEST_QUESTIONS = [
    "How much money does a farmer get per year under PM-KISAN and how is it paid?",
    "What documents do I need for Ayushman Bharat PMJAY?",
    "Is there a subsidy for solar pumps for farmers?",
    "What is the benefit under PM Ujjwala Yojana?",
    "I am a girl child's parent, what savings scheme should I use?",
    "What financial help is available for pregnant women?",
    "Can SC/ST students in Gujarat get a post-matric scholarship?",
    "What is the eligibility for Atal Pension Yojana?",
    "Tell me about a scheme for widows in Gujarat.",
    "What is the eligibility for the Mars colonization scheme?",  # deliberately out-of-scope
]


def run_e2e_tests():
    print(f"Running {len(E2E_TEST_QUESTIONS)} end-to-end (retrieval + LLM) test questions...\n")
    for i, question in enumerate(E2E_TEST_QUESTIONS, start=1):
        print("=" * 70)
        print(f"{i}. Q: {question}")
        print("-" * 70)
        result = answer_question(question)
        print(result["answer"])
        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                print(f"  - {s['name']} ({s['scheme_id']}) -> {s['official_link']}")
        print()
        time.sleep(2)  # small pacing gap between questions to be gentle on free-tier RPM limits


# --- Manual test harness for Phase 2.3 -------------------------------------

SAMPLE_CONTEXT = """Scheme name: PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
Category: Agriculture
State: All India
Description: A central sector scheme providing income support to all landholding farmer families.
Benefits: Rs. 6,000 per year paid in three equal installments of Rs. 2,000 every four months, via DBT.
Eligibility: All landholding farmer families with cultivable land, subject to exclusions. Institutional landholders are not eligible. Income tax payers in the last assessment year are excluded.
Documents required: Aadhaar card, Land ownership/records documents, Bank account passbook, Citizenship certificate.
How to apply: Register online at pmkisan.gov.in via 'Farmers Corner' > 'New Farmer Registration', or through the local Common Service Centre (CSC).
official_link: https://pmkisan.gov.in

Scheme name: Pradhan Mantri Awas Yojana - Urban 2.0 (PMAY-U)
Category: Housing
State: All India
Description: Financial assistance to eligible urban households (EWS, LIG, MIG) to construct, buy, or improve a pucca house.
Benefits: Up to Rs. 2.5 lakh for Beneficiary-Led Construction; interest subsidy on home loans for EWS/LIG/MIG.
Eligibility: Applicant must not own a pucca house anywhere in India. EWS income up to Rs. 3 lakh, LIG Rs. 3-6 lakh, MIG Rs. 6-9 lakh.
Documents required: Aadhaar card, income proof, bank account details, land ownership documents (for BLC).
How to apply: Apply online through pmay-urban.gov.in or through your Urban Local Body during an active application window.
official_link: https://pmay-urban.gov.in"""


TEST_CASES = [
    {
        "label": "1. Answerable - directly in context",
        "question": "How much money does a farmer get per year under PM-KISAN and how is it paid?",
    },
    {
        "label": "2. Partially answerable - context covers the scheme but not this specific detail",
        "question": "What is the current PM-KISAN installment release date for this year?",
    },
    {
        "label": "3. Completely out of scope - not in context at all",
        "question": "What is the eligibility for Ayushman Bharat PMJAY?",
    },
]


def run_prompt_only_tests():
    print("Testing SYSTEM_PROMPT with 3 manual test cases (hardcoded context)...\n")
    for case in TEST_CASES:
        print("=" * 70)
        print(case["label"])
        print(f"Q: {case['question']}")
        print("-" * 70)
        answer = ask_gemini(SAMPLE_CONTEXT, case["question"])
        print(answer)
        print()


def main():
    if "--prompt-only" in sys.argv:
        run_prompt_only_tests()
    else:
        run_e2e_tests()


if __name__ == "__main__":
    main()