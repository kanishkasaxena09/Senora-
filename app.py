import os
import json
import random
import time
import math
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="SENORA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session_state():
    defaults = {
        "flashcards": [],
        "current_card_idx": 0,
        "card_flipped": False,
        "card_study_stats": {"known": 0, "learning": 0, "new": 0},
        "quiz_questions": [],
        "current_quiz_idx": 0,
        "quiz_score": 0,
        "quiz_answered": False,
        "quiz_selected": None,
        "chat_history": [],
        "chat_model": "llama-3.3-70b-versatile",
        "summary_text": "",
        "summary_result": "",
        "timer_running": False,
        "timer_end": None,
        "timer_mode": "Pomodoro (25 min)",
        "timer_sessions": 0,
        "study_notes": [],
        "current_note": "",
        "selected_model": "llama-3.3-70b-versatile",
        "study_subject": "General",
        "active_tab": 0,
        "sidebar_collapsed": False,
        "session_history": [],
        "show_toast": None,
        "dark_mode": True,
        "sound_enabled": False,
        "first_visit": True,
        "study_streak": 0,
        "last_study_date": None,
        "total_study_time": 0,
        "study_plan": None,
        "mind_map_data": None,
        "essay_input": "",
        "essay_feedback": "",
        "citation_input": "",
        "citation_result": "",
        "ai_planner_subject": "",
        "ai_planner_duration": "",
        "ai_planner_goals": "",
        "generated_plan": "",
        "voice_notes": [],
        "spaced_repetition": {},
        "study_analytics": {"daily_minutes": {}, "subject_breakdown": {}, "weekly_scores": {}},
        "diagram_prompt": "",
        "diagram_result": "",
        "collab_room_id": "",
        "collab_messages": [],
        "current_page": "Dashboard",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    # Update streak
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.last_study_date != today:
        if st.session_state.last_study_date == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
            st.session_state.study_streak += 1
        elif st.session_state.last_study_date is None:
            st.session_state.study_streak = 1
        else:
            st.session_state.study_streak = 1
        st.session_state.last_study_date = today

init_session_state()

# ============================================================
# GROQ API SETUP
# ============================================================
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass
    if not api_key:
        return None
    return Groq(api_key=api_key)

GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "Qwen 3.6 27B": "qwen/qwen3.6-27b",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS Safeguard 20B": "openai/gpt-oss-safeguard-20b",
}

VISION_MODELS = ["meta-llama/llama-4-scout-17b-16e-instruct", "qwen/qwen3.6-27b"]

def call_groq(messages: List[Dict], model: str = None, temperature: float = 0.7,
              max_tokens: int = 2048, stream: bool = False, response_format: Dict = None) -> str:
    client = get_groq_client()
    if not client:
        return "API Key not found. Set `GROQ_API_KEY` in environment or `.env` file."
    try:
        kwargs = {
            "messages": messages,
            "model": model or "llama-3.3-70b-versatile",
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "stream": stream,
        }
        if response_format:
            kwargs["response_format"] = response_format
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

