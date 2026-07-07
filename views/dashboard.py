import random
from datetime import datetime

import streamlit as st

from components import page_header, stat_card, empty_state, spacer, progress_bar
from state import get_study_stats, get_recent_activity


# Quotes seeded to today's date so they don't flicker on rerun
_QUOTES = [
    "The beautiful thing about learning is that no one can take it away from you. — B.B. King",
    "Education is the passport to the future. — Malcolm X",
    "The more that you read, the more things you will know. — Dr. Seuss",
    "Live as if you were to die tomorrow. Learn as if you were to live forever. — Gandhi",
    "The expert in anything was once a beginner. — Helen Hayes",
    "Learning never exhausts the mind. — Leonardo da Vinci",
]


def render() -> None:
    page_header("🏠", "Dashboard", "Your study overview at a glance.")

    stats = get_study_stats()

    # ── Stat cards ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("🔥", "Streak", stats["streak"], "days")
    with c2:
        stat_card("🃏", "Flashcards", stats["total_cards"],
                  f"{stats['easy']} easy · {stats['hard']} hard")
    with c3:
        stat_card("⏱️", "Study Time", stats["total_time"], "minutes total")
    with c4:
        stat_card("📝", "Notes", stats["total_notes"], "saved notes")

    spacer(20)

    # ── Quick actions + Recent activity ──
    left, right = st.columns(2)

    with left:
        st.markdown("#### ⚡ Quick Actions")
        spacer(8)
        _ACTIONS = [
            ("💬", "Chat with AI Tutor", "Ask questions about any topic", "AI Tutor"),
            ("🎴", "Study Flashcards", "Review your saved cards", "Flashcards"),
            ("📝", "Take a Quiz", "Test your knowledge", "Quiz"),
            ("📄", "Summarize Text", "Get AI summaries of study material", "Summarizer"),
            ("⏱️", "Start Focus Timer", "Begin a Pomodoro session", "Focus Timer"),
            ("📅", "Create Study Plan", "Generate a personalized plan", "Study Planner"),
        ]
        for icon, title, desc, page in _ACTIONS:
            if st.button(f"{icon} {title}", key=f"qa_{title}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
            st.caption(desc)

    with right:
        st.markdown("#### 📊 Recent Activity")
        spacer(8)
        activities = get_recent_activity()
        if not activities:
            empty_state("📋", "No Activity Yet",
                        "Start studying to see your activity here!")
        else:
            for act in activities:
                st.markdown(
                    f"""<div style="display:flex;align-items:center;gap:12px;
                        padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
                        <span style="font-size:1.2rem;">{act['icon']}</span>
                        <div style="flex:1;">
                            <div style="color:#e2e8f0;font-size:0.88rem;">{act['text']}</div>
                            <div style="color:#64748b;font-size:0.7rem;">{act['time']}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    spacer(20)

    # ── Study progress ──
    st.markdown("#### 📈 Study Progress")
    p1, p2 = st.columns(2)

    with p1:
        if stats["total_cards"] > 0:
            easy_pct = (stats["easy"] / stats["total_cards"]) * 100
            hard_pct = (stats["hard"] / stats["total_cards"]) * 100
            new_pct = (stats["new_cards"] / stats["total_cards"]) * 100

            st.markdown(
                '<div class="dashboard-card">'
                '<div style="font-weight:700;color:#f1f5f9;margin-bottom:12px;">Flashcard Mastery</div>',
                unsafe_allow_html=True,
            )
            progress_bar("Easy", easy_pct, "#059669", "#6ee7b7", "✅")
            progress_bar("Hard", hard_pct, "#e11d48", "#fda4af", "❌")
            progress_bar("New", new_pct, "#6d5bf6", "#a5b4fc", "🆕")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                """<div class="dashboard-card" style="text-align:center;padding:40px;">
                    <span style="font-size:2rem;display:block;margin-bottom:8px;">🃏</span>
                    <div style="color:#64748b;font-size:0.9rem;">
                        No flashcards yet. Create some to track progress!</div>
                </div>""",
                unsafe_allow_html=True,
            )

    with p2:
        st.markdown(
            f"""<div class="dashboard-card">
                <div style="font-weight:700;color:#f1f5f9;margin-bottom:12px;">Study Stats</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                    <div style="text-align:center;padding:16px;background:rgba(255,255,255,0.03);border-radius:12px;">
                        <div style="font-size:1.8rem;font-weight:800;color:#38bdf8;">{stats['total_sessions']}</div>
                        <div style="color:#64748b;font-size:0.75rem;margin-top:4px;">Sessions</div>
                    </div>
                    <div style="text-align:center;padding:16px;background:rgba(255,255,255,0.03);border-radius:12px;">
                        <div style="font-size:1.8rem;font-weight:800;color:#a78bfa;">{stats['total_time']}</div>
                        <div style="color:#64748b;font-size:0.75rem;margin-top:4px;">Minutes</div>
                    </div>
                    <div style="text-align:center;padding:16px;background:rgba(255,255,255,0.03);border-radius:12px;">
                        <div style="font-size:1.8rem;font-weight:800;color:#34d399;">{stats['total_notes']}</div>
                        <div style="color:#64748b;font-size:0.75rem;margin-top:4px;">Notes</div>
                    </div>
                    <div style="text-align:center;padding:16px;background:rgba(255,255,255,0.03);border-radius:12px;">
                        <div style="font-size:1.8rem;font-weight:800;color:#fbbf24;">{stats['streak']}</div>
                        <div style="color:#64748b;font-size:0.75rem;margin-top:4px;">Day Streak</div>
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Quote of the day (seeded, won't flicker) ──
    rng = random.Random(datetime.now().strftime("%Y-%m-%d"))
    quote = rng.choice(_QUOTES)
    st.markdown(
        f"""<div style="margin-top:24px;padding:20px;
            background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.1);
            border-radius:16px;text-align:center;">
            <span style="color:#a5b4fc;font-size:1.1rem;font-style:italic;">"{quote}"</span>
        </div>""",
        unsafe_allow_html=True,
    )
