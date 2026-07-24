"""
app.py

Phase 5.1: Streamlit Setup - basic app shell.

No backend logic yet - just page config, a language selector, and
navigation between the 'Chat' and 'Eligibility Checker' views (both
currently placeholders). Backend wiring happens in Phase 5.3.

Run with:
    streamlit run src/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Scheme Assistant",
    page_icon="🇮🇳",
    layout="centered",
)

# --- Session state defaults -------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = "English"
if "view" not in st.session_state:
    st.session_state.view = "Chat"

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
        options=["Chat", "Eligibility Checker"],
        index=["Chat", "Eligibility Checker"].index(st.session_state.view),
    )

# --- Main area: route to the selected view -----------------------------------
st.title("Scheme Assistant")

if st.session_state.view == "Chat":
    st.header("💬 Chat")
    st.info("Ask a question about any Indian government scheme, in English, Hindi, or Gujarati.")
    st.text_input("Type your question here...", disabled=True, placeholder="(Chat backend not wired yet - Phase 5.3)")

elif st.session_state.view == "Eligibility Checker":
    st.header("✅ Eligibility Checker")
    st.info("Answer a few quick questions to see which schemes you're likely eligible for.")
    st.button("Start Eligibility Check", disabled=True, help="(Eligibility backend not wired yet - Phase 5.3)")