"""
SENORA — Global CSS injection.

Call ``inject_css()`` once at the top of app.py.
"""

import streamlit as st

_CSS = """
<style>
/* ─── FONTS ─── */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-0: #05060a;
    --bg-1: #0a0c14;
    --surface: rgba(22, 24, 38, 0.62);
    --surface-soft: rgba(22, 24, 38, 0.42);
    --border: rgba(255,255,255,0.07);
    --border-strong: rgba(255,255,255,0.14);
    --text-hi: #f4f6fb;
    --text-mid: #aab2c5;
    --text-lo: #6b7386;
    --accent-1: #6d5bf6;
    --accent-2: #14b8a6;
    --accent-3: #f0b429;
    --accent-grad: linear-gradient(135deg, #6d5bf6 0%, #4f8ef7 55%, #14b8a6 100%);
    --radius-lg: 22px;
    --radius-md: 16px;
    --radius-sm: 12px;
}

* { font-family: 'Inter', -apple-system, sans-serif !important; }

.main .block-container {
    padding: 0 2.2rem 4rem 2.2rem;
    max-width: 1360px;
}

/* ─── BACKGROUND ─── */
.stApp {
    background:
        radial-gradient(ellipse 60% 45% at 12% 8%, rgba(109, 91, 246, 0.16) 0%, transparent 60%),
        radial-gradient(ellipse 55% 45% at 90% 12%, rgba(20, 184, 166, 0.12) 0%, transparent 60%),
        radial-gradient(ellipse 70% 55% at 50% 100%, rgba(79, 142, 247, 0.08) 0%, transparent 65%),
        linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 55%, var(--bg-0) 100%);
    background-attachment: fixed;
}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08090f 0%, #0c0e17 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container {
    background: transparent;
    padding: 1.3rem 1.1rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-hi) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label { color: var(--text-mid) !important; }
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption { color: var(--text-lo) !important; }

/* ─── HEADINGS ─── */
h1, h2, h3 { font-family: 'Sora', sans-serif !important; }
h1 {
    color: var(--text-hi) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    font-size: 2.3rem !important;
    line-height: 1.15 !important;
}
h2 {
    color: #eef1f8 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    font-size: 1.35rem !important;
    line-height: 1.25 !important;
}
h3 {
    color: #dde2ef !important;
    font-weight: 600 !important;
    font-size: 1.08rem !important;
    line-height: 1.3 !important;
}
p, .stMarkdown, label { line-height: 1.65; }

/* ─── GLASS CARDS ─── */
.glass-card {
    background: var(--surface);
    backdrop-filter: blur(22px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 30px 32px;
    position: relative;
    transition: all 0.45s cubic-bezier(0.23, 1, 0.32, 1);
    box-shadow: 0 10px 34px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.04);
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.16), transparent);
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 22px 50px rgba(0,0,0,0.36), 0 0 28px rgba(109,91,246,0.10),
                inset 0 1px 0 rgba(255,255,255,0.06);
    border-color: rgba(109,91,246,0.22);
}

/* ─── DASHBOARD CARDS ─── */
.dashboard-card {
    background: var(--surface);
    backdrop-filter: blur(22px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 22px 24px;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    box-shadow: 0 8px 28px rgba(0,0,0,0.28);
    position: relative;
    overflow: hidden;
}
.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.13), transparent);
}
.dashboard-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 44px rgba(0,0,0,0.36), 0 0 22px rgba(20,184,166,0.10);
    border-color: rgba(20,184,166,0.22);
}
.dashboard-card-icon { font-size: 1.9rem; margin-bottom: 10px; display: block; }
.dashboard-card-title { color: var(--text-hi); font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; }
.dashboard-card-value {
    font-family: 'Sora', sans-serif;
    color: var(--text-hi);
    font-weight: 800;
    font-size: 1.9rem;
    letter-spacing: -0.03em;
}
.dashboard-card-subtitle { color: var(--text-lo); font-size: 0.78rem; margin-top: 4px; }

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
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
    font-size: 1.2rem;
    line-height: 1.7;
    padding: 40px;
    box-shadow: 0 20px 55px rgba(0,0,0,0.4);
}
.flashcard-front-3d {
    background: linear-gradient(135deg, #5b4bd6 0%, #6d5bf6 50%, #4f8ef7 100%);
    border: 1px solid rgba(255,255,255,0.1);
}
.flashcard-back-3d {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 50%, #2dd4bf 100%);
    border: 1px solid rgba(255,255,255,0.1);
    transform: rotateY(180deg);
}

/* ─── BUTTONS ─── */
.stButton > button {
    background: var(--accent-grad) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
    font-size: 0.88rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 16px rgba(109, 91, 246, 0.28) !important;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 26px rgba(109, 91, 246, 0.42) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.98) !important; }
.stButton > button:focus-visible {
    outline: 2px solid #a78bfa !important;
    outline-offset: 2px !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.045) !important;
    color: var(--text-mid) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: var(--text-hi) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent-grad) !important;
}

/* ─── SIDEBAR NAV BUTTONS ─── */
[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    border-radius: var(--radius-sm) !important;
    margin-bottom: 2px !important;
    transition: all 0.25s cubic-bezier(0.23, 1, 0.32, 1) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    border-left: 2px solid transparent !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    transform: translateX(3px) !important;
    border-left: 2px solid rgba(109,91,246,0.55) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    border-left: 2px solid #b7aefc !important;
    box-shadow: 0 4px 18px rgba(109, 91, 246, 0.32) !important;
}

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(9, 10, 18, 0.82) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: #e7eaf3 !important;
    font-size: 0.94rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 4px rgba(109, 91, 246, 0.14), 0 0 20px rgba(109, 91, 246, 0.06) !important;
}

/* ─── SELECTS ─── */
.stSelectbox > div > div,
.stSelectSlider > div > div {
    background: rgba(9, 10, 18, 0.82) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: #e7eaf3 !important;
}

/* ─── SLIDER ─── */
.stSlider > div > div > div > div {
    background: var(--accent-grad) !important;
    border-radius: 6px !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(9, 10, 18, 0.55) !important;
    border-radius: var(--radius-lg) !important;
    padding: 6px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-lo) !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    border: none !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-hi) !important;
    background: rgba(255,255,255,0.03) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-grad) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(109, 91, 246, 0.32) !important;
}

/* ─── EXPANDER ─── */
.streamlit-expanderHeader {
    background: var(--surface-soft) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 14px 18px !important;
    font-weight: 600 !important;
    color: #dde2ef !important;
    transition: all 0.25s ease !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(22, 24, 38, 0.7) !important;
    border-color: rgba(109,91,246,0.18) !important;
}
.streamlit-expanderContent {
    background: rgba(22, 24, 38, 0.32) !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    padding: 18px !important;
}

/* ─── CHAT MESSAGES ─── */
.chat-message-user {
    background: var(--accent-grad);
    color: white;
    padding: 14px 22px;
    border-radius: 20px 20px 4px 20px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 8px 24px rgba(109, 91, 246, 0.24);
    animation: slideInRight 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    word-wrap: break-word;
}
.chat-message-assistant {
    background: rgba(22, 24, 38, 0.82);
    backdrop-filter: blur(12px);
    color: #e7eaf3;
    padding: 14px 22px;
    border-radius: 20px 20px 20px 4px;
    margin: 10px auto 10px 0;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid var(--border);
    animation: slideInLeft 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    word-wrap: break-word;
}

/* ─── TIMER RING ─── */
.timer-ring-container {
    position: relative;
    width: 260px;
    height: 260px;
    margin: 0 auto;
}
.timer-ring-svg { transform: rotate(-90deg); }
.timer-ring-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 8; }
.timer-ring-progress {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s linear;
    filter: drop-shadow(0 0 8px rgba(20, 184, 166, 0.4));
}
.timer-ring-text {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Sora', sans-serif;
    font-size: 3.1rem;
    font-weight: 800;
    color: #2dd4bf;
    text-shadow: 0 0 30px rgba(20,184,166,0.3);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.04em;
}
.timer-ring-label {
    position: absolute;
    top: 65%; left: 50%;
    transform: translateX(-50%);
    color: var(--text-lo);
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ─── QUIZ ─── */
.quiz-question-box {
    background: linear-gradient(135deg, rgba(109,91,246,0.09), rgba(79,142,247,0.05));
    border: 1px solid rgba(109,91,246,0.14);
    border-left: 4px solid var(--accent-1);
    padding: 24px;
    border-radius: var(--radius-md);
    margin: 16px 0;
    font-size: 1.08rem;
    color: #e7eaf3;
    animation: cardEnter 0.4s ease-out;
}
.explanation-box {
    background: linear-gradient(135deg, rgba(20,184,166,0.09), rgba(45,212,191,0.05));
    border: 1px solid rgba(20,184,166,0.18);
    padding: 18px 24px;
    border-radius: var(--radius-sm);
    margin-top: 14px;
    color: #5eead4;
    font-size: 0.94rem;
    line-height: 1.6;
    animation: slideInLeft 0.3s ease-out;
}
.score-result-box {
    text-align: center;
    padding: 48px 40px;
    background: rgba(22, 24, 38, 0.75);
    backdrop-filter: blur(22px);
    border-radius: 26px;
    border: 1px solid var(--border);
    box-shadow: 0 25px 60px rgba(0,0,0,0.3);
    animation: scaleIn 0.5s cubic-bezier(0.23, 1, 0.32, 1);
}

/* ─── BADGES ─── */
.badge-easy {
    background: linear-gradient(135deg, #0d9488, #14b8a6);
    padding: 6px 16px; border-radius: 24px; color: white;
    font-weight: 700; font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(20, 184, 166, 0.25);
}
.badge-new {
    background: var(--accent-grad);
    padding: 6px 16px; border-radius: 24px; color: white;
    font-weight: 700; font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(109, 91, 246, 0.25);
}
.badge-hard {
    background: linear-gradient(135deg, #dc2626, #f43f5e);
    padding: 6px 16px; border-radius: 24px; color: white;
    font-weight: 700; font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
}

/* ─── PROGRESS BAR ─── */
.stProgress > div > div {
    background: var(--accent-grad) !important;
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
    background: var(--surface-soft);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--radius-sm);
    padding: 12px 8px;
    text-align: center;
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(109,91,246,0.22);
    transform: translateY(-2px);
}
[data-testid="stMetric"] > div:first-child {
    color: var(--text-lo) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetric"] > div:last-child {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-hi) !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
}

/* ─── NOTE CARDS ─── */
.note-tag {
    background: rgba(109, 91, 246, 0.13);
    color: #b7aefc;
    padding: 4px 12px;
    border-radius: 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
    border: 1px solid rgba(109,91,246,0.12);
}

/* ─── MIND MAP ─── */
.mind-map-container {
    background: var(--surface-soft);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 24px;
    min-height: 400px;
    overflow-x: auto;
}
.mind-map-node {
    background: var(--accent-grad);
    color: white;
    padding: 10px 18px;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.9rem;
    display: inline-block;
    margin: 6px;
    box-shadow: 0 4px 12px rgba(109, 91, 246, 0.25);
    transition: all 0.3s ease;
}
.mind-map-node:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(109, 91, 246, 0.4); }
.mind-map-branch {
    background: rgba(109, 91, 246, 0.09);
    border-left: 3px solid var(--accent-1);
    padding: 8px 16px;
    border-radius: 0 10px 10px 0;
    margin: 4px 0 4px 20px;
    color: #dde2ef;
    font-size: 0.85rem;
}

/* ─── SUMMARY OUTPUT ─── */
.summary-output {
    background: var(--surface-soft);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--radius-md);
    padding: 28px;
    min-height: 320px;
    max-height: 600px;
    overflow-y: auto;
    animation: cardEnter 0.4s ease-out;
    line-height: 1.7;
}

/* ─── STREAK BADGE ─── */
.streak-badge {
    background: linear-gradient(135deg, var(--accent-3), #f59e0b);
    padding: 6px 14px; border-radius: 24px; color: #1a1206;
    font-weight: 800; font-size: 0.85rem;
    box-shadow: 0 4px 12px rgba(240, 180, 41, 0.3);
    display: inline-flex; align-items: center; gap: 6px;
}

/* ─── COLLAB ─── */
.collab-message { padding: 10px 16px; border-radius: 14px; margin: 6px 0; font-size: 0.9rem; max-width: 85%; }
.collab-message-user { background: var(--accent-grad); color: white; margin-left: auto; border-radius: 14px 14px 4px 14px; }
.collab-message-other { background: rgba(22, 24, 38, 0.72); color: #e7eaf3; border: 1px solid var(--border); border-radius: 14px 14px 14px 4px; }

/* ─── EMPTY STATE ─── */
.empty-state-box {
    text-align: center;
    padding: 54px 36px;
    background: rgba(22, 24, 38, 0.28);
    border: 2px dashed rgba(255,255,255,0.06);
    border-radius: var(--radius-lg);
    animation: scaleIn 0.4s ease-out;
}
.empty-state-icon {
    font-size: 3.4rem;
    animation: float 4s ease-in-out infinite;
    display: block;
    margin-bottom: 1rem;
}

/* ─── FILE UPLOADER ─── */
.stFileUploader > div > div {
    background: rgba(9, 10, 18, 0.6) !important;
    border: 2px dashed rgba(109, 91, 246, 0.28) !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s ease !important;
}
.stFileUploader > div > div:hover {
    border-color: rgba(109, 91, 246, 0.5) !important;
    background: rgba(109, 91, 246, 0.05) !important;
}

/* ─── ALERTS ─── */
.stAlert { border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; }
.stAlert [data-testid="stAlertContentSuccess"] { background: rgba(20, 184, 166, 0.09) !important; color: #5eead4 !important; }
.stAlert [data-testid="stAlertContentInfo"] { background: rgba(79, 142, 247, 0.09) !important; color: #93c5fd !important; }
.stAlert [data-testid="stAlertContentWarning"] { background: rgba(240, 180, 41, 0.09) !important; color: #fde68a !important; }
.stAlert [data-testid="stAlertContentError"] { background: rgba(220, 38, 38, 0.09) !important; color: #fca5a5 !important; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-0); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6d5bf6, #14b8a6); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #8577f9, #2dd4bf); }

/* ─── HIDE BRANDING ─── */
#MainMenu, footer { visibility: hidden; }
header { visibility: visible !important; }
.stDeployButton { display: none !important; }

/* ─── DIVIDER / SPINNER ─── */
hr { border-color: rgba(255,255,255,0.05) !important; margin: 1.5rem 0 !important; }
.stSpinner > div { border-color: var(--accent-1) transparent transparent transparent !important; }

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
@keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
}
@keyframes pageEnter {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.main .block-container { animation: pageEnter 0.45s cubic-bezier(0.23, 1, 0.32, 1); }

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    .main .block-container { padding: 0 1rem 2rem 1rem !important; }
    .glass-card { padding: 20px; border-radius: 18px; }
    .dashboard-card { padding: 18px; border-radius: 16px; }
    .dashboard-card-value { font-size: 1.5rem; }
    h1 { font-size: 1.8rem !important; }
    .timer-ring-container { width: 200px; height: 200px; }
    .timer-ring-text { font-size: 2.4rem; }
}
</style>
"""


def inject_css() -> None:
    """Inject the global CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)
