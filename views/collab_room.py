import html as html_lib
from datetime import datetime

import streamlit as st

from api import call_groq
from components import page_header, empty_state
from state import make_id


def render() -> None:
    page_header("🤝", "Collaborative Study Room",
                "Simulated study group with AI-powered discussion.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Room Settings")

        # Generate room ID once and persist
        if not st.session_state.collab_room_id:
            st.session_state.collab_room_id = f"room-{make_id()}"

        room_id = st.text_input("Room ID:",
                                value=st.session_state.collab_room_id,
                                placeholder="Enter room ID",
                                key="collab_room_input")
        st.session_state.collab_room_id = room_id

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 💡 AI Study Partner")

        ai_topic = st.text_input("Topic to discuss:",
                                 placeholder="e.g., Quantum Mechanics",
                                 key="collab_topic")
        ai_role = st.selectbox(
            "AI Role:",
            ["Study Buddy", "Devil's Advocate", "Tutor", "Quiz Master", "Skeptic"],
            key="collab_role",
        )

        _ROLE_PROMPTS = {
            "Study Buddy": "You are a friendly study buddy discussing {topic}. Be encouraging, ask thought-provoking questions, and share insights.",
            "Devil's Advocate": "You are playing devil's advocate on {topic}. Challenge assumptions and present counterarguments to deepen understanding.",
            "Tutor": "You are an expert tutor explaining {topic}. Break down complex concepts and check for understanding.",
            "Quiz Master": "You are a quiz master testing knowledge on {topic}. Ask challenging questions and provide explanations.",
            "Skeptic": "You are a skeptical reviewer of {topic}. Question the validity of claims and ask for evidence.",
        }

        if st.button("🤖 Ask AI Partner", use_container_width=True,
                     type="primary", key="collab_ask"):
            if ai_topic:
                with st.spinner("AI is thinking..."):
                    system = _ROLE_PROMPTS[ai_role].format(topic=ai_topic)
                    messages = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": (
                            f"Let's discuss {ai_topic}. "
                            "Start with an engaging question or insight."
                        )},
                    ]
                    r = call_groq(
                        messages=messages,
                        model=st.session_state.selected_model,
                        temperature=0.7, max_tokens=1024,
                    )
                    st.session_state.collab_messages.append({
                        "role": "ai", "content": r,
                        "avatar": "🤖",
                        "time": datetime.now().strftime("%H:%M"),
                    })
                    st.rerun()
            else:
                st.warning("Enter a topic.")

    with col_right:
        st.markdown(f"#### 💬 Room: {st.session_state.collab_room_id}")

        if not st.session_state.collab_messages:
            empty_state("🤝", "Empty Room",
                        "Start a discussion with the AI study partner "
                        "or add your own thoughts!")
        else:
            for msg in st.session_state.collab_messages:
                cls = ("collab-message-user" if msg["role"] == "user"
                       else "collab-message-other")
                safe_content = html_lib.escape(msg.get("content", ""))
                st.markdown(
                    f"""<div style="display:flex;align-items:flex-start;gap:8px;margin:8px 0;">
                        <span style="font-size:1.2rem;">{msg.get('avatar', '💬')}</span>
                        <div class="collab-message {cls}">
                            <div style="font-size:0.75rem;color:#64748b;margin-bottom:4px;">
                                {msg.get('time', '')}</div>
                            {safe_content}
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        user_msg = st.text_input("Your message:",
                                 placeholder="Share your thoughts...",
                                 key="collab_msg_input")
        if st.button("💬 Send", use_container_width=True, key="collab_send"):
            if user_msg and user_msg.strip():
                st.session_state.collab_messages.append({
                    "role": "user", "content": user_msg.strip(),
                    "avatar": "👤",
                    "time": datetime.now().strftime("%H:%M"),
                })
                st.rerun()
