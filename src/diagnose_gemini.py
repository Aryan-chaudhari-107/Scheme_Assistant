"""
diagnose_gemini.py

Standalone diagnostic: makes ONE simple call to Gemini and prints the
FULL error (type, message, status code) instead of a generic caught
message. Run this to see exactly why rag.py is failing with ClientError.

Usage:
    python src/diagnose_gemini.py
"""

import os
import traceback

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
print(f"GEMINI_API_KEY found: {'yes, starts with ' + api_key[:6] + '...' if api_key else 'NO - not set!'}")
print()

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Say hello in one sentence.",
        config=types.GenerateContentConfig(max_output_tokens=50),
    )
    print("SUCCESS!")
    print(response.text)
except Exception as e:
    print(f"FAILED with {type(e).__name__}")
    print(f"Error details: {e}")
    print()
    print("Full traceback:")
    traceback.print_exc()