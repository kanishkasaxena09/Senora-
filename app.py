import streamlit as st

from styles import inject_css
from state import init_session_state, export_data, import_data
from api import get_groq_client, GROQ_MODELS
from datetime import datetime

# ── Page config (must be first Streamlit call) ──────────────────
st.set_page_config(
    page_title="SENORA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialise ──────────────────────────────────────────────────
init_session_state()
inject_css()

# ── Page registry ───────────────────────────────────────────────
_NAV = [
    ("🏠", "Dashboard"),
    ("💬", "AI Tutor"),
    ("🎴", "Flashcards"),
    ("📝", "Quiz"),
    ("📄", "Summarizer"),
    ("⏱️", "Focus Timer"),
    ("🗒️", "Notes"),
    ("📅", "Study Planner"),
    ("🧠", "Mind Map"),
    ("📝", "Essay Grader"),
    ("📖", "Citation Gen"),
    ("🤝", "Collab Room"),
]

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(
        """<div style="text-align:center;margin-bottom:1.2rem;">
            <div style="font-size:2.8rem;margin-bottom:0.3rem;
                animation:float 4s ease-in-out infinite;display:inline-block;">🎓</div>
            <h1 style="font-size:1.35rem!important;margin:0;font-weight:800!important;">
                SENORA</h1>
            <p style="color:#64748b;font-size:0.75rem;margin-top:2px;">
                Study smarter, not harder</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Navigation
    st.markdown("### Navigation")
    for icon, page in _NAV:
        is_active = st.session_state.current_page == page
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon} {page}", key=f"nav_{page}",
                     use_container_width=True, type=btn_type):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")

    # API status
    if get_groq_client():
        st.success("✅ API Connected")
    else:
        st.error("❌ No API Key")
        st.info("Set `GROQ_API_KEY` in `.env`")

    st.markdown("---")

    # Model selection
    st.markdown("### AI Model")
    selected_name = st.selectbox("Choose Model", list(GROQ_MODELS.keys()),
                                 index=0, label_visibility="collapsed")
    st.session_state.selected_model = GROQ_MODELS[selected_name]

    # Subject
    st.markdown("### Subject")
    st.session_state.study_subject = st.text_input(
        "What are you studying?",
        value=st.session_state.study_subject,
        placeholder="e.g., Biology, Python, History...",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Streak badge
    if st.session_state.study_streak > 0:
        st.markdown(
            f"""<div style="text-align:center;margin-bottom:16px;">
                <span class="streak-badge">
                    🔥 {st.session_state.study_streak} day streak</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # Quick stats
    st.markdown("### Study Stats")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Sessions", st.session_state.timer_sessions)
    with c2:
        st.metric("Cards", len(st.session_state.flashcards))
    with c3:
        st.metric("Notes", len(st.session_state.study_notes))

    st.markdown("---")

    # Export / Import
    st.markdown("### Data")
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button(
            "⬇️ Export", export_data(),
            file_name=f"study_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json", use_container_width=True,
        )
    with ec2:
        uploaded = st.file_uploader("⬆️ Import", type=["json"],
                                    label_visibility="collapsed")
        if uploaded:
            if import_data(uploaded.read().decode("utf-8")):
                st.toast("✅ Data imported!")
                st.rerun()
            else:
                st.error("Invalid file")

    # Footer
    st.markdown(
        """<p style="text-align:center;color:#475569;font-size:0.7rem;margin-top:1rem;">
            SENORA v5.0 | Groq API + Streamlit
        </p>""",
        unsafe_allow_html=True,
    )


# ── Header ──────────────────────────────────────────────────────
st.markdown(
    """<div style="text-align:center;margin-bottom:8px;">
        <div style="display:inline-block;
            background:linear-gradient(135deg,#6d5bf6,#4f8ef7,#14b8a6);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;font-size:2.6rem;font-weight:800;
            letter-spacing:-0.04em;">
            SENORA
        </div>
    </div>
    <p style="text-align:center;color:#64748b;margin-bottom:30px;font-size:1rem;">
        Your intelligent companion for smarter learning
    </p>""",
    unsafe_allow_html=True,
)

# ── Page router ─────────────────────────────────────────────────
_PAGE_MODULES = {
    "Dashboard": "views.dashboard",
    "AI Tutor": "views.ai_tutor",
    "Flashcards": "views.flashcards",
    "Quiz": "views.quiz",
    "Summarizer": "views.summarizer",
    "Focus Timer": "views.focus_timer",
    "Notes": "views.notes",
    "Study Planner": "views.study_planner",
    "Mind Map": "views.mind_map",
    "Essay Grader": "views.essay_grader",
    "Citation Gen": "views.citation_gen",
    "Collab Room": "views.collab_room",
}

current = st.session_state.current_page
module_path = _PAGE_MODULES.get(current, "pages.dashboard")

# Dynamic import
import importlib
page_module = importlib.import_module(module_path)
page_module.render()

# ── Footer ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """<p style="text-align:center;color:#475569;font-size:0.75rem;">
        SENORA v5.0 | Powered by Groq API + Streamlit
    </p>""",
    unsafe_allow_html=True,
)