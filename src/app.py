"""
app.py

Phase 5.1: Streamlit Setup - basic app shell.
Phase 5.2: Core Screens Build - all 3 screens with mock/placeholder data.

Real backend wiring (rag.py, eligibility_checker.py, translate.py) happens
in Phase 5.3 - everything here uses hardcoded placeholder data so the UI
can be reviewed and navigated independently first.

Run with:
    streamlit run src/app.py
"""

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))  # for eligibility_checker.py, eligibility_explainer.py (repo root)
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for rag.py, translate.py (src/)

from rag import answer_question_multilingual  # noqa: E402
from eligibility_checker import check_eligibility  # noqa: E402
from eligibility_explainer import explain_eligibility  # noqa: E402

st.set_page_config(
    page_title="Scheme Assistant",
    page_icon="🇮🇳",
    layout="centered",
)

# --- Session state defaults -------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = "English"
if "view" not in st.session_state:
    st.session_state.view = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "eligibility_results" not in st.session_state:
    st.session_state.eligibility_results = None

# --- Sidebar: language selector + navigation --------------------------------
with st.sidebar:
    st.title("🇮🇳 Scheme Assistant")
    st.caption("Find and check eligibility for Indian government welfare schemes")

    st.session_state.language = st.selectbox(
        "Language / भाषा / ભાષા",
        options=["English", "Hindi", "Gujarati"],
        index=["English", "Hindi", "Gujarati"].index(st.session_state.language),
    )

    st.divider()

    st.session_state.view = st.radio(
        "Navigate",
        options=["Home", "Chat", "Eligibility Checker"],
        index=["Home", "Chat", "Eligibility Checker"].index(st.session_state.view),
    )

st.title("Scheme Assistant")


# =============================================================================
# SCREEN 1: Home / Landing page
# =============================================================================
if st.session_state.view == "Home":
    st.header("👋 Welcome")
    st.markdown(
        """
Scheme Assistant helps you find and understand **Indian government welfare
schemes** — in **English, Hindi, or Gujarati**.

**What you can do here:**
- 💬 **Chat** — ask any question about a scheme (eligibility, benefits, how to apply) in your own words
- ✅ **Eligibility Checker** — answer a few quick questions and see which of 24 schemes you likely qualify for

Currently covering **24 real schemes** across agriculture, health, housing,
education, women & child welfare, pensions, and employment — including
Gujarat state-specific schemes.
        """
    )
    st.info("👈 Use the sidebar to pick your language and get started.")


# =============================================================================
# SCREEN 2: Chat interface
# =============================================================================
elif st.session_state.view == "Chat":
    st.header("💬 Chat")
    st.caption("Ask a question in English, Hindi, or Gujarati.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                for s in message["sources"][:3]:  # cap at 3 to keep it clean
                    st.caption(f"📄 Source: **{s['name']}** — [Official Link]({s['official_link']})")

    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Searching schemes and generating an answer..."):
            try:
                result = answer_question_multilingual(user_input)
                answer_text = result["answer"]
                sources = result["sources"]
            except Exception as e:
                answer_text = f"Sorry, something went wrong while answering ({type(e).__name__}). Please try again."
                sources = []

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer_text, "sources": sources}
        )
        st.rerun()


