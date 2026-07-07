import streamlit as st

from api import call_groq, parse_json_response
from components import page_header, empty_state


def render() -> None:
    page_header("📝", "AI Quiz Generator",
                "Test your knowledge with AI-generated quizzes.")

    col_gen, col_quiz = st.columns([1, 2])

    # ── Left: Generate ──
    with col_gen:
        st.markdown("#### Generate")
        quiz_topic = st.text_area("Topic/Notes:",
                                  placeholder="Paste notes or describe a topic...",
                                  height=130, key="quiz_topic_input")
        num_q = st.slider("Questions:", 3, 10, 5, key="quiz_num")
        difficulty = st.select_slider("Difficulty:", ["Easy", "Medium", "Hard"],
                                      value="Medium", key="quiz_diff")

        if st.button("🎯 Generate", use_container_width=True, type="primary",
                     key="quiz_generate"):
            if quiz_topic and quiz_topic.strip():
                with st.spinner("Creating..."):
                    prompt = (
                        f"Generate a {difficulty.lower()} quiz with {num_q} MCQs. "
                        "Return ONLY JSON:\n"
                        '{"questions":[{"question":"...","options":["a","b","c","d"],'
                        '"correct":0,"explanation":"..."}]}\n\n'
                        f"Content: {quiz_topic[:4000]}"
                    )
                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.3, max_tokens=4096,
                        response_format={"type": "json_object"},
                    )
                    data = parse_json_response(r)
                    if data and isinstance(data, dict):
                        questions = data.get("questions", [])
                        if questions:
                            st.session_state.quiz_questions = questions
                            st.session_state.current_quiz_idx = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_answered = False
                            st.session_state.quiz_selected = None
                            st.toast(f"✅ Generated {len(questions)} questions!")
                            st.rerun()
                        else:
                            st.error("No questions found in response.")
                    else:
                        st.error("Failed to parse AI response.")
                        st.code(r[:500])
            else:
                st.warning("Enter a topic or paste notes.")

    # ── Right: Take quiz ──
    with col_quiz:
        st.markdown("#### Take Quiz")
        qs = st.session_state.quiz_questions
        if not qs:
            empty_state("🎯", "No Quiz Yet", "Generate one on the left to start!")
            return

        idx = st.session_state.current_quiz_idx
        if idx < len(qs):
            q = qs[idx]
            st.progress(idx / len(qs), text=f"Q{idx + 1} of {len(qs)}")
            st.markdown(f"**Score: {st.session_state.quiz_score}/{len(qs)}**")
            st.markdown(
                f'<div class="quiz-question-box"><strong>Q{idx + 1}:</strong> '
                f'{q["question"]}</div>',
                unsafe_allow_html=True,
            )

            options = q.get("options", [])
            correct = q.get("correct", 0)

            for i, opt in enumerate(options):
                label = chr(65 + i)
                if st.session_state.quiz_answered:
                    if i == correct:
                        st.success(f"✅ {label}. {opt}")
                    elif i == st.session_state.quiz_selected and i != correct:
                        st.error(f"❌ {label}. {opt}")
                    else:
                        st.markdown(f"{label}. {opt}")
                else:
                    if st.button(f"{label}. {opt}", key=f"qopt_{idx}_{i}",
                                 use_container_width=True):
                        st.session_state.quiz_selected = i
                        st.session_state.quiz_answered = True
                        if i == correct:
                            st.session_state.quiz_score += 1
                        st.rerun()

            if st.session_state.quiz_answered:
                explanation = q.get("explanation", "")
                st.markdown(
                    f'<div class="explanation-box">💡 <b>Explanation:</b> '
                    f'{explanation}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Next Question ➡", use_container_width=True,
                             type="primary", key="quiz_next"):
                    st.session_state.current_quiz_idx += 1
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_selected = None
                    st.rerun()
        else:
            # ── Results screen ──
            score = st.session_state.quiz_score
            total = len(qs)
            pct = (score / total) * 100 if total > 0 else 0

            if pct >= 80:
                emoji, color, msg = "🌟", "#34d399", "Excellent! You're a master!"
            elif pct >= 60:
                emoji, color, msg = "👍", "#a78bfa", "Good job! Keep practicing!"
            else:
                emoji, color, msg = "📚", "#f43f5e", "Keep studying! You'll get there!"

            st.balloons()
            st.markdown(
                f"""<div class="score-result-box" style="border:2px solid {color}33;">
                    <div style="font-size:3.5rem;margin-bottom:8px;">{emoji}</div>
                    <h2 style="color:{color};margin:0 0 8px;">{msg}</h2>
                    <div style="font-size:2.8rem;font-weight:800;color:{color};
                        letter-spacing:-0.03em;">{score}/{total}</div>
                    <p style="color:#64748b;">{pct:.0f}% Correct</p>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("🔄 New Quiz", use_container_width=True, type="primary",
                         key="quiz_reset"):
                st.session_state.quiz_questions = []
                st.session_state.current_quiz_idx = 0
                st.session_state.quiz_score = 0
                st.rerun()
