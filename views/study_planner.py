from datetime import datetime

import streamlit as st

from api import call_groq
from components import page_header, empty_state, copy_button


def render() -> None:
    page_header("📅", "AI Study Planner",
                "Generate a personalized study schedule with AI.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Plan Settings")
        subject = st.text_input("Subject:", value=st.session_state.study_subject,
                                placeholder="e.g., Organic Chemistry",
                                key="planner_subject")
        duration_opt = st.selectbox(
            "Duration:",
            ["1 Week", "2 Weeks", "1 Month", "3 Months", "Custom"],
            key="planner_duration",
        )
        custom_days = 14
        if duration_opt == "Custom":
            custom_days = st.number_input("Days:", min_value=1, max_value=365,
                                          value=14, key="planner_custom_days")

        goals = st.text_area(
            "Goals:",
            placeholder="What do you want to achieve? e.g., Pass midterm...",
            height=80, key="planner_goals",
        )

        sc1, sc2 = st.columns(2)
        with sc1:
            study_hours = st.slider("Hours/day:", 1, 8, 2, key="planner_hours")
        with sc2:
            intensity = st.select_slider("Intensity:",
                                         ["Relaxed", "Moderate", "Intense"],
                                         key="planner_intensity")

        if st.button("✨ Generate Plan", use_container_width=True, type="primary",
                     key="gen_plan"):
            if subject and goals:
                days = {
                    "1 Week": 7, "2 Weeks": 14, "1 Month": 30, "3 Months": 90,
                }.get(duration_opt, custom_days)

                with st.spinner("Creating your personalized study plan..."):
                    prompt = (
                        f"Create a detailed {days}-day study plan for {subject}.\n"
                        f"Goals: {goals}\n"
                        f"Study hours per day: {study_hours}\n"
                        f"Intensity: {intensity}\n\n"
                        "Return a structured markdown plan with:\n"
                        "- Daily breakdown (Day 1, Day 2, etc.)\n"
                        "- Topics to cover each day\n"
                        "- Recommended resources\n"
                        "- Review sessions\n"
                        "- Practice exercises\n"
                        "- Weekly milestones\n\n"
                        "Format with clear headers, bullet points, and emojis."
                    )
                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.5, max_tokens=4096,
                    )
                    st.session_state.generated_plan = r
                    st.rerun()
            else:
                st.warning("Please enter a subject and goals.")

    with col_right:
        st.markdown("#### Your Study Plan")
        if st.session_state.generated_plan:
            st.markdown(st.session_state.generated_plan)
            copy_button(st.session_state.generated_plan, "Copy Plan")
            st.download_button(
                "⬇️ Download Plan",
                st.session_state.generated_plan,
                file_name=f"study_plan_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
            )
        else:
            empty_state("📅", "No Plan Yet",
                        "Fill in the details and generate your personalized study plan!")