# =============================================================================
# SCREEN 3: Eligibility Checker
# =============================================================================
elif st.session_state.view == "Eligibility Checker":
    st.header("✅ Eligibility Checker")
    st.caption("Answer a few quick questions to see which schemes you're likely eligible for.")

    with st.form("eligibility_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            annual_family_income = st.number_input("Annual family income (Rs.)", min_value=0, value=200000, step=10000)
            state = st.selectbox("State", options=["Gujarat", "Other"])
            occupation = st.selectbox(
                "Occupation",
                options=[
                    "Farmer", "Artisan/Craftsperson", "Small Business Owner/Entrepreneur",
                    "Student", "Unorganised Sector Worker", "Homemaker",
                    "Government Employee", "Other",
                ],
            )
            gender = st.selectbox("Gender", options=["Female", "Male", "Other"])
        with col2:
            social_category = st.selectbox("Social category", options=["General", "OBC/SEBC", "SC", "ST", "EBC", "Minority"])
            marital_status = st.selectbox("Marital status", options=["Unmarried", "Married", "Widowed"])
            owns_pucca_house = st.checkbox("I already own a pucca (permanent) house")
            is_income_tax_payer = st.checkbox("I am an income tax payer")
            has_girl_child_under_10 = st.checkbox("I have a girl child under 10 years old")
            is_pregnant_or_recent_mother = st.checkbox("I am pregnant or a recent mother")

        submitted = st.form_submit_button("Check My Eligibility")

    if submitted:
        profile = {
            "age": age,
            "annual_family_income": annual_family_income,
            "state": state,
            "occupation": occupation,
            "gender": gender,
            "social_category": social_category,
            "marital_status": marital_status,
            "owns_pucca_house": owns_pucca_house,
            "is_income_tax_payer": is_income_tax_payer,
            "has_girl_child_under_10": has_girl_child_under_10,
            "is_pregnant_or_recent_mother": is_pregnant_or_recent_mother,
        }
        language_lower = st.session_state.language.lower()

        with st.spinner("Checking your eligibility across all schemes..."):
            try:
                raw_results = check_eligibility(profile)
            except Exception as e:
                st.error(f"Sorry, something went wrong while checking eligibility ({type(e).__name__}). Please try again.")
                raw_results = None

        if raw_results:
            eligible_raw = {sid: r for sid, r in raw_results.items() if r["status"] == "likely_eligible"}
            review_raw = {sid: r for sid, r in raw_results.items() if r["status"] == "check_manually"}
            not_eligible_raw = {sid: r for sid, r in raw_results.items() if r["status"] == "likely_not_eligible"}

            # Generate explanations ONCE here and cache the final text - not
            # re-generated on every rerun (e.g. every time you navigate away
            # and back), which would waste API calls unnecessarily.
            with st.spinner("Preparing explanations..."):
                eligible_final = [
                    {"name": r["name"], "link": r["official_link"], "explanation": explain_eligibility(r, profile, language_lower)}
                    for r in eligible_raw.values()
                ]
                review_final = [
                    {"name": r["name"], "link": r["official_link"], "explanation": explain_eligibility(r, profile, language_lower)}
                    for r in review_raw.values()
                ]
                not_eligible_final = [
                    {"name": r["name"], "reason": "; ".join(r["reasons"]) if r["reasons"] else "did not meet eligibility criteria"}
                    for r in not_eligible_raw.values()
                ]

            st.session_state.eligibility_results = {
                "total": len(raw_results),
                "eligible": eligible_final,
                "review": review_final,
                "not_eligible": not_eligible_final,
            }

    # Render from session_state (not tied to the submit event) so results
    # survive navigating away to another screen and back.
    results = st.session_state.eligibility_results
    if results:
        st.success(f"Checked all {results['total']} schemes.")

        st.subheader(f"✅ Likely Eligible ({len(results['eligible'])})")
        if results["eligible"]:
            for item in results["eligible"]:
                st.markdown(f"**{item['name']}**")
                st.markdown(item["explanation"])
                st.caption(f"📄 [Official Link]({item['link']})")
        else:
            st.caption("No schemes matched in this category.")

        st.subheader(f"❓ Check Manually ({len(results['review'])})")
        if results["review"]:
            for item in results["review"]:
                st.markdown(f"**{item['name']}**")
                st.markdown(item["explanation"])
                st.caption(f"📄 [Official Link]({item['link']})")
        else:
            st.caption("No schemes in this category.")

        with st.expander(f"❌ Likely Not Eligible ({len(results['not_eligible'])})"):
            for item in results["not_eligible"]:
                st.markdown(f"**{item['name']}** — {item['reason']}")