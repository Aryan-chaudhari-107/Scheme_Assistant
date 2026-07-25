# Judge Q&A Preparation

Practice these out loud until you can say each in under 30 seconds without
looking at notes.

---

## Q1: "How do you prevent hallucination?"

**Answer:**
"Two layers. First, RAG grounding — we never let the model answer from
its own general knowledge. Every answer is generated strictly from
scheme documents retrieved from our ChromaDB vector database, and our
system prompt explicitly instructs the model to say 'I don't have this
information' rather than guess if the retrieved context doesn't cover
the question. We tested this directly — asking about a fake 'Mars
colonization scheme' correctly triggers a refusal instead of an invented
answer. Second, for eligibility specifically — the actual yes/no decision
is made by plain rule-based Python code, not the LLM at all. The AI only
explains a decision that's already been made, and is explicitly forbidden
from contradicting it."

---

## Q2: "How would you scale to more schemes/languages?"

**Answer:**
"Adding schemes doesn't need any code changes — just a new JSON file in
our schema, then re-running two scripts to rebuild the index. We proved
this scaling from 9 to 24 schemes during development without touching
the pipeline code. Adding a new language is also lightweight — our
translation layer uses the LLM itself for detection and translation, so
adding, say, Marathi or Tamil is a prompt change, not new infrastructure
or a new model to host."

---

## Q3: "How is this different from just asking ChatGPT?"

**Answer:**
"Three things. One — every answer is grounded in verified official scheme
data with a citation and a real government link, not the model's general
training knowledge, which can be outdated or simply wrong for
fast-changing scheme details. Two — our eligibility checker uses
deterministic rule-based logic for the actual decision, so it's not
subject to LLM inconsistency on a factual question with real financial
consequences. Three — it's multilingual by design for the actual target
users, including handling how people really type Hindi and Gujarati in
practice, like Romanized/transliterated text, not just proper script."

---

## Bonus: likely follow-up questions (based on our actual build)

**"Why Gemini instead of Claude, if the project was originally planned around Claude?"**
"Cost during development — we didn't have a paid Anthropic subscription,
and Gemini's free tier let us iterate and test extensively without
worrying about hitting limits mid-build. The architecture is
provider-agnostic; swapping models is a config change, not a rewrite."

**"What happens if the API goes down during a real user's session?"**
"We handle that explicitly — every API call is wrapped in error handling
that returns a clear, honest message to the user ('having trouble
reaching the service, please try again') instead of crashing or showing
a raw error. We also have retry logic that reads the actual server-
suggested wait time on rate limits, rather than guessing."

**"How confident are you in the eligibility results?"**
"For most schemes, very — the checker uses exact structured rules we
extracted from official eligibility criteria. But we're honest about the
limits too: 3 of our 24 schemes genuinely require official government
database verification (SECC/BPL status) we can't replicate with a
self-reported form, so those are explicitly flagged 'check manually'
instead of a false confident yes or no."