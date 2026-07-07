"""
Essay Grader — AI-powered essay feedback and scoring.
"""

from datetime import datetime

import streamlit as st

from api import call_groq
from components import page_header, empty_state, copy_button


def render() -> None:
    page_header("📝", "AI Essay Grader",
                "Get detailed feedback on your essays and writing.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Submit Essay")
        essay_title = st.text_input("Essay Title:",
                                    placeholder="e.g., The Impact of Climate Change",
                                    key="essay_title")
        essay_text = st.text_area("Essay:", value=st.session_state.essay_input,
                                  placeholder="Paste your essay here...",
                                  height=300, key="essay_text_input")

        ec1, ec2 = st.columns(2)
        with ec1:
            essay_type = st.selectbox(
                "Type:",
                ["Academic", "Creative", "Argumentative", "Expository", "Narrative"],
                key="essay_type",
            )
        with ec2:
            grade_level = st.selectbox(
                "Level:",
                ["Middle School", "High School", "Undergraduate", "Graduate", "Professional"],
                key="essay_level",
            )

        if st.button("🎯 Grade Essay", use_container_width=True, type="primary",
                     key="grade_essay"):
            if essay_text and essay_text.strip():
                st.session_state.essay_input = essay_text
                with st.spinner("Analyzing your essay..."):
                    prompt = (
                        f"You are an expert writing instructor. "
                        f"Grade and provide detailed feedback on this "
                        f"{essay_type.lower()} essay written at a "
                        f"{grade_level.lower()} level.\n\n"
                        f"Essay Title: {essay_title}\n\n"
                        f"Essay:\n{essay_text[:5000]}\n\n"
                        "Provide feedback in this format:\n\n"
                        "## Overall Score: X/100\n\n"
                        "## Strengths\n- [List strengths]\n\n"
                        "## Areas for Improvement\n- [List improvements]\n\n"
                        "## Grammar & Mechanics\n- [Grammar issues]\n\n"
                        "## Structure & Organization\n- [Structure feedback]\n\n"
                        "## Argument/Content Quality\n- [Content feedback]\n\n"
                        "## Suggested Revisions\n- [Specific suggestions]\n\n"
                        "## Final Comments\n[Encouraging closing remarks]"
                    )
                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.4, max_tokens=4096,
                    )
                    st.session_state.essay_feedback = r
                    st.rerun()
            else:
                st.warning("Please enter an essay to grade.")

    with col_right:
        st.markdown("#### Feedback")
        if st.session_state.essay_feedback:
            st.markdown(st.session_state.essay_feedback)
            copy_button(st.session_state.essay_feedback, "Copy Feedback")
            st.download_button(
                "⬇️ Download Feedback",
                st.session_state.essay_feedback,
                file_name=f"essay_feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
            )
        else:
            empty_state("📊", "Feedback Appears Here",
                        "Submit your essay for AI-powered grading and feedback!")
