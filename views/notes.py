"""
Notes — create, search, enhance, and convert notes to flashcards.
"""

from datetime import datetime

import streamlit as st

from api import call_groq, parse_json_response, extract_cards_from_json
from components import page_header, empty_state, copy_button, word_count
from state import make_id


def render() -> None:
    page_header("🗒️", "Study Notes",
                "Create, search, and enhance notes with AI.")

    col_left, col_right = st.columns(2)

    # ── Left: Create ──
    with col_left:
        st.markdown("#### Create")
        note_title = st.text_input("Title:",
                                   placeholder="e.g., Chapter 3 — Cell Structure",
                                   key="note_title")
        note_content = st.text_area("Content:", placeholder="Write notes...",
                                    height=180, key="note_content_input")
        note_tags = st.text_input("Tags:", placeholder="biology, cells, exam-prep",
                                  key="note_tags")
        st.markdown(
            f"<span style='color:#64748b;font-size:0.8rem;'>"
            f"{word_count(note_content)} words</span>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save", use_container_width=True, type="primary",
                         key="note_save"):
                if note_title and note_content:
                    st.session_state.study_notes.append({
                        "title": note_title,
                        "content": note_content,
                        "tags": [t.strip() for t in note_tags.split(",") if t.strip()],
                        "created": datetime.now().isoformat(),
                        "id": make_id(),
                    })
                    st.toast("✅ Note saved!")
                    st.rerun()
                else:
                    st.warning("Fill in title and content.")

        with c2:
            if st.button("✨ AI Enhance", use_container_width=True, key="note_enhance"):
                if note_content and note_content.strip():
                    with st.spinner("Enhancing..."):
                        prompt = (
                            "Improve and structure these notes with markdown formatting. "
                            "Keep original info, enhance clarity, add helpful context.\n\n"
                            f"Notes: {note_content[:3000]}"
                        )
                        r = call_groq(
                            messages=[{"role": "user", "content": prompt}],
                            model=st.session_state.selected_model,
                            temperature=0.4, max_tokens=4096,
                        )
                        st.session_state.current_note = r
                        st.rerun()
                else:
                    st.warning("Enter content first.")

        if st.session_state.current_note:
            st.markdown("---")
            st.markdown("#### Enhanced:")
            st.markdown(st.session_state.current_note)
            copy_button(st.session_state.current_note, "Copy Enhanced")

    # ── Right: Saved notes ──
    with col_right:
        st.markdown("#### Saved Notes")
        notes = st.session_state.study_notes
        if not notes:
            empty_state("📝", "No Notes Yet", "Create a note on the left!")
            return

        search = st.text_input("🔍 Search:", placeholder="By title or tag...",
                               key="note_search")

        for note in reversed(notes):
            # Filter
            if search:
                haystack = (note.get("title", "") + " "
                            + ",".join(note.get("tags", []))).lower()
                if search.lower() not in haystack:
                    continue

            nid = note.get("id", "")
            with st.expander(f"📄 {note.get('title', 'Untitled')}"):
                # Tags
                tags = note.get("tags", [])
                if tags:
                    tag_html = "".join(
                        f'<span class="note-tag">{t}</span>' for t in tags
                    )
                else:
                    tag_html = ('<span style="color:#475569;font-size:0.75rem;">'
                                'No tags</span>')
                st.markdown(f"<div style='margin-bottom:8px;'>{tag_html}</div>",
                            unsafe_allow_html=True)
                st.markdown(
                    f"<span style='color:#475569;font-size:0.75rem;'>"
                    f"🕐 {note.get('created', '')[:10]}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.markdown(note.get("content", ""))

                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    if st.button("📝 Edit", key=f"ed_{nid}",
                                 use_container_width=True):
                        st.session_state.current_note = note.get("content", "")
                        st.rerun()
                with ac2:
                    if st.button("🗑️ Delete", key=f"dl_{nid}",
                                 use_container_width=True):
                        st.session_state.study_notes = [
                            n for n in notes if n.get("id") != nid
                        ]
                        st.toast("🗑️ Note deleted")
                        st.rerun()
                with ac3:
                    if st.button("🃏 To Cards", key=f"fc_{nid}",
                                 use_container_width=True):
                        with st.spinner("Converting..."):
                            prompt = (
                                'Convert to flashcards. Return JSON: '
                                '[{"front":"...","back":"..."},...]\n\n'
                                + note.get("content", "")[:3000]
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
                                        "difficulty": "new",
                                        "id": make_id(),
                                    })
                                st.toast(f"✅ Created {len(cards)} flashcards!")
                                st.rerun()
                            else:
                                st.error("Failed to convert.")
