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
    st.session_state.view = "Home"
if "chat_history" not in st.session_state:
    # Mock conversation so the chat screen has something to show before Phase 5.3
    st.session_state.chat_history = [
        {"role": "user", "content": "What is the benefit under PM-KISAN?"},
        {
            "role": "assistant",
            "content": (
                "Under **PM-KISAN**, eligible farmer families receive Rs. 6,000 per year, "
                "paid in three installments of Rs. 2,000 every four months via DBT."
            ),
            "source": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "link": "https://pmkisan.gov.in",
        },
    ]

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
    st.caption("Ask a question in English, Hindi, or Gujarati — mock conversation shown below.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "source" in message:
                st.caption(f"📄 Source: {message['source']} · [Official link]({message['link']})")

    user_input = st.chat_input("Type your question here... (not wired to backend yet)")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": "*(placeholder response - real answers wired in Phase 5.3)*",
                "source": "N/A",
                "link": "#",
            }
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
        st.success("Here are your results (placeholder data - real matching wired in Phase 5.3):")

        st.subheader("✅ Likely Eligible")
        st.markdown("- **PM-KISAN** - income support for landholding farmer families")
        st.markdown("- **PM Jan Dhan Yojana** - zero-balance bank account")

        st.subheader("❓ Check Manually")
        st.markdown("- **Ayushman Bharat (PMJAY)** - requires SECC/BPL verification, please confirm at your nearest CSC")

        st.subheader("❌ Likely Not Eligible")
        st.markdown("- **Manav Garima Yojana** - occupation does not match required category")