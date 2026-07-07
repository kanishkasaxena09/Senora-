"""
Reusable UI components for SENORA.
"""

import html as html_lib
import math

import streamlit as st


# ── Page header ─────────────────────────────────────────────────
def page_header(icon: str, title: str, subtitle: str) -> None:
    """Render a glassmorphism page header card."""
    st.markdown(
        f"""<div class='glass-card' style='margin-bottom:20px;'>
            <h3 style='margin:0 0 6px 0;'>{icon} {title}</h3>
            <p style='color:#64748b;margin:0;font-size:0.9rem;'>{subtitle}</p>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Stat card ───────────────────────────────────────────────────
def stat_card(icon: str, title: str, value, subtitle: str = "") -> None:
    """Render a dashboard stat card."""
    st.markdown(
        f"""<div class="dashboard-card">
            <span class="dashboard-card-icon">{icon}</span>
            <div class="dashboard-card-title">{title}</div>
            <div class="dashboard-card-value">{value}</div>
            <div class="dashboard-card-subtitle">{subtitle}</div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Empty state ─────────────────────────────────────────────────
def empty_state(icon: str, title: str, subtitle: str) -> None:
    """Render a centered empty-state placeholder."""
    st.markdown(
        f"""<div class="empty-state-box">
            <span class="empty-state-icon">{icon}</span>
            <h3 style="color:#f1f5f9;margin-bottom:8px;font-weight:700;">{title}</h3>
            <p style="color:#64748b;font-size:0.95rem;">{subtitle}</p>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Copy to clipboard (XSS-safe) ───────────────────────────────
def copy_button(text: str, label: str = "Copy") -> None:
    """Render a small copy-to-clipboard button. Escapes for both HTML and JS."""
    # Escape HTML entities first, then escape backticks and ${} for JS template
    safe = html_lib.escape(text)
    safe = safe.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    st.markdown(
        f"""<button onclick="navigator.clipboard.writeText(`{safe}`);\
this.textContent='✅ Copied!';setTimeout(()=>this.textContent='📋 {label}',1500)"
            style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
            border-radius:10px;padding:6px 14px;color:#94a3b8;font-size:0.8rem;
            cursor:pointer;transition:all 0.2s;"
            onmouseover="this.style.background='rgba(255,255,255,0.1)'"
            onmouseout="this.style.background='rgba(255,255,255,0.05)'"
            aria-label="Copy to clipboard">
            📋 {label}
        </button>""",
        unsafe_allow_html=True,
    )


# ── Word count ──────────────────────────────────────────────────
def word_count(text: str) -> int:
    return len(text.split()) if text and text.strip() else 0


# ── Spacer ──────────────────────────────────────────────────────
def spacer(px: int = 16) -> None:
    st.markdown(f"<div style='height:{px}px;'></div>", unsafe_allow_html=True)


# ── 3D flashcard ────────────────────────────────────────────────
def render_flashcard(front: str, back: str, flipped: bool) -> None:
    """Render a 3D-flip flashcard using CSS transforms."""
    flip_class = "flipped" if flipped else ""
    safe_front = html_lib.escape(front)
    safe_back = html_lib.escape(back)
    st.markdown(
        f"""<div class="flashcard-container">
            <div class="flashcard-inner {flip_class}">
                <div class="flashcard-front-3d">
                    <div>
                        <div style="font-size:0.75rem;opacity:0.6;margin-bottom:10px;
                            font-weight:700;letter-spacing:0.08em;">QUESTION</div>
                        <div style="font-weight:600;font-size:1.2rem;">{safe_front}</div>
                    </div>
                </div>
                <div class="flashcard-back-3d">
                    <div>
                        <div style="font-size:0.75rem;opacity:0.6;margin-bottom:10px;
                            font-weight:700;letter-spacing:0.08em;">ANSWER</div>
                        <div style="font-weight:500;font-size:1.1rem;">{safe_back}</div>
                    </div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── SVG timer ring ──────────────────────────────────────────────
def render_timer_ring(
    remaining_seconds: float,
    total_seconds: float,
    label: str = "Focus",
) -> None:
    """Render a circular SVG timer with a gradient ring."""
    progress = 1 - (remaining_seconds / total_seconds) if total_seconds > 0 else 0
    progress = max(0.0, min(1.0, progress))

    mins, secs = divmod(int(max(0, remaining_seconds)), 60)
    time_str = f"{mins:02d}:{secs:02d}"

    radius = 110
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - progress)

    st.markdown(
        f"""<div class="timer-ring-container">
            <svg class="timer-ring-svg" width="260" height="260" role="img"
                 aria-label="Timer showing {time_str}">
                <defs>
                    <linearGradient id="timerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#6d5bf6"/>
                        <stop offset="100%" style="stop-color:#14b8a6"/>
                    </linearGradient>
                </defs>
                <circle class="timer-ring-bg" cx="130" cy="130" r="{radius}"/>
                <circle class="timer-ring-progress" cx="130" cy="130" r="{radius}"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke="url(#timerGrad)"/>
            </svg>
            <div class="timer-ring-text">{time_str}</div>
            <div class="timer-ring-label">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Progress badge row ──────────────────────────────────────────
def flashcard_badges(easy: int, new: int, hard: int) -> None:
    """Render Easy / New / Hard badge row."""
    st.markdown(
        f"""<div style="display:flex;justify-content:center;gap:14px;margin-top:20px;">
            <span class="badge-easy">✅ Easy {easy}</span>
            <span class="badge-new">🆕 New {new}</span>
            <span class="badge-hard">❌ Hard {hard}</span>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Progress bar row for dashboard ──────────────────────────────
def progress_bar(label: str, percent: float, color_start: str, color_end: str, icon: str = "") -> None:
    """Render a custom styled progress bar."""
    st.markdown(
        f"""<div style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:{color_end};font-size:0.8rem;">{icon} {label}</span>
                <span style="color:{color_end};font-size:0.8rem;font-weight:600;">{percent:.0f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:8px;height:8px;overflow:hidden;">
                <div style="background:linear-gradient(90deg,{color_start},{color_end});
                    height:100%;width:{percent}%;border-radius:8px;transition:width 0.5s ease;"></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