def call_groq_vision(image_url: str, prompt: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> str:
    """Call Groq with vision capabilities"""
    client = get_groq_client()
    if not client:
        return "API Key not found."
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_completion_tokens=2048,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Vision API Error: {str(e)}"

# ============================================================
# EXPORT / IMPORT HELPERS
# ============================================================
def export_data() -> str:
    data = {
        "flashcards": st.session_state.flashcards,
        "study_notes": st.session_state.study_notes,
        "session_history": st.session_state.session_history,
        "study_streak": st.session_state.study_streak,
        "timer_sessions": st.session_state.timer_sessions,
        "quiz_score": st.session_state.quiz_score,
        "total_study_time": st.session_state.total_study_time,
        "study_analytics": st.session_state.study_analytics,
        "spaced_repetition": st.session_state.spaced_repetition,
        "exported_at": datetime.now().isoformat(),
    }
    return json.dumps(data, indent=2)

def import_data(data_str: str) -> bool:
    try:
        data = json.loads(data_str)
        if "flashcards" in data:
            st.session_state.flashcards = data["flashcards"]
        if "study_notes" in data:
            st.session_state.study_notes = data["study_notes"]
        if "session_history" in data:
            st.session_state.session_history = data["session_history"]
        if "study_analytics" in data:
            st.session_state.study_analytics = data["study_analytics"]
        if "spaced_repetition" in data:
            st.session_state.spaced_repetition = data["spaced_repetition"]
        return True
    except:
        return False

# ============================================================
# MAXIMUM CSS — CINEMATIC UI
# ============================================================
st.markdown("""
<style>
/* ─── RESET & BASE ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', -apple-system, sans-serif !important; }

.main .block-container {
    padding: 0 2rem 4rem 2rem;
    max-width: 1400px;
}

/* ─── ANIMATED MESH BACKGROUND ─── */
.stApp {
    background:
        radial-gradient(ellipse at 15% 20%, rgba(99, 102, 241, 0.18) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 80%, rgba(56, 189, 248, 0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 70%),
        linear-gradient(180deg, #06070a 0%, #090a10 50%, #07080e 100%);
    background-attachment: fixed;
}

/* ─── FLOATING PARTICLES CANVAS ─── */
@keyframes floatUp {
    0% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}
.particle {
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    animation: floatUp linear infinite;
    z-index: 0;
}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0b12 0%, #0d0e18 100%);
    border-right: 1px solid rgba(255,255,255,0.04);
}
[data-testid="stSidebar"] .block-container { background: transparent; padding: 1.2rem; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #94a3b8 !important; }
[data-testid="stSidebar"] small, [data-testid="stSidebar"] .stCaption { color: #64748b !important; }

/* ─── HEADINGS ─── */
h1 { color: #f8fafc !important; font-weight: 800 !important; letter-spacing: -0.04em !important; font-size: 2.4rem !important; }
h2 { color: #f1f5f9 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; font-size: 1.4rem !important; }
h3 { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 1.1rem !important; }

/* ─── GLASSMORPHISM CARDS (3D TILT) ─── */
.glass-card {
    background: rgba(20, 22, 38, 0.65);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 32px;
    position: relative;
    transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}
.glass-card:hover {
    transform: translateY(-3px) scale(1.005);
    box-shadow: 0 20px 50px rgba(0,0,0,0.35), 0 0 30px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.06);
    border-color: rgba(99,102,241,0.15);
}

/* ─── DASHBOARD CARDS ─── */
.dashboard-card {
    background: rgba(20, 22, 38, 0.65);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 24px;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    position: relative;
    overflow: hidden;
}
.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
}
.dashboard-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.35), 0 0 24px rgba(99,102,241,0.1);
    border-color: rgba(99,102,241,0.2);
}
.dashboard-card-icon {
    font-size: 2rem;
    margin-bottom: 12px;
    display: block;
}
.dashboard-card-title {
    color: #f1f5f9;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 4px;
}
.dashboard-card-value {
    color: #e2e8f0;
    font-weight: 800;
    font-size: 2rem;
    letter-spacing: -0.03em;
}
.dashboard-card-subtitle {
    color: #64748b;
    font-size: 0.8rem;
    margin-top: 4px;
}

/* ─── QUICK ACTION BUTTONS ─── */
.quick-action-btn {
    background: rgba(20, 22, 38, 0.5);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 16px 20px;
    color: #e2e8f0;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    text-align: left;
}
.quick-action-btn:hover {
    background: rgba(79, 70, 229, 0.1);
    border-color: rgba(99,102,241,0.3);
    transform: translateX(4px);
}
.quick-action-btn-icon {
    font-size: 1.5rem;
}

/* ─── 3D FLASHCARD ─── */
.flashcard-container {
    perspective: 1200px;
    width: 100%;
    min-height: 260px;
    cursor: pointer;
}
.flashcard-inner {
    position: relative;
    width: 100%;
    min-height: 260px;
    transition: transform 0.7s cubic-bezier(0.23, 1, 0.32, 1);
    transform-style: preserve-3d;
}
.flashcard-inner.flipped { transform: rotateY(180deg); }
.flashcard-front-3d, .flashcard-back-3d {
    position: absolute;
    width: 100%;
    min-height: 260px;
    backface-visibility: hidden;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
    font-size: 1.25rem;
    line-height: 1.7;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.flashcard-front-3d {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    border: 1px solid rgba(255,255,255,0.1);
}
.flashcard-back-3d {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
    border: 1px solid rgba(255,255,255,0.1);
    transform: rotateY(180deg);
}

/* ─── BUTTONS ─── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s ease;
}
.stButton > button:hover::after { left: 100%; }
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.45) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.98) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #f1f5f9 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
}

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(10, 12, 22, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12), 0 0 20px rgba(99, 102, 241, 0.06) !important;
}

/* ─── SELECTS ─── */
.stSelectbox > div > div,
.stSelectSlider > div > div {
    background: rgba(10, 12, 22, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
}

/* ─── SLIDER ─── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #06b6d4) !important;
    border-radius: 6px !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(10, 12, 22, 0.5) !important;
    border-radius: 18px !important;
    padding: 6px !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    border-radius: 14px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: none !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #e2e8f0 !important; background: rgba(255,255,255,0.03) !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35) !important;
}

/* ─── EXPANDER ─── */
.streamlit-expanderHeader {
    background: rgba(20, 22, 38, 0.5) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
    transition: all 0.25s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(20, 22, 38, 0.7) !important;
    border-color: rgba(99,102,241,0.15) !important;
}
/* Hide the default arrow icon to prevent overlap */
.streamlit-expanderHeader svg {
    display: none !important;
}
/* Add custom arrow using pseudo element */
.streamlit-expanderHeader::before {
    content: '▶';
    color: #6366f1;
    font-size: 0.7rem;
    transition: transform 0.3s ease;
    flex-shrink: 0;
}
.streamlit-expanderHeader[aria-expanded="true"]::before {
    content: '▼';
}
.streamlit-expanderContent {
    background: rgba(20, 22, 38, 0.3) !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    border-top: none !important;
    border-radius: 0 0 16px 16px !important;
    padding: 18px !important;
}

/* ─── CHAT MESSAGES ─── */
.chat-message-user {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 14px 22px;
    border-radius: 20px 20px 4px 20px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.25);
    animation: slideInRight 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    word-wrap: break-word;
}
.chat-message-assistant {
    background: rgba(20, 22, 38, 0.8);
    backdrop-filter: blur(12px);
    color: #e2e8f0;
    padding: 14px 22px;
    border-radius: 20px 20px 20px 4px;
    margin: 10px auto 10px 0;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid rgba(255,255,255,0.06);
    animation: slideInLeft 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    word-wrap: break-word;
}

/* ─── TIMER SVG RING ─── */
.timer-ring-container {
    position: relative;
    width: 260px;
    height: 260px;
    margin: 0 auto;
}
.timer-ring-svg {
    transform: rotate(-90deg);
}
.timer-ring-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 8; }
.timer-ring-progress {
    fill: none;
    stroke: url(#timerGradient);
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s linear;
    filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.4));
}
.timer-ring-text {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 3.2rem;
    font-weight: 800;
    color: #38bdf8;
    text-shadow: 0 0 30px rgba(56,189,248,0.3);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.04em;
}
.timer-ring-label {
    position: absolute;
    top: 65%; left: 50%;
    transform: translateX(-50%);
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ─── QUIZ QUESTION ─── */
.quiz-question-box {
    background: linear-gradient(135deg, rgba(79,70,229,0.08), rgba(124,58,237,0.04));
    border: 1px solid rgba(79,70,229,0.12);
    border-left: 4px solid #7c3aed;
    padding: 24px;
    border-radius: 18px;
    margin: 16px 0;
    font-size: 1.1rem;
    color: #e2e8f0;
    animation: cardEnter 0.4s ease-out;
}

/* ─── EXPLANATION BOX ─── */
.explanation-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(52,211,153,0.04));
    border: 1px solid rgba(16,185,129,0.15);
    padding: 18px 24px;
    border-radius: 14px;
    margin-top: 14px;
    color: #6ee7b7;
    font-size: 0.95rem;
    line-height: 1.6;
    animation: slideInLeft 0.3s ease-out;
}

/* ─── SCORE RESULT ─── */
.score-result-box {
    text-align: center;
    padding: 50px 40px;
    background: rgba(20, 22, 38, 0.7);
    backdrop-filter: blur(24px);
    border-radius: 28px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 25px 60px rgba(0,0,0,0.3);
    animation: scaleIn 0.5s cubic-bezier(0.23, 1, 0.32, 1);
}

/* ─── BADGES ─── */
.badge-easy {
    background: linear-gradient(135deg, #059669, #10b981);
    padding: 6px 16px;
    border-radius: 24px;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}
.badge-new {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    padding: 6px 16px;
    border-radius: 24px;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
}
.badge-hard {
    background: linear-gradient(135deg, #e11d48, #f43f5e);
    padding: 6px 16px;
    border-radius: 24px;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(225, 29, 72, 0.25);
}

/* ─── PROGRESS BAR ─── */
.stProgress > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #06b6d4) !important;
    border-radius: 10px !important;
    height: 8px !important;
}
.stProgress > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    height: 8px !important;
}

/* ─── METRIC CARDS ─── */
[data-testid="stMetric"] {
    background: rgba(20, 22, 38, 0.5);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 16px;
    padding: 12px 8px;
    text-align: center;
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(99,102,241,0.2);
    transform: translateY(-2px);
}
[data-testid="stMetric"] > div:first-child {
    color: #64748b !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetric"] > div:last-child {
    color: #f1f5f9 !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
}

/* ─── NOTE CARDS ─── */
.note-card {
    background: rgba(20, 22, 38, 0.4);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 14px;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}
.note-card:hover {
    background: rgba(20, 22, 38, 0.65);
    border-color: rgba(99, 102, 241, 0.2);
    box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    transform: translateY(-2px);
}
.note-tag {
    background: rgba(99, 102, 241, 0.12);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
    border: 1px solid rgba(99,102,241,0.1);
}

/* ─── ANIMATIONS ─── */
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(40px) scale(0.95); }
    to { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-40px) scale(0.95); }
    to { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes cardEnter {
    from { opacity: 0; transform: scale(0.92) translateY(16px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.88); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,0.15); }
    50% { box-shadow: 0 0 40px rgba(99,102,241,0.3); }
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes confetti {
    0% { transform: translateY(0) rotate(0deg); opacity: 1; }
    100% { transform: translateY(-500px) rotate(720deg); opacity: 0; }
}

/* ─── EMPTY STATE ─── */
.empty-state-box {
    text-align: center;
    padding: 56px 36px;
    background: rgba(20, 22, 38, 0.3);
    border: 2px dashed rgba(255,255,255,0.06);
    border-radius: 24px;
    animation: scaleIn 0.4s ease-out;
}
.empty-state-icon {
    font-size: 3.5rem;
    animation: float 4s ease-in-out infinite;
    display: block;
    margin-bottom: 1rem;
}

/* ─── FILE UPLOADER ─── */
.stFileUploader > div > div {
    background: rgba(10, 12, 22, 0.6) !important;
    border: 2px dashed rgba(79, 70, 229, 0.25) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
.stFileUploader > div > div:hover {
    border-color: rgba(79, 70, 229, 0.5) !important;
    background: rgba(79, 70, 229, 0.04) !important;
}

/* ─── TOAST NOTIFICATION ─── */
.toast-notification {
    position: fixed;
    bottom: 30px;
    right: 30px;
    padding: 16px 24px;
    background: rgba(20, 22, 38, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    color: #e2e8f0;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    z-index: 9999;
    animation: slideInRight 0.4s ease-out;
}

/* ─── ALERTS ─── */
.stAlert { border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.stAlert [data-testid="stAlertContentSuccess"] { background: rgba(16, 185, 129, 0.08) !important; color: #6ee7b7 !important; }
.stAlert [data-testid="stAlertContentInfo"] { background: rgba(56, 189, 248, 0.08) !important; color: #7dd3fc !important; }
.stAlert [data-testid="stAlertContentWarning"] { background: rgba(245, 158, 11, 0.08) !important; color: #fcd34d !important; }
.stAlert [data-testid="stAlertContentError"] { background: rgba(225, 29, 72, 0.08) !important; color: #fda4af !important; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #06070a; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #4f46e5, #7c3aed); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #6366f1, #8b5cf6); }

/* ─── HIDE BRANDING ─── */
#MainMenu,
footer {
    visibility: hidden;
}

/* Keep the header visible so the sidebar toggle remains */
header {
    visibility: visible !important;
}
.stDeployButton { display: none !important; }

/* ─── SHORTCUT BADGE ─── */
.kbd {
    display: inline-block;
    padding: 2px 8px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #94a3b8;
    font-family: monospace !important;
}

/* ─── STREAK BADGE ─── */
.streak-badge {
    background: linear-gradient(135deg, #f59e0b, #f97316);
    padding: 6px 14px;
    border-radius: 24px;
    color: white;
    font-weight: 800;
    font-size: 0.85rem;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* ─── DIVIDER ─── */
hr { border-color: rgba(255,255,255,0.04) !important; margin: 1.5rem 0 !important; }

/* ─── SPINNER ─── */
.stSpinner > div { border-color: #6366f1 transparent transparent transparent !important; }

/* ─── SUMMARY OUTPUT ─── */
.summary-output {
    background: rgba(20, 22, 38, 0.5);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 28px;
    min-height: 320px;
    max-height: 600px;
    overflow-y: auto;
    animation: cardEnter 0.4s ease-out;
    line-height: 1.7;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    .main .block-container { padding: 0 1rem 2rem 1rem !important; }
    .glass-card { padding: 20px; border-radius: 18px; }
    .timer-ring-container { width: 200px; height: 200px; }
    .timer-ring-text { font-size: 2.4rem; }
}

/* ─── MIND MAP STYLES ─── */
.mind-map-container {
    background: rgba(20, 22, 38, 0.5);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 24px;
    min-height: 400px;
    overflow-x: auto;
}
.mind-map-node {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 10px 18px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.9rem;
    display: inline-block;
    margin: 6px;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    transition: all 0.3s ease;
}
.mind-map-node:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
}
.mind-map-branch {
    background: rgba(99, 102, 241, 0.1);
    border-left: 3px solid #6366f1;
    padding: 8px 16px;
    border-radius: 0 10px 10px 0;
    margin: 4px 0 4px 20px;
    color: #e2e8f0;
    font-size: 0.85rem;
}

/* ─── STUDY PLAN STYLES ─── */
.study-plan-day {
    background: rgba(20, 22, 38, 0.5);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.study-plan-day:hover {
    border-color: rgba(99,102,241,0.2);
    transform: translateX(4px);
}
.study-plan-day-header {
    color: #a5b4fc;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 8px;
}
.study-plan-task {
    color: #94a3b8;
    font-size: 0.88rem;
    padding: 4px 0;
    padding-left: 16px;
    border-left: 2px solid rgba(99,102,241,0.3);
}

/* ─── COLLAB CHAT ─── */
.collab-message {
    padding: 10px 16px;
    border-radius: 14px;
    margin: 6px 0;
    font-size: 0.9rem;
    max-width: 85%;
}
.collab-message-user {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    margin-left: auto;
    border-radius: 14px 14px 4px 14px;
}
.collab-message-other {
    background: rgba(20, 22, 38, 0.7);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px 14px 14px 4px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# PARTICLE SYSTEM (JAVASCRIPT)
# ============================================================
st.markdown("""
<script>
// Create floating particles
(function() {
    const colors = ['rgba(99,102,241,0.3)', 'rgba(56,189,248,0.2)', 'rgba(139,92,246,0.25)', 'rgba(124,58,237,0.2)'];
    for (let i = 0; i < 20; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 6 + 2;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + 'vw';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.boxShadow = '0 0 ' + (size * 2) + 'px ' + p.style.background;
        p.style.animationDuration = (Math.random() * 15 + 10) + 's';
        p.style.animationDelay = (Math.random() * 10) + 's';
        document.body.appendChild(p);
    }
})();

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter') {
            const sendBtn = document.querySelector('button[kind="primary"]');
            if (sendBtn) sendBtn.click();
        }
    }
    if (e.key === ' ' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
    }
});
</script>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def render_empty_state(icon: str, title: str, subtitle: str):
    st.markdown(f"""
        <div class="empty-state-box">
            <span class="empty-state-icon">{icon}</span>
            <h3 style="color:#f1f5f9;margin-bottom:8px;font-weight:700;">{title}</h3>
            <p style="color:#64748b;font-size:0.95rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def show_toast(message: str, icon: str = "✅"):
    st.session_state.show_toast = {"message": message, "icon": icon}

def copy_to_clipboard(text: str, label: str = "Copy"):
    """Render a copy button using HTML."""
    import html as html_lib
    safe_text = html_lib.escape(text)
    st.markdown(f"""
    <button onclick="navigator.clipboard.writeText(`{safe_text}`);"
        style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
        border-radius:10px;padding:6px 14px;color:#94a3b8;font-size:0.8rem;
        cursor:pointer;transition:all 0.2s;"
        onmouseover="this.style.background='rgba(255,255,255,0.1)'"
        onmouseout="this.style.background='rgba(255,255,255,0.05)'">
        📋 {label}
    </button>
    """, unsafe_allow_html=True)

def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0

def get_study_stats():
    """Get current study statistics"""
    total_cards = len(st.session_state.flashcards)
    easy = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "easy")
    hard = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "hard")
    new_cards = total_cards - easy - hard

    total_notes = len(st.session_state.study_notes)
    total_sessions = st.session_state.timer_sessions
    total_time = st.session_state.total_study_time // 60
    streak = st.session_state.study_streak

    return {
        "total_cards": total_cards,
        "easy": easy,
        "hard": hard,
        "new_cards": new_cards,
        "total_notes": total_notes,
        "total_sessions": total_sessions,
        "total_time": total_time,
        "streak": streak,
    }

def get_recent_activity():
    """Get recent study activity"""
    activities = []

    # Add session history
    for s in st.session_state.session_history[-5:]:
        activities.append({
            "type": "session",
            "icon": "⏱️",
            "text": f"Completed {s['mode']} session",
            "time": s['date'][:16],
        })

    # Add note creation
    for n in st.session_state.study_notes[-3:]:
        activities.append({
            "type": "note",
            "icon": "📝",
            "text": f"Created note: {n['title']}",
            "time": n['created'][:16],
        })

    # Add flashcard creation
    for c in st.session_state.flashcards[-3:]:
        activities.append({
            "type": "card",
            "icon": "🃏",
            "text": f"Added flashcard: {c['front'][:30]}...",
            "time": c['created'][:16],
        })

    # Sort by time (newest first)
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities[:8]

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Logo
    st.markdown("""
        <div style="text-align:center;margin-bottom:1.2rem;">
            <div style="font-size:2.8rem;margin-bottom:0.3rem;animation:float 4s ease-in-out infinite;display:inline-block;">🎓</div>
            <h1 style="font-size:1.35rem!important;margin:0;font-weight:800!important;">SENORA</h1>
            <p style="color:#64748b;font-size:0.75rem;margin-top:2px;">Study smarter, not harder</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown("### Navigation")
    nav_options = [
        "🏠 Dashboard",
        "💬 AI Tutor",
        "🎴 Flashcards",
        "📝 Quiz",
        "📄 Summarizer",
        "⏱️ Focus Timer",
        "🗒️ Notes",
        "📅 Study Planner",
        "🧠 Mind Map",
        "📝 Essay Grader",
        "📖 Citation Gen",
        "🤝 Collab Room",
    ]

    nav_page_map = {
        "🏠 Dashboard": "Dashboard",
        "💬 AI Tutor": "AI Tutor",
        "🎴 Flashcards": "Flashcards",
        "📝 Quiz": "Quiz",
        "📄 Summarizer": "Summarizer",
        "⏱️ Focus Timer": "Focus Timer",
        "🗒️ Notes": "Notes",
        "📅 Study Planner": "Study Planner",
        "🧠 Mind Map": "Mind Map",
        "📝 Essay Grader": "Essay Grader",
        "📖 Citation Gen": "Citation Gen",
        "🤝 Collab Room": "Collab Room",
    }

    for nav in nav_options:
        page = nav_page_map[nav]
        is_active = st.session_state.current_page == page
        btn_type = "primary" if is_active else "secondary"
        if st.button(nav, key=f"nav_{page}", use_container_width=True, type=btn_type):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")

    # API Key Status
    client = get_groq_client()
    if client:
        st.success("✅ API Connected")
    else:
        st.error("❌ No API Key")
        st.info("Set `GROQ_API_KEY` in `.env`")

    st.markdown("---")

    # Model Selection
    st.markdown("### AI Model")
    selected_model_name = st.selectbox(
        "Choose Model", list(GROQ_MODELS.keys()), index=0, label_visibility="collapsed"
    )
    st.session_state.selected_model = GROQ_MODELS[selected_model_name]

    st.markdown("### Subject")
    st.session_state.study_subject = st.text_input(
        "What are you studying?", value=st.session_state.study_subject,
        placeholder="e.g., Biology, Python, History...", label_visibility="collapsed"
    )

    st.markdown("---")

    # Streak Badge
    if st.session_state.study_streak > 0:
        st.markdown(f"""
            <div style="text-align:center;margin-bottom:16px;">
                <span class="streak-badge">🔥 {st.session_state.study_streak} day streak</span>
            </div>
        """, unsafe_allow_html=True)

    # Stats
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
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.download_button("⬇️ Export", export_data(),
                          file_name=f"study_data_{datetime.now().strftime('%Y%m%d')}.json",
                          mime="application/json", use_container_width=True)
    with exp_col2:
        uploaded_json = st.file_uploader("⬆️ Import", type=["json"], label_visibility="collapsed")
        if uploaded_json:
            content = uploaded_json.read().decode("utf-8")
            if import_data(content):
                st.success("Imported!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid file")

    st.markdown("---")

    # Keyboard Shortcuts
    with st.expander("⌨️ Shortcuts"):
        st.markdown("""
        <div style="font-size:0.8rem;color:#94a3b8;line-height:2;">
        <span class="kbd">Ctrl+Enter</span> Send chat<br>
        <span class="kbd">Space</span> Flip card<br>
        <span class="kbd">← →</span> Navigate cards<br>
        <span class="kbd">1-4</span> Quiz options<br>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <p style="text-align:center;color:#475569;font-size:0.7rem;margin-top:1rem;">
            SENORA  v4.0 | Groq API + Streamlit
        </p>
    """, unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
    <div style="text-align:center;margin-bottom:8px;">
        <div style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed,#06b6d4);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        font-size:2.6rem;font-weight:800;letter-spacing:-0.04em;
        animation:gradientShift 4s ease infinite;background-size:200% 200%;">
            SENORA
        </div>
    </div>
    <p style="text-align:center;color:#64748b;margin-bottom:30px;font-size:1rem;">
        Your intelligent companion for smarter learning
    </p>
""", unsafe_allow_html=True)

# Toast notification
if st.session_state.show_toast:
    toast = st.session_state.show_toast
    st.markdown(f"""
        <div class="toast-notification">
            {toast['icon']} {toast['message']}
        </div>
    """, unsafe_allow_html=True)
    st.session_state.show_toast = None


# ============================================================
# DASHBOARD PAGE
# ============================================================
if st.session_state.current_page == "Dashboard":
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>🏠 Dashboard</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Your study overview at a glance.</p>
    </div>""", unsafe_allow_html=True)

    stats = get_study_stats()

    # Stats Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="dashboard-card">
                <span class="dashboard-card-icon">🔥</span>
                <div class="dashboard-card-title">Streak</div>
                <div class="dashboard-card-value">{stats['streak']}</div>
                <div class="dashboard-card-subtitle">days</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="dashboard-card">
                <span class="dashboard-card-icon">🃏</span>
                <div class="dashboard-card-title">Flashcards</div>
                <div class="dashboard-card-value">{stats['total_cards']}</div>
                <div class="dashboard-card-subtitle">{stats['easy']} easy, {stats['hard']} hard</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="dashboard-card">
                <span class="dashboard-card-icon">⏱️</span>
                <div class="dashboard-card-title">Study Time</div>
                <div class="dashboard-card-value">{stats['total_time']}</div>
                <div class="dashboard-card-subtitle">minutes total</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="dashboard-card">
                <span class="dashboard-card-icon">📝</span>
                <div class="dashboard-card-title">Notes</div>
                <div class="dashboard-card-value">{stats['total_notes']}</div>
                <div class="dashboard-card-subtitle">saved notes</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Quick Actions + Recent Activity
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("#### ⚡ Quick Actions")
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        actions = [
            ("💬", "Chat with AI Tutor", "Ask questions about any topic"),
            ("🎴", "Study Flashcards", "Review your saved cards"),
            ("📝", "Take a Quiz", "Test your knowledge"),
            ("📄", "Summarize Text", "Get AI summaries of study material"),
            ("⏱️", "Start Focus Timer", "Begin a Pomodoro session"),
            ("📅", "Create Study Plan", "Generate a personalized plan"),
        ]

        for icon, title, desc in actions:
            page_map = {
                "Chat with AI Tutor": "AI Tutor",
                "Study Flashcards": "Flashcards",
                "Take a Quiz": "Quiz",
                "Summarize Text": "Summarizer",
                "Start Focus Timer": "Focus Timer",
                "Create Study Plan": "Study Planner",
            }
            if st.button(f"{icon} {title}", key=f"qa_{title}", use_container_width=True):
                st.session_state.current_page = page_map.get(title, "Dashboard")
                st.rerun()
            st.markdown(f"<p style='color:#64748b;font-size:0.75rem;margin-top:-8px;margin-bottom:12px;padding-left:8px;'>{desc}</p>", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### 📊 Recent Activity")
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        activities = get_recent_activity()
        if not activities:
            render_empty_state("📋", "No Activity Yet", "Start studying to see your activity here!")
        else:
            for act in activities:
                st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
                        <span style="font-size:1.2rem;">{act['icon']}</span>
                        <div style="flex:1;">
                            <div style="color:#e2e8f0;font-size:0.88rem;">{act['text']}</div>
                            <div style="color:#64748b;font-size:0.7rem;">{act['time']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Study Progress Section
    st.markdown("#### 📈 Study Progress")
    prog_col1, prog_col2 = st.columns([1, 1])

    with prog_col1:
        if stats['total_cards'] > 0:
            easy_pct = (stats['easy'] / stats['total_cards']) * 100
            hard_pct = (stats['hard'] / stats['total_cards']) * 100
            new_pct = (stats['new_cards'] / stats['total_cards']) * 100

            st.markdown(f"""
                <div class="dashboard-card">
                    <div style="font-weight:700;color:#f1f5f9;margin-bottom:12px;">Flashcard Mastery</div>
                    <div style="margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="color:#6ee7b7;font-size:0.8rem;">✅ Easy</span>
                            <span style="color:#6ee7b7;font-size:0.8rem;font-weight:600;">{easy_pct:.0f}%</span>
                        </div>
                        <div style="background:rgba(255,255,255,0.05);border-radius:8px;height:8px;overflow:hidden;">
                            <div style="background:linear-gradient(90deg,#059669,#10b981);height:100%;width:{easy_pct}%;border-radius:8px;transition:width 0.5s ease;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="color:#fda4af;font-size:0.8rem;">❌ Hard</span>
                            <span style="color:#fda4af;font-size:0.8rem;font-weight:600;">{hard_pct:.0f}%</span>
                        </div>
                        <div style="background:rgba(255,255,255,0.05);border-radius:8px;height:8px;overflow:hidden;">
                            <div style="background:linear-gradient(90deg,#e11d48,#f43f5e);height:100%;width:{hard_pct}%;border-radius:8px;transition:width 0.5s ease;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="color:#a5b4fc;font-size:0.8rem;">🆕 New</span>
                            <span style="color:#a5b4fc;font-size:0.8rem;font-weight:600;">{new_pct:.0f}%</span>
                        </div>
                        <div style="background:rgba(255,255,255,0.05);border-radius:8px;height:8px;overflow:hidden;">
                            <div style="background:linear-gradient(90deg,#4f46e5,#7c3aed);height:100%;width:{new_pct}%;border-radius:8px;transition:width 0.5s ease;"></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="dashboard-card" style="text-align:center;padding:40px;">
                    <span style="font-size:2rem;display:block;margin-bottom:8px;">🃏</span>
                    <div style="color:#64748b;font-size:0.9rem;">No flashcards yet. Create some to track progress!</div>
                </div>
            """, unsafe_allow_html=True)

    with prog_col2:
        st.markdown(f"""
            <div class="dashboard-card">
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
            </div>
        """, unsafe_allow_html=True)

    # Motivational Quote
    quotes = [
        "The beautiful thing about learning is that no one can take it away from you. — B.B. King",
        "Education is the passport to the future. — Malcolm X",
        "The more that you read, the more things you will know. — Dr. Seuss",
        "Live as if you were to die tomorrow. Learn as if you were to live forever. — Gandhi",
        "The expert in anything was once a beginner. — Helen Hayes",
        "Learning never exhausts the mind. — Leonardo da Vinci",
    ]
    quote = random.choice(quotes)
    st.markdown(f"""
        <div style="margin-top:24px;padding:20px;background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.1);border-radius:16px;text-align:center;">
            <span style="color:#a5b4fc;font-size:1.1rem;font-style:italic;">"{quote}"</span>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# TAB 1: AI TUTOR
# ============================================================
if st.session_state.current_page == "AI Tutor":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_AI_Tutor", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>💬 AI Tutor Chat</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Ask anything. The AI adapts to your level.</p>
    </div>""", unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            render_empty_state("🤖", "Start a Conversation",
                             "Ask a question or pick a quick prompt below.")
        else:
            for msg in st.session_state.chat_history:
                cls = "chat-message-user" if msg["role"] == "user" else "chat-message-assistant"
                st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Ask:", placeholder=f"Ask about {st.session_state.study_subject}...",
                                   key="chat_input", label_visibility="collapsed")
    with col2:
        send_clicked = st.button("🚀 Send", use_container_width=True)

    st.markdown("<p style='color:#64748b;font-size:0.8rem;margin:8px 0 6px;'><b>Quick Questions:</b></p>", unsafe_allow_html=True)
    qc = st.columns(4)
    quick_prompts = ["Explain simply", "Practice problems", "Study plan", "Quiz me"]
    quick_clicked = None
    for i, p in enumerate(quick_prompts):
        with qc[i]:
            if st.button(p, key=f"qp_{i}", use_container_width=True):
                quick_clicked = p

    message_to_send = None
    if send_clicked and user_input.strip():
        message_to_send = user_input.strip()
    elif quick_clicked:
        message_to_send = quick_clicked

    if message_to_send:
        st.session_state.chat_history.append({"role": "user", "content": message_to_send})
        system_prompt = f"""You are an expert AI tutor in {st.session_state.study_subject}.
Teaching style: clear, patient, uses analogies, breaks down complex topics, provides memory techniques.
Adapt to the student's level."""
        messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.chat_history[-10:]:
            messages.append(m)
        with st.spinner("Thinking..."):
            response = call_groq(messages=messages, model=st.session_state.selected_model, temperature=0.7, max_tokens=2048)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.chat_history:
        c1, c2 = st.columns([1, 6])
        with c1:
            if st.button("🗑️ Clear", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
        with c2:
            if st.session_state.chat_history:
                all_chat = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_history])
                copy_to_clipboard(all_chat, "Copy Chat")


# ============================================================
# TAB 2: FLASHCARDS (with 3D Flip)
# ============================================================
if st.session_state.current_page == "Flashcards":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Flashcards", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>🎴 Smart Flashcards</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Create, generate, and study with 3D flip cards.</p>
    </div>""", unsafe_allow_html=True)

    cl, cr = st.columns([1, 2])

    with cl:
        st.markdown("#### Create")
        with st.expander("✍️ Manual", expanded=True):
            cf = st.text_area("Front:", placeholder="What is photosynthesis?", height=70, key="cf_front")
            cb = st.text_area("Back:", placeholder="Process of converting light to energy...", height=70, key="cf_back")
            if st.button("➕ Add", use_container_width=True):
                if cf and cb:
                    st.session_state.flashcards.append({
                        "front": cf, "back": cb,
                        "created": datetime.now().isoformat(), "difficulty": "new"
                    })
                    st.success("Added!")
                    st.rerun()

        with st.expander("🤖 AI Generate"):
            topic = st.text_input("Topic:", placeholder="e.g., Cell Biology, Python")
            nc = st.slider("Count:", 3, 10, 5)
            if st.button("✨ Generate", use_container_width=True):
                if topic:
                    with st.spinner("Generating..."):
                        prompt = f"""Generate {nc} flashcards about "{topic}" in {st.session_state.study_subject}.
Return ONLY a JSON array: [{{"front":"...","back":"..."}},...]"""
                        r = call_groq(messages=[{"role": "user", "content": prompt}],
                                     model=st.session_state.selected_model, temperature=0.5,
                                     max_tokens=2048, response_format={"type": "json_object"})
                        try:
                            if not r.startswith("API"):
                                js = r.split("```json")[-1].split("```")[0] if "```" in r else r
                                cards = json.loads(js)
                                if isinstance(cards, dict): cards = cards.get("flashcards", cards.get("cards", []))
                                for c in cards:
                                    st.session_state.flashcards.append({
                                        "front": c["front"], "back": c["back"],
                                        "created": datetime.now().isoformat(), "difficulty": "new"
                                    })
                                st.success(f"Generated {len(cards)} cards!"); time.sleep(0.8); st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {str(e)[:80]}"); st.code(r[:400])

        with st.expander("📤 Import"):
            uf = st.file_uploader("Upload .txt:", type=["txt"])
            if uf:
                content = uf.read().decode("utf-8")
                if st.button("🔄 Convert"):
                    with st.spinner("Converting..."):
                        prompt = f"""Convert to flashcards. Return JSON: [{{"front":"...","back":"..."}},...]
{content[:3000]}"""
                        r = call_groq(messages=[{"role": "user", "content": prompt}],
                                     model=st.session_state.selected_model, temperature=0.3, max_tokens=2048)
                        try:
                            for c in json.loads(r):
                                st.session_state.flashcards.append({
                                    "front": c["front"], "back": c["back"],
                                    "created": datetime.now().isoformat(), "difficulty": "new"
                                })
                            st.success("Done!"); st.rerun()
                        except: st.error("Failed.")

    with cr:
        st.markdown("#### Study Mode")
        if not st.session_state.flashcards:
            render_empty_state("🃏", "No Flashcards",
                             "Create cards on the left or generate with AI.")
        else:
            total = len(st.session_state.flashcards)
            idx = st.session_state.current_card_idx % total
            card = st.session_state.flashcards[idx]

            st.progress((idx + 1) / total, text=f"Card {idx + 1} of {total}")

            # 3D Flip Card
            flip_class = "flipped" if st.session_state.card_flipped else ""
            st.markdown(f"""
                <div class="flashcard-container">
                    <div class="flashcard-inner {flip_class}">
                        <div class="flashcard-front-3d">
                            <div>
                                <div style="font-size:0.75rem;opacity:0.6;margin-bottom:10px;font-weight:700;letter-spacing:0.08em;">QUESTION</div>
                                <div style="font-weight:600;font-size:1.2rem;">{card['front']}</div>
                            </div>
                        </div>
                        <div class="flashcard-back-3d">
                            <div>
                                <div style="font-size:0.75rem;opacity:0.6;margin-bottom:10px;font-weight:700;letter-spacing:0.08em;">ANSWER</div>
                                <div style="font-weight:500;font-size:1.1rem;">{card['back']}</div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            bc = st.columns([1, 1, 1, 1, 1])
            with bc[0]:
                if st.button("◀ Prev"):
                    st.session_state.current_card_idx = (idx - 1) % total
                    st.session_state.card_flipped = False; st.rerun()
            with bc[1]:
                if st.button("🔄 Flip", type="primary"):
                    st.session_state.card_flipped = not st.session_state.card_flipped; st.rerun()
            with bc[2]:
                if st.button("❌ Hard"):
                    card["difficulty"] = "hard"
                    st.session_state.current_card_idx = (idx + 1) % total
                    st.session_state.card_flipped = False; st.rerun()
            with bc[3]:
                if st.button("✅ Easy"):
                    card["difficulty"] = "easy"
                    st.session_state.current_card_idx = (idx + 1) % total
                    st.session_state.card_flipped = False; st.rerun()
            with bc[4]:
                if st.button("Next ▶"):
                    st.session_state.current_card_idx = (idx + 1) % total
                    st.session_state.card_flipped = False; st.rerun()

            if st.button("🔀 Shuffle", use_container_width=True):
                random.shuffle(st.session_state.flashcards)
                st.session_state.current_card_idx = 0
                st.session_state.card_flipped = False; st.rerun()

            easy = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "easy")
            hard = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "hard")
            new = total - easy - hard
            st.markdown(f"""
                <div style="display:flex;justify-content:center;gap:14px;margin-top:20px;">
                    <span class="badge-easy">✅ Easy {easy}</span>
                    <span class="badge-new">🆕 New {new}</span>
                    <span class="badge-hard">❌ Hard {hard}</span>
                </div>
            """, unsafe_allow_html=True)


