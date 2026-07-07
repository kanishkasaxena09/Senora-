import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

import streamlit as st


# ── Defaults ────────────────────────────────────────────────────
_DEFAULTS: Dict = {
    # Flashcards
    "flashcards": [],
    "current_card_idx": 0,
    "card_flipped": False,
    # Quiz
    "quiz_questions": [],
    "current_quiz_idx": 0,
    "quiz_score": 0,
    "quiz_answered": False,
    "quiz_selected": None,
    # Chat
    "chat_history": [],
    # Summarizer
    "summary_text": "",
    "summary_result": "",
    # Timer
    "timer_running": False,
    "timer_end": None,
    "timer_mode": "Pomodoro (25 min)",
    "timer_sessions": 0,
    "total_study_time": 0,
    "session_history": [],
    # Notes
    "study_notes": [],
    "current_note": "",
    # Settings
    "selected_model": "llama-3.3-70b-versatile",
    "study_subject": "General",
    "current_page": "Dashboard",
    # Study planner
    "ai_planner_subject": "",
    "ai_planner_duration": "",
    "ai_planner_goals": "",
    "generated_plan": "",
    # Mind map
    "mind_map_data": None,
    # Essay grader
    "essay_input": "",
    "essay_feedback": "",
    # Citation
    "citation_input": "",
    "citation_result": "",
    # Collab room
    "collab_room_id": "",
    "collab_messages": [],
    # Streak / analytics
    "study_streak": 0,
    "last_study_date": None,
    "study_analytics": {
        "daily_minutes": {},
        "subject_breakdown": {},
        "weekly_scores": {},
    },
    "spaced_repetition": {},
    # Internal
    "_streak_checked_this_session": False,
}


# ── Init ────────────────────────────────────────────────────────
def init_session_state() -> None:
    """Populate session-state defaults and update the daily streak (once)."""
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # ── Streak logic (runs at most once per browser session) ────
    if not st.session_state._streak_checked_this_session:
        st.session_state._streak_checked_this_session = True
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        last = st.session_state.last_study_date

        if last != today:
            if last == yesterday:
                st.session_state.study_streak += 1
            elif last is None:
                st.session_state.study_streak = 1
            else:
                # Streak broken
                st.session_state.study_streak = 1
            st.session_state.last_study_date = today


# ── Unique ID generator ────────────────────────────────────────
def make_id() -> str:
    """Return a short unique ID safe for use as a Streamlit key."""
    return uuid.uuid4().hex[:10]


# ── Study stats ─────────────────────────────────────────────────
def get_study_stats() -> Dict:
    """Compute study statistics from session state."""
    cards = st.session_state.flashcards
    total_cards = len(cards)
    easy = sum(1 for c in cards if c.get("difficulty") == "easy")
    hard = sum(1 for c in cards if c.get("difficulty") == "hard")
    return {
        "total_cards": total_cards,
        "easy": easy,
        "hard": hard,
        "new_cards": total_cards - easy - hard,
        "total_notes": len(st.session_state.study_notes),
        "total_sessions": st.session_state.timer_sessions,
        "total_time": st.session_state.total_study_time // 60,
        "streak": st.session_state.study_streak,
    }


# ── Recent activity ─────────────────────────────────────────────
def get_recent_activity() -> List[Dict]:
    """Build a chronological list of recent study events."""
    activities: List[Dict] = []

    for s in st.session_state.session_history[-5:]:
        activities.append({
            "icon": "⏱️",
            "text": f"Completed {s.get('mode', 'study')} session",
            "time": s.get("date", "")[:16],
        })

    for n in st.session_state.study_notes[-3:]:
        activities.append({
            "icon": "📝",
            "text": f"Created note: {n.get('title', 'Untitled')}",
            "time": n.get("created", "")[:16],
        })

    for c in st.session_state.flashcards[-3:]:
        front = c.get("front", "")
        label = (front[:30] + "…") if len(front) > 30 else front
        activities.append({
            "icon": "🃏",
            "text": f"Added flashcard: {label}",
            "time": c.get("created", "")[:16],
        })

    activities.sort(key=lambda x: x["time"], reverse=True)
    return activities[:8]


# ── Export / Import ─────────────────────────────────────────────
def export_data() -> str:
    """Serialize study data as JSON."""
    data = {
        "flashcards": st.session_state.flashcards,
        "study_notes": st.session_state.study_notes,
        "session_history": st.session_state.session_history,
        "study_streak": st.session_state.study_streak,
        "timer_sessions": st.session_state.timer_sessions,
        "total_study_time": st.session_state.total_study_time,
        "study_analytics": st.session_state.study_analytics,
        "spaced_repetition": st.session_state.spaced_repetition,
        "exported_at": datetime.now().isoformat(),
    }
    return json.dumps(data, indent=2)


def import_data(data_str: str) -> bool:
    """Deserialize JSON study data into session state. Returns True on success."""
    try:
        data = json.loads(data_str)
    except (json.JSONDecodeError, ValueError):
        return False

    _IMPORTABLE = (
        "flashcards", "study_notes", "session_history",
        "study_analytics", "spaced_repetition",
    )
    for key in _IMPORTABLE:
        if key in data:
            st.session_state[key] = data[key]
    return True
