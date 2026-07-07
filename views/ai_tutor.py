import streamlit as st

from api import call_groq
from components import page_header, empty_state, copy_button


def render() -> None:
    page_header("💬", "AI Tutor Chat", "Ask anything. The AI adapts to your level.")

    # ── Chat history ──
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            empty_state("🤖", "Start a Conversation",
                        "Ask a question or pick a quick prompt below.")
        else:
            for msg in st.session_state.chat_history:
                cls = "chat-message-user" if msg["role"] == "user" else "chat-message-assistant"
                st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)

    # ── Input row ──
    col_input, col_send = st.columns([4, 1])
    with col_input:
        user_input = st.text_input(
            "Ask:", placeholder=f"Ask about {st.session_state.study_subject}...",
            key="chat_input", label_visibility="collapsed",
        )
    with col_send:
        send_clicked = st.button("🚀 Send", use_container_width=True, type="primary")

    # ── Quick prompts ──
    st.markdown(
        "<p style='color:#64748b;font-size:0.8rem;margin:8px 0 6px;'><b>Quick Questions:</b></p>",
        unsafe_allow_html=True,
    )
    prompt_cols = st.columns(4)
    quick_prompts = ["Explain simply", "Practice problems", "Study plan", "Quiz me"]
    quick_clicked = None
    for i, p in enumerate(quick_prompts):
        with prompt_cols[i]:
            if st.button(p, key=f"qp_{i}", use_container_width=True):
                quick_clicked = p

    # ── Determine message to send ──
    message_to_send = None
    if send_clicked and user_input and user_input.strip():
        message_to_send = user_input.strip()
    elif quick_clicked:
        message_to_send = quick_clicked

    if message_to_send:
        st.session_state.chat_history.append({"role": "user", "content": message_to_send})
        system_prompt = (
            f"You are an expert AI tutor in {st.session_state.study_subject}. "
            "Teaching style: clear, patient, uses analogies, breaks down complex topics, "
            "provides memory techniques. Adapt to the student's level."
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(st.session_state.chat_history[-10:])

        with st.spinner("Thinking..."):
            response = call_groq(
                messages=messages,
                model=st.session_state.selected_model,
                temperature=0.7,
                max_tokens=2048,
            )
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # ── Clear / Copy ──
    if st.session_state.chat_history:
        c1, c2 = st.columns([1, 6])
        with c1:
            if st.button("🗑️ Clear", type="secondary", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
        with c2:
            all_chat = "\n\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in st.session_state.chat_history
            )
            copy_button(all_chat, "Copy Chat")
