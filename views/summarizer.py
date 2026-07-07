from datetime import datetime

import streamlit as st

from api import call_groq
from components import page_header, empty_state, copy_button, word_count


_SUMMARY_TYPES = {
    "Concise": "Concise 2-3 paragraph summary.",
    "Detailed Notes": "Detailed notes with all concepts and definitions.",
    "Key Points": "Key points as organized bullet list.",
    "Study Guide": "Study guide with concepts, definitions, formulas, review questions.",
    "ELI5": "Explain using simple analogies for a beginner.",
}


def render() -> None:
    page_header("📄", "AI Summarizer",
                "Paste material and get structured summaries.")

    col_in, col_out = st.columns(2)

    with col_in:
        st.markdown("#### Input")
        inp = st.text_area("Material:",
                           value=st.session_state.summary_text,
                           placeholder="Paste notes, textbook, article...",
                           height=280, key="sum_input")
        st.markdown(
            f"<span style='color:#64748b;font-size:0.8rem;'>{word_count(inp)} words</span>",
            unsafe_allow_html=True,
        )
        stype = st.selectbox("Type:", list(_SUMMARY_TYPES.keys()), key="sum_type")

        if st.button("✨ Summarize", use_container_width=True, type="primary",
                     key="summarize_btn"):
            if inp and inp.strip():
                st.session_state.summary_text = inp
                with st.spinner("Summarizing..."):
                    prompt = (
                        f"{_SUMMARY_TYPES[stype]}\n"
                        "Format with markdown headers, bullets, emphasis.\n\n"
                        f"Material:\n{inp[:6000]}"
                    )
                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.4, max_tokens=4096,
                    )
                    st.session_state.summary_result = r
                    st.rerun()
            else:
                st.warning("Enter text to summarize.")

    with col_out:
        st.markdown("#### Output")
        if st.session_state.summary_result:
            # Render with st.markdown for proper markdown processing
            st.markdown(st.session_state.summary_result)
            copy_button(st.session_state.summary_result, "Copy")
            st.download_button(
                "⬇️ Download",
                st.session_state.summary_result,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
            )
        else:
            empty_state("✍️", "Summary Appears Here",
                        "Enter material and click 'Summarize'.")