# ============================================================
# TAB 3: QUIZ
# ============================================================
if st.session_state.current_page == "Quiz":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Quiz", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>📝 AI Quiz Generator</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Test your knowledge with AI-generated quizzes.</p>
    </div>""", unsafe_allow_html=True)

    ql, qr = st.columns([1, 2])

    with ql:
        st.markdown("#### Generate")
        qt = st.text_area("Topic/Notes:", placeholder="Paste notes or describe a topic...", height=130)
        qc = st.slider("Questions:", 3, 10, 5)
        qd = st.select_slider("Difficulty:", ["Easy", "Medium", "Hard"], value="Medium")
        if st.button("🎯 Generate", use_container_width=True, type="primary"):
            if qt.strip():
                with st.spinner("Creating..."):
                    prompt = f"""Generate a {qd.lower()} quiz with {qc} MCQs. Return ONLY JSON:
{{"questions":[{{"question":"...","options":["a","b","c","d"],"correct":0,"explanation":"..."}}]}}

Content: {qt[:4000]}"""
                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.3,
                                 max_tokens=4096, response_format={"type": "json_object"})
                    try:
                        if not r.startswith("API"):
                            js = r.split("```json")[-1].split("```")[0] if "```" in r else r
                            data = json.loads(js)
                            st.session_state.quiz_questions = data.get("questions", [])
                            st.session_state.current_quiz_idx = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_answered = False
                            st.session_state.quiz_selected = None
                            st.success(f"Generated {len(st.session_state.quiz_questions)} questions!")
                            time.sleep(0.8); st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)[:80]}"); st.code(r[:500])

    with qr:
        st.markdown("#### Take Quiz")
        if not st.session_state.quiz_questions:
            render_empty_state("🎯", "No Quiz Yet", "Generate one on the left to start!")
        else:
            qs = st.session_state.quiz_questions
            idx = st.session_state.current_quiz_idx
            if idx < len(qs):
                q = qs[idx]
                st.progress(idx / len(qs), text=f"Q{idx+1} of {len(qs)}")
                st.markdown(f"**Score: {st.session_state.quiz_score}/{len(qs)}**")
                st.markdown(f'<div class="quiz-question-box"><strong>Q{idx+1}:</strong> {q["question"]}</div>', unsafe_allow_html=True)

                for i, opt in enumerate(q["options"]):
                    label = chr(65 + i)
                    if st.session_state.quiz_answered:
                        if i == q["correct"]: st.success(f"✅ {label}. {opt}")
                        elif i == st.session_state.quiz_selected and i != q["correct"]: st.error(f"❌ {label}. {opt}")
                        else: st.markdown(f"{label}. {opt}")
                    else:
                        if st.button(f"{label}. {opt}", key=f"qo_{i}", use_container_width=True):
                            st.session_state.quiz_selected = i
                            st.session_state.quiz_answered = True
                            if i == q["correct"]: st.session_state.quiz_score += 1
                            st.rerun()

                if st.session_state.quiz_answered:
                    st.markdown(f'<div class="explanation-box">💡 <b>Explanation:</b> {q["explanation"]}</div>', unsafe_allow_html=True)
                    if st.button("Next Question ➡", use_container_width=True, type="primary"):
                        st.session_state.current_quiz_idx += 1
                        st.session_state.quiz_answered = False
                        st.session_state.quiz_selected = None
                        st.rerun()
            else:
                score = st.session_state.quiz_score
                total = len(qs)
                pct = (score / total) * 100
                if pct >= 80: emoji, color, msg = "🌟", "#34d399", "Excellent! You're a master!"
                elif pct >= 60: emoji, color, msg = "👍", "#a78bfa", "Good job! Keep practicing!"
                else: emoji, color, msg = "📚", "#f43f5e", "Keep studying! You'll get there!"

                st.balloons()
                st.markdown(f"""
                    <div class="score-result-box" style="border:2px solid {color}33;">
                        <div style="font-size:3.5rem;margin-bottom:8px;">{emoji}</div>
                        <h2 style="color:{color};margin:0 0 8px;">{msg}</h2>
                        <div style="font-size:2.8rem;font-weight:800;color:{color};letter-spacing:-0.03em;">{score}/{total}</div>
                        <p style="color:#64748b;">{pct:.0f}% Correct</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🔄 New Quiz", use_container_width=True, type="primary"):
                    st.session_state.quiz_questions = []
                    st.session_state.current_quiz_idx = 0
                    st.session_state.quiz_score = 0
                    st.rerun()


