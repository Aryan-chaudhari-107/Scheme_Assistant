"""
translate.py

Phase 3.2: Translate-In - language detection + translation to English.

detect_and_translate_to_english(user_text) uses the same Gemini model as
rag.py to detect what language a question is written in (English, Hindi,
Gujarati, or transliterated/Romanized Hindi or Gujarati - e.g. typing
Hindi using English letters, extremely common in real usage on Indian
keyboards) and returns an accurate English translation ready to feed into
the Module 2 RAG pipeline unchanged.

Usage:
    python src/translate.py   # runs the built-in test cases
"""

import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TRANSLATE_MODEL = "gemini-3.1-flash-lite"

DETECT_TRANSLATE_SYSTEM_PROMPT = """You are a language detection and translation tool for an Indian government schemes assistant.

Given a user's question, do TWO things:
1. Detect the language: one of "english", "hindi", "gujarati", "hinglish" (Hindi written in Latin/English letters), or "gujlish" (Gujarati written in Latin/English letters).
2. Translate the question into clear, natural English, preserving the exact meaning and intent. If it is already in English, return it unchanged (only fix obvious typos if needed).

Respond ONLY with a JSON object in this exact format, no other text:
{"detected_language": "<one of: english, hindi, gujarati, hinglish, gujlish>", "english_translation": "<the English question>"}
"""


def detect_and_translate_to_english(user_text: str) -> dict:
    """Detect the language of user_text and translate it to English.

    Returns a dict: {"detected_language": str, "english_translation": str}

    Falls back to treating input as English (returned unchanged) if the
    API call fails, so the RAG pipeline can still attempt an answer rather
    than crashing entirely on a translation hiccup.
    """
    try:
        response = client.models.generate_content(
            model=TRANSLATE_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=DETECT_TRANSLATE_SYSTEM_PROMPT,
                max_output_tokens=300,
                response_mime_type="application/json",
            ),
        )
        result = json.loads(response.text)
        return {
            "detected_language": result.get("detected_language", "english"),
            "english_translation": result.get("english_translation", user_text),
        }
    except Exception as e:
        print(f"  [translate warning] detection/translation failed ({type(e).__name__}), falling back to original text as-is")
        return {"detected_language": "unknown", "english_translation": user_text}


TRANSLATE_RESPONSE_SYSTEM_PROMPT = """You are a precise translator for an Indian government schemes assistant.

Translate the given English answer into the target language, following these STRICT rules:
1. Preserve ALL numbers, amounts, percentages, and dates EXACTLY as written (e.g. "Rs. 6,000", "60%", "18-40 years") - never round, reword, or drop them.
2. Preserve official scheme names EXACTLY as given, in their original form (e.g. "PM-KISAN", "Pradhan Mantri Awas Yojana"). You may add the translated meaning in parentheses if natural, but never replace or alter the original name.
3. Preserve every URL/official_link character-for-character, unchanged, never translated or reformatted.
4. Translate everything else (explanations, eligibility descriptions, instructions) into natural, fluent target-language text.
5. Do not add or remove any factual content - only translate.

Respond with ONLY the translated text, no preamble, no explanation.
"""


def translate_response(english_text: str, target_language: str) -> str:
    """Translate an English answer into target_language ('hindi' or 'gujarati'),
    strictly preserving numbers, scheme names, and URLs unchanged.

    If target_language is 'english' (or unrecognized), returns the text unchanged.
    Falls back to the original English text if the API call fails.
    """
    if target_language.lower() not in ("hindi", "gujarati"):
        return english_text

    try:
        response = client.models.generate_content(
            model=TRANSLATE_MODEL,
            contents=f"Target language: {target_language}\n\nEnglish text to translate:\n{english_text}",
            config=types.GenerateContentConfig(
                system_instruction=TRANSLATE_RESPONSE_SYSTEM_PROMPT,
                max_output_tokens=1024,
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"  [translate warning] response translation failed ({type(e).__name__}), returning English text as fallback")
        return english_text


# --- Phase 3.3 test case: English answer with income threshold + scheme name + link ---

SAMPLE_ENGLISH_ANSWER = """Under the PM Awas Yojana - Urban (PMAY-U) scheme, the Economically Weaker Section (EWS) category covers households with an annual income up to Rs. 3,00,000. Beneficiaries can receive financial assistance of up to Rs. 2,50,000 for constructing a new house on their own land under the Beneficiary-Led Construction component.

For more details and to apply, visit the official website: https://pmay-urban.gov.in"""


def run_translate_response_tests():
    print("Testing translate_response() on all 3 target languages...\n")
    print("Original English answer:")
    print(SAMPLE_ENGLISH_ANSWER)
    print()

    for lang in ["english", "hindi", "gujarati"]:
        print("=" * 70)
        print(f"Target language: {lang}")
        print("-" * 70)
        translated = translate_response(SAMPLE_ENGLISH_ANSWER, lang)
        print(translated)
        print()

TEST_CASES = [
    ("English", "What is the benefit under PM-KISAN?"),
    ("Hindi (Devanagari script)", "पीएम किसान योजना का लाभ क्या है?"),
    ("Gujarati (Gujarati script)", "પીએમ કિસાન યોજનાનો લાભ શું છે?"),
    ("Transliterated Hindi (Latin letters)", "PM Kisan yojana ke baare mein bataiye"),
]


def main():
    print("Testing detect_and_translate_to_english() on 4 input types...\n")
    for label, text in TEST_CASES:
        print("=" * 70)
        print(f"{label}")
        print(f"Input: {text}")
        result = detect_and_translate_to_english(text)
        print(f"Detected language: {result['detected_language']}")
        print(f"English translation: {result['english_translation']}")
        print()

    print()
    run_translate_response_tests()


if __name__ == "__main__":
    main()