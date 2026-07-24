# Translation Strategy (Phase 3.1)

## Decision

We will use the same LLM already powering the RAG pipeline (Gemini
Flash-Lite) for all translation work, rather than hosting a separate
dedicated translation model. No new infrastructure, no new API key, no
extra hosting cost - just different prompts to the model we already call.

## Approach

**Translate-in (question -> English):** When a user asks a question in
Hindi or Gujarati, we first detect the language, then translate the
question into English *before* it is sent to ChromaDB for retrieval.
This is necessary because our scheme documents and their embeddings
(built in Phase 2.1) are entirely in English - ChromaDB's semantic
search only works well when the query language matches the indexed
language.

**Answer generation (single-step, not translate-out):** Rather than
generating the answer in English and then running a *second* translation
call to convert it to the user's language (the "translate-out" step the
original plan describes), we generate the answer directly in the user's
detected language in the same LLM call that produces the answer. We give
the model the retrieved English scheme context plus an instruction to
respond in Hindi/Gujarati/English as appropriate. Modern LLMs like Gemini
are strong multilingual generators, so this produces natural, fluent
output without a redundant round-trip translation step.

This collapses what could have been 3 LLM calls per non-English question
(detect -> translate question -> generate answer -> translate answer)
down to 2 (detect+translate question -> generate answer directly in
target language), which matters concretely for us since we're on
Gemini's free tier with daily request quotas per model (see Phase 2.4).

## Why not a dedicated translation model (e.g. AI4Bharat IndicTrans2)?

IndicTrans2 is a strong open-source option purpose-built for Indian
languages and would likely produce more literal, technically precise
translations. But it requires separately hosting and serving a model,
adds a new dependency and deployment surface, and is not needed to hit
our MVP quality bar. We're noting it here as an optional stretch upgrade
if the rest of the build finishes ahead of schedule - not part of the
current plan.

## Languages supported for MVP

- English (no translation needed)
- Hindi (hi)
- Gujarati (gu)