# ============================================================
# TAB 4: SUMMARIZER
# ============================================================
if st.session_state.current_page == "Summarizer":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Summarizer", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>📄 AI Summarizer</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Paste material and get structured summaries.</p>
    </div>""", unsafe_allow_html=True)

    s1, s2 = st.columns([1, 1])
    with s1:
        st.markdown("#### Input")
        inp = st.text_area("Material:", value=st.session_state.summary_text,
                          placeholder="Paste notes, textbook, article...", height=280, key="sum_inp")
        st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{word_count(inp)} words</span>", unsafe_allow_html=True)
        stype = st.selectbox("Type:", ["Concise", "Detailed Notes", "Key Points", "Study Guide", "ELI5"])

        if st.button("✨ Summarize", use_container_width=True, type="primary"):
            if inp.strip():
                st.session_state.summary_text = inp
                with st.spinner("Summarizing..."):
                    ti = {"Concise": "Concise 2-3 paragraph summary.",
                          "Detailed Notes": "Detailed notes with all concepts and definitions.",
                          "Key Points": "Key points as organized bullet list.",
                          "Study Guide": "Study guide with concepts, definitions, formulas, review questions.",
                          "ELI5": "Explain using simple analogies for a beginner."}
                    prompt = f"""{ti[stype]}
