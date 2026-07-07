import json
import random
from datetime import datetime

import streamlit as st

from api import call_groq, parse_json_response, extract_cards_from_json
from components import (
    page_header, empty_state, render_flashcard, flashcard_badges, spacer,
)
from state import make_id


def render() -> None:
    page_header("🎴", "Smart Flashcards",
                "Create, generate, and study with 3D flip cards.")

    col_left, col_right = st.columns([1, 2])

    # ── Left: Create cards ──
    with col_left:
        st.markdown("#### Create")

        with st.expander("✍️ Manual", expanded=True):
            front = st.text_area("Front:", placeholder="What is photosynthesis?",
                                 height=70, key="cf_front")
            back = st.text_area("Back:", placeholder="Process of converting light to energy...",
                                height=70, key="cf_back")
            if st.button("➕ Add", use_container_width=True, key="add_card"):
                if front and back:
                    st.session_state.flashcards.append({
                        "front": front, "back": back,
                        "created": datetime.now().isoformat(),
                        "difficulty": "new", "id": make_id(),
                    })
                    st.toast("✅ Card added!")
                    st.rerun()
                else:
                    st.warning("Fill in both sides.")

        with st.expander("🤖 AI Generate"):
            topic = st.text_input("Topic:", placeholder="e.g., Cell Biology, Python",
                                  key="fc_gen_topic")
            count = st.slider("Count:", 3, 10, 5, key="fc_gen_count")
            if st.button("✨ Generate", use_container_width=True, key="gen_cards"):
                if topic:
                    with st.spinner("Generating..."):
                        prompt = (
                            f'Generate {count} flashcards about "{topic}" '
                            f"in {st.session_state.study_subject}.\n"
                            'Return ONLY a JSON array: [{"front":"...","back":"..."},...]'
                        )
                        r = call_groq(
                            messages=[{"role": "user", "content": prompt}],
                            model=st.session_state.selected_model,
                            temperature=0.5, max_tokens=2048,
                            response_format={"type": "json_object"},
                        )
                        data = parse_json_response(r)
                        if data is not None:
                            cards = extract_cards_from_json(data)
                            for c in cards:
                                st.session_state.flashcards.append({
                                    "front": c.get("front", ""),
                                    "back": c.get("back", ""),
                                    "created": datetime.now().isoformat(),
                                    "difficulty": "new", "id": make_id(),
                                })
                            st.toast(f"✅ Generated {len(cards)} cards!")
                            st.rerun()
                        else:
                            st.error("Failed to parse AI response.")
                            st.code(r[:400])
                else:
                    st.warning("Enter a topic.")

        with st.expander("📤 Import from File"):
            uploaded = st.file_uploader("Upload .txt:", type=["txt"], key="fc_upload")
            if uploaded:
                content = uploaded.read().decode("utf-8")
                if st.button("🔄 Convert", use_container_width=True, key="convert_cards"):
                    with st.spinner("Converting..."):
                        prompt = (
                            'Convert to flashcards. Return JSON: '
                            '[{"front":"...","back":"..."},...]\n\n'
                            + content[:3000]
                        )
                        r = call_groq(
                            messages=[{"role": "user", "content": prompt}],
                            model=st.session_state.selected_model,
                            temperature=0.3, max_tokens=2048,
                        )
                        data = parse_json_response(r)
                        if data is not None:
                            cards = extract_cards_from_json(data)
                            for c in cards:
                                st.session_state.flashcards.append({
                                    "front": c.get("front", ""),
                                    "back": c.get("back", ""),
                                    "created": datetime.now().isoformat(),
                                    "difficulty": "new", "id": make_id(),
                                })
                            st.toast(f"✅ Imported {len(cards)} cards!")
                            st.rerun()
                        else:
                            st.error("Failed to parse the converted text.")

    # ── Right: Study mode ──
    with col_right:
        st.markdown("#### Study Mode")
        if not st.session_state.flashcards:
            empty_state("🃏", "No Flashcards",
                        "Create cards on the left or generate with AI.")
            return

        total = len(st.session_state.flashcards)
        idx = st.session_state.current_card_idx % total
        card = st.session_state.flashcards[idx]

        st.progress((idx + 1) / total, text=f"Card {idx + 1} of {total}")

        render_flashcard(card["front"], card["back"], st.session_state.card_flipped)
        spacer(12)

        # Navigation buttons
        b1, b2, b3, b4, b5 = st.columns(5)
        with b1:
            if st.button("◀ Prev", key="fc_prev"):
                st.session_state.current_card_idx = (idx - 1) % total
                st.session_state.card_flipped = False
                st.rerun()
        with b2:
            if st.button("🔄 Flip", type="primary", key="fc_flip"):
                st.session_state.card_flipped = not st.session_state.card_flipped
                st.rerun()
        with b3:
            if st.button("❌ Hard", key="fc_hard"):
                card["difficulty"] = "hard"
                st.session_state.current_card_idx = (idx + 1) % total
                st.session_state.card_flipped = False
                st.rerun()
        with b4:
            if st.button("✅ Easy", key="fc_easy"):
                card["difficulty"] = "easy"
                st.session_state.current_card_idx = (idx + 1) % total
                st.session_state.card_flipped = False
                st.rerun()
        with b5:
            if st.button("Next ▶", key="fc_next"):
                st.session_state.current_card_idx = (idx + 1) % total
                st.session_state.card_flipped = False
                st.rerun()

        if st.button("🔀 Shuffle", use_container_width=True, key="fc_shuffle"):
            random.shuffle(st.session_state.flashcards)
            st.session_state.current_card_idx = 0
            st.session_state.card_flipped = False
            st.rerun()

        # Badge summary
        easy = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "easy")
        hard = sum(1 for c in st.session_state.flashcards if c.get("difficulty") == "hard")
        new = total - easy - hard
        flashcard_badges(easy, new, hard)
