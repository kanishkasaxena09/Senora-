"""
Focus Timer — Pomodoro technique with visual SVG ring timer.

Uses a short 1-second ``time.sleep`` + ``st.rerun()`` cycle while running.
This is the standard Streamlit approach for a live timer without extra
dependencies.  The sleep is kept minimal to reduce blocking.
"""

import time
from datetime import datetime, timedelta

import streamlit as st

from components import page_header, render_timer_ring, spacer

_DURATION_MAP = {
    "Pomodoro (25 min)": 1500,
    "Short Break (5 min)": 300,
    "Long Break (15 min)": 900,
}


def render() -> None:
    page_header("⏱️", "Focus Timer",
                "Pomodoro technique with visual ring timer.")

    col_left, col_right = st.columns(2)

    # ── Settings ──
    with col_left:
        st.markdown("#### Settings")
        mode = st.selectbox("Mode:", list(_DURATION_MAP.keys()) + ["Custom"],
                            key="timer_mode_select")

        if mode == "Custom":
            custom_min = st.number_input("Minutes:", min_value=1, max_value=120,
                                         value=25, key="timer_custom")
            duration = custom_min * 60
        else:
            duration = _DURATION_MAP[mode]

        st.session_state.timer_mode = mode

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if st.button("▶ Start", use_container_width=True, type="primary",
                         key="timer_start"):
                st.session_state.timer_running = True
                st.session_state.timer_end = datetime.now() + timedelta(seconds=duration)
                st.rerun()
        with bc2:
            if st.button("⏸ Pause", use_container_width=True, key="timer_pause"):
                st.session_state.timer_running = False
                st.rerun()
        with bc3:
            if st.button("↺ Reset", use_container_width=True, key="timer_reset"):
                st.session_state.timer_running = False
                st.session_state.timer_end = None
                st.rerun()

        st.markdown("---")
        st.markdown(f"**Completed:** {st.session_state.timer_sessions} sessions")
        st.markdown(f"**Total time:** {st.session_state.total_study_time // 60}m")

        with st.expander("💡 Focus Tips"):
            st.markdown(
                "- **Single-task** — Focus on ONE thing\n"
                "- **No phone** — Eliminate distractions\n"
                "- **Plan ahead** — Know your goal before starting\n"
                "- **Hydrate** — Keep water nearby\n"
                "- **Move** — Stretch during breaks"
            )

    # ── Timer display ──
    with col_right:
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
                    "mode": mode, "date": datetime.now().isoformat(),
                    "duration": duration,
                })
                st.balloons()
                st.success("🎉 Session complete! Great work!")
        else:
            remaining = duration

        label = mode.split("(")[0].strip() if "(" in mode else mode
        render_timer_ring(remaining, duration, label)

        if st.session_state.timer_running:
            st.info("🔥 Stay focused!")
        else:
            st.warning("⏸ Paused — Ready when you are")

    # ── Session history ──
    if st.session_state.session_history:
        st.markdown("---")
        st.markdown("#### Recent Sessions")
        for s in reversed(st.session_state.session_history[-5:]):
            st.markdown(
                f"<span style='color:#64748b;font-size:0.8rem;'>"
                f"⏱ {s.get('mode', '?')} — {s.get('date', '')[:10]} "
                f"{s.get('date', '')[11:16]}</span>",
                unsafe_allow_html=True,
            )

    # ── Auto-refresh while running ──
    if st.session_state.timer_running and remaining > 0:
        time.sleep(1)
        st.rerun()