Format with markdown headers, bullets, emphasis.

Material:
{inp[:6000]}"""
                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.4, max_tokens=4096)
                    st.session_state.summary_result = r; st.rerun()
            else:
                st.warning("Enter text to summarize.")

    with s2:
        st.markdown("#### Output")
        if st.session_state.summary_result:
            st.markdown(f'<div class="summary-output">{st.session_state.summary_result}</div>', unsafe_allow_html=True)
            copy_to_clipboard(st.session_state.summary_result, "Copy")
            st.download_button("⬇️ Download", st.session_state.summary_result,
                             file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                             mime="text/markdown")
        else:
            render_empty_state("✍️", "Summary Appears Here", "Enter material and click 'Summarize'.")


# ============================================================
# TAB 5: FOCUS TIMER (with SVG Ring)
# ============================================================
if st.session_state.current_page == "Focus Timer":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Focus_Timer", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>⏱️ Focus Timer</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Pomodoro technique with visual ring timer.</p>
    </div>""", unsafe_allow_html=True)

    tl, tr = st.columns([1, 1])

    with tl:
        st.markdown("#### Settings")
        tm = st.selectbox("Mode:", ["Pomodoro (25 min)", "Short Break (5 min)", "Long Break (15 min)", "Custom"])
        if tm == "Custom":
            cm = st.number_input("Minutes:", min_value=1, max_value=120, value=25)
            duration = cm * 60
        else:
            duration = {"Pomodoro (25 min)": 1500, "Short Break (5 min)": 300, "Long Break (15 min)": 900}[tm]
        st.session_state.timer_mode = tm

        bc = st.columns(3)
        with bc[0]:
            if st.button("▶ Start", use_container_width=True, type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_end = datetime.now() + timedelta(seconds=duration)
                st.rerun()
        with bc[1]:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state.timer_running = False; st.rerun()
        with bc[2]:
            if st.button("↺ Reset", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_end = None; st.rerun()

        st.markdown("---")
        st.markdown(f"**Completed:** {st.session_state.timer_sessions} sessions")
        st.markdown(f"**Total time:** {st.session_state.total_study_time // 60}m")

        with st.expander("💡 Focus Tips"):
            st.markdown("""- **Single-task** — Focus on ONE thing
- **No phone** — Eliminate distractions
- **Plan ahead** — Know your goal before starting
- **Hydrate** — Keep water nearby
- **Move** — Stretch during breaks""")

    with tr:
        st.markdown("#### Timer")
        running = st.session_state.timer_running and st.session_state.timer_end
        if running:
            remaining = (st.session_state.timer_end - datetime.now()).total_seconds()
            if remaining <= 0:
                remaining = 0
                st.session_state.timer_running = False
                st.session_state.timer_sessions += 1
                st.session_state.total_study_time += duration
                st.session_state.session_history.append({
                    "mode": tm, "date": datetime.now().isoformat(), "duration": duration
                })
                st.balloons()
                st.success("🎉 Session complete! Great work!")
            progress = 1 - (remaining / duration) if duration > 0 else 1
        else:
            remaining = duration
            progress = 0

        mins, secs = divmod(int(max(0, remaining)), 60)
        timer_str = f"{mins:02d}:{secs:02d}"

        # SVG Ring Timer
        radius = 110
        circumference = 2 * math.pi * radius
        offset = circumference * (1 - progress)
        st.markdown(f"""
            <div class="timer-ring-container">
                <svg class="timer-ring-svg" width="260" height="260">
                    <defs>
                        <linearGradient id="timerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#4f46e5"/>
                            <stop offset="100%" style="stop-color:#06b6d4"/>
                        </linearGradient>
                    </defs>
                    <circle class="timer-ring-bg" cx="130" cy="130" r="{radius}"/>
                    <circle class="timer-ring-progress" cx="130" cy="130" r="{radius}"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"/>
                </svg>
                <div class="timer-ring-text">{timer_str}</div>
                <div class="timer-ring-label">{tm.split('(')[0].strip()}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.timer_running:
            st.info("🔥 Stay focused!")
        else:
            st.warning("⏸ Paused — Ready when you are")

        if st.session_state.timer_running and remaining > 0:
            time.sleep(1); st.rerun()

    # Session History
    if st.session_state.session_history:
        st.markdown("---")
        st.markdown("#### Recent Sessions")
        for s in reversed(st.session_state.session_history[-5:]):
            st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>⏱ {s['mode']} — {s['date'][:10]} {s['date'][11:16]}</span>", unsafe_allow_html=True)


# ============================================================
# TAB 6: STUDY NOTES
# ============================================================
if st.session_state.current_page == "Notes":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Notes", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>🗒️ Study Notes</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Create, search, and enhance notes with AI.</p>
    </div>""", unsafe_allow_html=True)

    nl, nr = st.columns([1, 1])

    with nl:
        st.markdown("#### Create")
        nt = st.text_input("Title:", placeholder="e.g., Chapter 3 - Cell Structure")
        nc = st.text_area("Content:", placeholder="Write notes...", height=180, key="note_content")
        ntags = st.text_input("Tags:", placeholder="biology, cells, exam-prep")
        st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{word_count(nc)} words</span>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save", use_container_width=True, type="primary"):
                if nt and nc:
                    st.session_state.study_notes.append({
                        "title": nt, "content": nc,
                        "tags": [t.strip() for t in ntags.split(",") if t.strip()],
                        "created": datetime.now().isoformat(),
                        "id": len(st.session_state.study_notes) + 1
                    })
                    st.success("Saved!"); time.sleep(0.5); st.rerun()
        with c2:
            if st.button("✨ AI Enhance", use_container_width=True):
                if nc.strip():
                    with st.spinner("Enhancing..."):
                        prompt = f"""Improve and structure these notes with markdown formatting.
Keep original info, enhance clarity, add helpful context.

Notes: {nc[:3000]}"""
                        r = call_groq(messages=[{"role": "user", "content": prompt}],
                                     model=st.session_state.selected_model, temperature=0.4, max_tokens=4096)
                        st.session_state.current_note = r; st.rerun()
                else:
                    st.warning("Enter content first.")

        if st.session_state.current_note:
            st.markdown("---")
            st.markdown("#### Enhanced:")
            st.markdown(st.session_state.current_note)
            copy_to_clipboard(st.session_state.current_note, "Copy Enhanced")

    with nr:
        st.markdown("#### Saved Notes")
        if not st.session_state.study_notes:
            render_empty_state("📝", "No Notes Yet", "Create a note on the left!")
        else:
            search = st.text_input("🔍 Search:", placeholder="By title or tag...")
            for note in reversed(st.session_state.study_notes):
                if search and search.lower() not in note["title"].lower() and search.lower() not in ",".join(note["tags"]).lower():
                    continue
                with st.expander(f"📄 {note['title']}"):
                    tags = "".join([f'<span class="note-tag">{t}</span>' for t in note["tags"]]) if note["tags"] else '<span style="color:#475569;font-size:0.75rem;">No tags</span>'
                    st.markdown(f"<div style='margin-bottom:8px;'>{tags}</div>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#475569;font-size:0.75rem;'>🕐 {note['created'][:10]}</span>", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(note["content"])
                    ac = st.columns(3)
                    with ac[0]:
                        if st.button("📝 Edit", key=f"ed_{note['id']}", use_container_width=True):
                            st.session_state.current_note = note["content"]; st.rerun()
                    with ac[1]:
                        if st.button("🗑️ Delete", key=f"dl_{note['id']}", use_container_width=True):
                            st.session_state.study_notes = [n for n in st.session_state.study_notes if n["id"] != note["id"]]
                            st.rerun()
                    with ac[2]:
                        if st.button("🃏 To Cards", key=f"fc_{note['id']}", use_container_width=True):
                            with st.spinner("Converting..."):
                                prompt = f"""Convert to flashcards. Return JSON: [{{"front":"...","back":"..."}},...]
{note['content'][:3000]}"""
                                r = call_groq(messages=[{"role": "user", "content": prompt}],
                                             model=st.session_state.selected_model, temperature=0.3, max_tokens=2048)
                                try:
                                    for c in json.loads(r):
                                        st.session_state.flashcards.append({
                                            "front": c["front"], "back": c["back"],
                                            "created": datetime.now().isoformat(), "difficulty": "new"
                                        })
                                    st.success(f"Created flashcards!"); time.sleep(0.8); st.rerun()
                                except: st.error("Failed.")


# ============================================================
# NEW FEATURE 1: STUDY PLANNER
# ============================================================
if st.session_state.current_page == "Study Planner":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Study_Planner", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>📅 AI Study Planner</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Generate a personalized study schedule with AI.</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Plan Settings")
        subject = st.text_input("Subject:", value=st.session_state.study_subject, placeholder="e.g., Organic Chemistry")
        duration = st.selectbox("Duration:", ["1 Week", "2 Weeks", "1 Month", "3 Months", "Custom"])
        if duration == "Custom":
            custom_days = st.number_input("Days:", min_value=1, max_value=365, value=14)
        goals = st.text_area("Goals:", placeholder="What do you want to achieve? e.g., Pass midterm, learn Python basics...", height=80)

        col1, col2 = st.columns(2)
        with col1:
            study_hours = st.slider("Hours/day:", 1, 8, 2)
        with col2:
            intensity = st.select_slider("Intensity:", ["Relaxed", "Moderate", "Intense"])

        if st.button("✨ Generate Plan", use_container_width=True, type="primary"):
            if subject and goals:
                with st.spinner("Creating your personalized study plan..."):
                    days = {"1 Week": 7, "2 Weeks": 14, "1 Month": 30, "3 Months": 90}.get(duration, custom_days if duration == "Custom" else 14)
                    prompt = f"""Create a detailed {days}-day study plan for {subject}.
Goals: {goals}
Study hours per day: {study_hours}
Intensity: {intensity}

Return a structured markdown plan with:
- Daily breakdown (Day 1, Day 2, etc.)
- Topics to cover each day
- Recommended resources
- Review sessions
- Practice exercises
- Weekly milestones

Format with clear headers, bullet points, and emojis."""

                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.5, max_tokens=4096)
                    st.session_state.generated_plan = r
                    st.rerun()
            else:
                st.warning("Please enter a subject and goals.")

    with right:
        st.markdown("#### Your Study Plan")
        if st.session_state.generated_plan:
            st.markdown(f'<div class="summary-output">{st.session_state.generated_plan}</div>', unsafe_allow_html=True)
            copy_to_clipboard(st.session_state.generated_plan, "Copy Plan")
            st.download_button("⬇️ Download Plan", st.session_state.generated_plan,
                             file_name=f"study_plan_{datetime.now().strftime('%Y%m%d')}.md",
                             mime="text/markdown")
        else:
            render_empty_state("📅", "No Plan Yet", "Fill in the details and generate your personalized study plan!")


# ============================================================
# NEW FEATURE 2: MIND MAP GENERATOR
# ============================================================
if st.session_state.current_page == "Mind Map":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Mind_Map", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>🧠 AI Mind Map Generator</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Generate visual concept maps from any topic.</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Generate Mind Map")
        topic = st.text_input("Topic:", placeholder="e.g., Photosynthesis, French Revolution, Machine Learning")
        depth = st.slider("Depth:", 2, 5, 3)

        if st.button("✨ Generate Mind Map", use_container_width=True, type="primary"):
            if topic:
                with st.spinner("Generating mind map..."):
                    prompt = f"""Generate a hierarchical mind map for: "{topic}"
Return ONLY JSON in this exact format:
{{
  "central": "Main Topic",
  "branches": [
    {{
      "name": "Branch 1",
      "sub_branches": ["Sub 1", "Sub 2", "Sub 3"]
    }},
    {{
      "name": "Branch 2",
      "sub_branches": ["Sub 1", "Sub 2"]
    }}
  ]
}}

Generate {depth} levels of depth with 3-5 branches at each level."""

                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.3,
                                 max_tokens=2048, response_format={"type": "json_object"})
                    try:
                        if not r.startswith("API"):
                            js = r.split("```json")[-1].split("```")[0] if "```" in r else r
                            data = json.loads(js)
                            st.session_state.mind_map_data = data
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)[:80]}")
                        st.code(r[:500])
            else:
                st.warning("Enter a topic.")

    with right:
        st.markdown("#### Mind Map")
        if st.session_state.mind_map_data:
            data = st.session_state.mind_map_data

            # Render mind map as HTML
            html = f"""
            <div class="mind-map-container">
                <div style="text-align:center;margin-bottom:24px;">
                    <div class="mind-map-node" style="font-size:1.2rem;padding:14px 28px;">
                        🎯 {data.get('central', 'Topic')}
                    </div>
                </div>
            """

            for branch in data.get('branches', []):
                html += f"""
                <div style="margin:16px 0;">
                    <div class="mind-map-node">{branch.get('name', '')}</div>
                    <div style="margin-top:8px;">
                """
                for sub in branch.get('sub_branches', []):
                    html += f'<div class="mind-map-branch">{sub}</div>'
                html += "</div></div>"

            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

            # Export options
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            copy_to_clipboard(json.dumps(data, indent=2), "Copy JSON")
        else:
            render_empty_state("🧠", "No Mind Map Yet", "Enter a topic and generate a visual concept map!")


