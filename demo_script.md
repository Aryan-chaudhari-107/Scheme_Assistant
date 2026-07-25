# Demo Script - Scheme Assistant (Target: 4 minutes)

**Setup before judges arrive:** app already running (`streamlit run src\app.py`),
browser on the Home screen, language set to English, chat history cleared,
internet connection confirmed working.

---

## [0:00-0:20] Opening (Home screen)

**Say:**
"Hi, we built Scheme Assistant — a multilingual AI assistant that helps
Indian citizens find and understand government welfare schemes, in
English, Hindi, and Gujarati. Millions of people miss out on schemes they
actually qualify for because the information is scattered and not in
their language. We're solving that."

*(Point to the Home screen while saying this - no clicking yet)*

---

## [0:20-1:20] Capability 1: Multilingual answer with source citation

**Say:** "Let's ask a question in Hindi."

*(Click Chat, type or paste:)*
```
पीएम किसान के तहत कितना पैसा मिलता है?
```

**While it loads, say:**
"Under the hood, this is doing three things: detecting the language,
translating the question to English to search our database, then
answering directly in Hindi — all grounded in real scheme data, not
guessed."

**When the answer appears, say:**
"Notice it answers in Hindi, gives the exact amount — Rs. 6,000 per year
— and cites the source scheme with a link to the official government
website, so the user can verify it themselves."

---

## [1:20-2:30] Capability 2: Eligibility Checker with a clear result

**Say:** "Now let's check if someone actually qualifies for anything."

*(Click Eligibility Checker, fill in quickly:)*
- Age: 35, Income: 200000, State: Gujarat, Occupation: Farmer, rest defaults
- Click "Check My Eligibility"

**While it loads, say:**
"This part is deliberately NOT AI-decided. A person's eligibility for
real money is a factual yes/no question, so we use plain rule-based code
to make that decision — the AI only explains the result afterward, in
plain language. It never gets to override the decision."

**When results appear, say:**
"PM-KISAN shows as likely eligible, with a plain-language explanation.
Notice we also have a 'Check Manually' category — for schemes like
Ayushman Bharat that depend on official government database verification
we can't fully replicate ourselves, we're honest about that instead of
guessing."

---

## [2:30-3:10] Capability 3: Graceful fallback (out-of-database question)

**Say:** "One more important thing — what happens when we ask something
it doesn't know?"

*(Click Chat, type:)*
```
What is the eligibility for the Mars colonization scheme?
```

**When the answer appears, say:**
"It clearly says this isn't in its data, instead of making something up.
This matters a lot for a tool giving people information about their
rights and benefits — a wrong confident answer is worse than no answer."

---

## [3:10-3:50] Architecture overview (30 seconds)

**Say, while showing the README architecture diagram or just talking:**
"Quickly on how it works: user question comes in, we detect and translate
the language, search a ChromaDB vector database of 24 real government
schemes for the most relevant ones, then Gemini generates an answer
strictly from that retrieved data — never from its own general knowledge.
The eligibility checker is a separate, fully deterministic path — pure
Python rules, no AI in the decision itself, only in the explanation
afterward."

---

## [3:50-4:00] Close

**Say:**
"24 real schemes today, fully tested in 3 languages, with a working
eligibility checker. Thank you — happy to answer questions."

---

## Timing checklist
- [ ] Total run-through takes 4 minutes or less when rehearsed
- [ ] All 4 capabilities covered: multilingual + citation, eligibility checker, graceful fallback, architecture
- [ ] No live typing of unscripted questions during actual judging