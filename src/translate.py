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


# --- Test cases covering all 4 required input types ------------------------

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


if __name__ == "__main__":
    main()