# ============================================================
# NEW FEATURE 3: ESSAY GRADER
# ============================================================
if st.session_state.current_page == "Essay Grader":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Essay_Grader", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>📝 AI Essay Grader</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Get detailed feedback on your essays and writing.</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Submit Essay")
        essay_title = st.text_input("Essay Title:", placeholder="e.g., The Impact of Climate Change")
        essay_text = st.text_area("Essay:", value=st.session_state.essay_input,
                                   placeholder="Paste your essay here...", height=300, key="essay_text")

        col1, col2 = st.columns(2)
        with col1:
            essay_type = st.selectbox("Type:", ["Academic", "Creative", "Argumentative", "Expository", "Narrative"])
        with col2:
            grade_level = st.selectbox("Level:", ["Middle School", "High School", "Undergraduate", "Graduate", "Professional"])

        if st.button("🎯 Grade Essay", use_container_width=True, type="primary"):
            if essay_text.strip():
                st.session_state.essay_input = essay_text
                with st.spinner("Analyzing your essay..."):
                    prompt = f"""You are an expert writing instructor. Grade and provide detailed feedback on this {essay_type.lower()} essay written at a {grade_level.lower()} level.

Essay Title: {essay_title}

Essay:
{essay_text[:5000]}

Provide feedback in this format:

## Overall Score: X/100

## Strengths
- [List strengths]

## Areas for Improvement
- [List improvements]

## Grammar & Mechanics
- [Grammar issues]

## Structure & Organization
- [Structure feedback]

## Argument/Content Quality
- [Content feedback]

## Suggested Revisions
- [Specific suggestions]

## Final Comments
[Encouraging closing remarks]"""

                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.4, max_tokens=4096)
                    st.session_state.essay_feedback = r
                    st.rerun()
            else:
                st.warning("Please enter an essay to grade.")

    with right:
        st.markdown("#### Feedback")
        if st.session_state.essay_feedback:
            st.markdown(f'<div class="summary-output">{st.session_state.essay_feedback}</div>', unsafe_allow_html=True)
            copy_to_clipboard(st.session_state.essay_feedback, "Copy Feedback")
            st.download_button("⬇️ Download Feedback", st.session_state.essay_feedback,
                             file_name=f"essay_feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                             mime="text/markdown")
        else:
            render_empty_state("📊", "Feedback Appears Here", "Submit your essay for AI-powered grading and feedback!")


# ============================================================
# NEW FEATURE 4: CITATION GENERATOR
# ============================================================
if st.session_state.current_page == "Citation Gen":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Citation_Gen", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>📖 AI Citation Generator</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Generate proper citations in any format.</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Citation Details")
        citation_type = st.selectbox("Format:", ["APA 7th", "MLA 9th", "Chicago", "Harvard", "IEEE", "BibTeX"])
        source_type = st.selectbox("Source:", ["Book", "Journal Article", "Website", "Video", "Podcast", "Conference Paper", "Thesis"])

        with st.expander("Enter Details", expanded=True):
            title = st.text_input("Title:", placeholder="Title of the work")
            author = st.text_input("Author(s):", placeholder="e.g., Smith, J. D.")
            year = st.text_input("Year:", placeholder="2024")

            if source_type in ["Book", "Journal Article", "Conference Paper"]:
                publisher = st.text_input("Publisher/Journal:", placeholder="e.g., Nature, ACM")

            if source_type == "Website":
                url = st.text_input("URL:", placeholder="https://...")
                access_date = st.text_input("Access Date:", placeholder="2024-06-29")

            if source_type == "Journal Article":
                volume = st.text_input("Volume:", placeholder="12")
                issue = st.text_input("Issue:", placeholder="3")
                pages = st.text_input("Pages:", placeholder="45-67")

        if st.button("✨ Generate Citation", use_container_width=True, type="primary"):
            if title and author and year:
                with st.spinner("Generating citation..."):
                    prompt = f"""Generate a {citation_type} citation for this {source_type.lower()}:

Title: {title}
Author(s): {author}
Year: {year}
"""
                    if source_type in ["Book", "Journal Article", "Conference Paper"]:
                        prompt += f"Publisher/Journal: {publisher}\n"
                    if source_type == "Website":
                        prompt += f"URL: {url}\nAccess Date: {access_date}\n"
                    if source_type == "Journal Article":
                        prompt += f"Volume: {volume}\nIssue: {issue}\nPages: {pages}\n"

                    prompt += f"""
Return ONLY the properly formatted citation. No extra text."""

                    r = call_groq(messages=[{"role": "user", "content": prompt}],
                                 model=st.session_state.selected_model, temperature=0.2, max_tokens=512)
                    st.session_state.citation_result = r.strip()
                    st.rerun()
            else:
                st.warning("Please fill in at least title, author, and year.")

    with right:
        st.markdown("#### Citation")
        if st.session_state.citation_result:
            st.markdown(f"""
                <div style="background:rgba(20,22,38,0.5);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;font-family:monospace;font-size:0.9rem;color:#e2e8f0;line-height:1.6;">
                    {st.session_state.citation_result}
                </div>
            """, unsafe_allow_html=True)
            copy_to_clipboard(st.session_state.citation_result, "Copy Citation")
        else:
            render_empty_state("📖", "Citation Appears Here", "Fill in the details to generate a properly formatted citation!")


