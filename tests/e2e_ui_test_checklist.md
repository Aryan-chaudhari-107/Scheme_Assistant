# Phase 5.4 - End-to-End UI Test Checklist

Run these through the actual running app (`streamlit run src\app.py`), not
scripts. Tick off each as you go. If anything fails, note it and we'll fix
it before moving on.

---

## Part A - Chat screen, English (from Module 2)

- [ ] "What is the benefit under PM-KISAN?" -> correct amount (Rs. 6,000/year), cites PM-KISAN with link
- [ ] "What documents do I need for Ayushman Bharat PMJAY?" -> correct document list, cites PMJAY
- [ ] "Is there a subsidy for solar pumps for farmers?" -> mentions PM-KUSUM, 60% subsidy
- [ ] "Compare PM Awas Yojana Urban and PM Awas Yojana Gramin." -> discusses BOTH schemes, doesn't drop one
- [ ] "What is the eligibility for the Mars colonization scheme?" -> clearly refuses, does NOT invent an answer

## Part B - Chat screen, Hindi (from Module 3)

- [ ] "पीएम किसान के तहत कितना पैसा मिलता है?" -> answers in Hindi, correct amount, cites PM-KISAN
- [ ] "सुकन्या समृद्धि योजना की ब्याज दर क्या है?" -> answers in Hindi, correct interest rate

## Part C - Chat screen, Gujarati (from Module 3)

- [ ] "ઉજ્જવલા યોજનાનો લાભ શું છે?" -> answers in Gujarati, correct benefits
- [ ] "વ્હાલી દીકરી યોજના માટે કોણ પાત્ર છે?" -> answers in Gujarati, correct eligibility

## Part D - Chat screen, transliterated + mixed language (from Module 3)

- [ ] "PM Kisan yojana mein kitna paisa milta hai?" (Latin-letter Hindi) -> understood correctly, answered in Hindi
- [ ] "PM-KISAN scheme ke under kitna benefit milta hai per year?" (mixed Hindi/English) -> understood correctly

## Part E - Eligibility Checker, 5+ profiles through the real form (from Module 4)

- [ ] **Profile 1 (Gujarat farmer, 35, income 2L):** PM-KISAN shows as Likely Eligible with a real explanation
- [ ] **Profile 2 (Gujarat mother with young daughter, 26, income 1L):** Sukanya Samriddhi Yojana AND Vahli Dikri Yojana both show as Likely Eligible
- [ ] **Profile 3 (Gujarat widow, 30, income 1L):** Ganga Swaroop Yojana shows as Likely Eligible
- [ ] **Profile 4 (Gujarat SC student, 17, family income 2L):** Gujarat Post-Matric Scholarship AND NSP Post-Matric Scholarship both show as Likely Eligible
- [ ] **Profile 5 (senior citizen, 65, Other state, income 80k):** NSAP Old Age Pension shows under "Check Manually" (not a hard yes/no), with an explanation that mentions needing official verification
- [ ] For at least one profile, expand the "Likely Not Eligible" section and confirm the reasons shown make sense

## Part F - General UI checks

- [ ] Switching language mid-session (sidebar) doesn't crash the app
- [ ] Switching between Home / Chat / Eligibility Checker preserves chat history (doesn't reset when you navigate away and back)
- [ ] No raw Python errors/tracebacks appear anywhere during normal use
- [ ] App remains responsive after 10+ chat messages in one session

---

## Results log

(Fill this in as you go - just need a quick note per section, not full transcripts)

| Section | Result | Notes |
|---------|--------|-------|
| A - English chat | | |
| B - Hindi chat | | |
| C - Gujarati chat | | |
| D - Transliterated/mixed | | |
| E - Eligibility profiles | | |
| F - General UI | | |