# ============================================================
# NEW FEATURE 5: COLLABORATIVE STUDY ROOM
# ============================================================
if st.session_state.current_page == "Collab Room":

    # Back to Dashboard button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Dashboard", key="back_btn_Collab_Room", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='glass-card' style='margin-bottom:20px;'>
        <h3 style='margin:0 0 6px 0;'>🤝 Collaborative Study Room</h3>
        <p style='color:#64748b;margin:0;font-size:0.9rem;'>Simulated study group with AI-powered discussion.</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Room Settings")
        room_id = st.text_input("Room ID:", value=st.session_state.collab_room_id or f"room-{random.randint(1000,9999)}", placeholder="Enter room ID")
        st.session_state.collab_room_id = room_id

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 💡 AI Study Partner")
        ai_topic = st.text_input("Topic to discuss:", placeholder="e.g., Quantum Mechanics")
        ai_role = st.selectbox("AI Role:", ["SENORA", "Devil's Advocate", "Tutor", "Quiz Master", "Skeptic"])

        if st.button("🤖 Ask AI Partner", use_container_width=True, type="primary"):
            if ai_topic:
                with st.spinner("AI is thinking..."):
                    role_prompts = {
                        "SENORA": f"You are a friendly SENORA discussing {ai_topic}. Be encouraging, ask thought-provoking questions, and share insights.",
                        "Devil's Advocate": f"You are playing devil's advocate on {ai_topic}. Challenge assumptions and present counterarguments to deepen understanding.",
                        "Tutor": f"You are an expert tutor explaining {ai_topic}. Break down complex concepts and check for understanding.",
                        "Quiz Master": f"You are a quiz master testing knowledge on {ai_topic}. Ask challenging questions and provide explanations.",
                        "Skeptic": f"You are a skeptical reviewer of {ai_topic}. Question the validity of claims and ask for evidence.",
                    }

                    messages = [
                        {"role": "system", "content": role_prompts[ai_role]},
                        {"role": "user", "content": f"Let's discuss {ai_topic}. Start with an engaging question or insight."}
                    ]

                    r = call_groq(messages=messages, model=st.session_state.selected_model, temperature=0.7, max_tokens=1024)
                    st.session_state.collab_messages.append({
                        "role": "ai",
                        "content": r,
                        "avatar": "🤖",
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            else:
                st.warning("Enter a topic.")

    with right:
        st.markdown(f"#### 💬 Room: {st.session_state.collab_room_id}")

        # Display messages
        if not st.session_state.collab_messages:
            render_empty_state("🤝", "Empty Room", "Start a discussion with the AI study partner or add your own thoughts!")
        else:
            for msg in st.session_state.collab_messages:
                cls = "collab-message-user" if msg["role"] == "user" else "collab-message-other"
                st.markdown(f"""
                    <div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;">
                        <span style="font-size:1.2rem;">{msg['avatar']}</span>
                        <div class="collab-message {cls}">
                            <div style="font-size:0.75rem;color:#64748b;margin-bottom:4px;">{msg['time']}</div>
                            {msg['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # User input
        user_msg = st.text_input("Your message:", placeholder="Share your thoughts...", key="collab_input")
        if st.button("💬 Send", use_container_width=True):
            if user_msg.strip():
                st.session_state.collab_messages.append({
                    "role": "user",
                    "content": user_msg,
                    "avatar": "👤",
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
    <p style="text-align:center;color:#475569;font-size:0.75rem;">
        SENORA v4.0 | Powered by Groq API + Streamlit
    </p>
""", unsafe_allow_html=True)    