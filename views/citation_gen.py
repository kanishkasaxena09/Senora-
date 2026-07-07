"""
Citation Generator — generate properly formatted academic citations.
"""

import streamlit as st

from api import call_groq
from components import page_header, empty_state, copy_button


def render() -> None:
    page_header("📖", "AI Citation Generator",
                "Generate proper citations in any format.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Citation Details")
        citation_type = st.selectbox(
            "Format:",
            ["APA 7th", "MLA 9th", "Chicago", "Harvard", "IEEE", "BibTeX"],
            key="cit_format",
        )
        source_type = st.selectbox(
            "Source:",
            ["Book", "Journal Article", "Website", "Video", "Podcast",
             "Conference Paper", "Thesis"],
            key="cit_source",
        )

        with st.expander("Enter Details", expanded=True):
            title = st.text_input("Title:", placeholder="Title of the work",
                                  key="cit_title")
            author = st.text_input("Author(s):", placeholder="e.g., Smith, J. D.",
                                   key="cit_author")
            year = st.text_input("Year:", placeholder="2024", key="cit_year")

            # ── Conditional fields (always initialize defaults) ──
            publisher = ""
            url = ""
            access_date = ""
            volume = ""
            issue = ""
            pages_field = ""

            if source_type in ("Book", "Journal Article", "Conference Paper"):
                publisher = st.text_input("Publisher/Journal:",
                                          placeholder="e.g., Nature, ACM",
                                          key="cit_publisher")
            if source_type == "Website":
                url = st.text_input("URL:", placeholder="https://...",
                                    key="cit_url")
                access_date = st.text_input("Access Date:",
                                            placeholder="2024-06-29",
                                            key="cit_access")
            if source_type == "Journal Article":
                volume = st.text_input("Volume:", placeholder="12",
                                       key="cit_volume")
                issue = st.text_input("Issue:", placeholder="3",
                                      key="cit_issue")
                pages_field = st.text_input("Pages:", placeholder="45-67",
                                            key="cit_pages")

        if st.button("✨ Generate Citation", use_container_width=True,
                     type="primary", key="gen_citation"):
            if title and author and year:
                with st.spinner("Generating citation..."):
                    prompt = (
                        f"Generate a {citation_type} citation for this "
                        f"{source_type.lower()}:\n\n"
                        f"Title: {title}\n"
                        f"Author(s): {author}\n"
                        f"Year: {year}\n"
                    )
                    if publisher:
                        prompt += f"Publisher/Journal: {publisher}\n"
                    if url:
                        prompt += f"URL: {url}\n"
                    if access_date:
                        prompt += f"Access Date: {access_date}\n"
                    if volume:
                        prompt += f"Volume: {volume}\n"
                    if issue:
                        prompt += f"Issue: {issue}\n"
                    if pages_field:
                        prompt += f"Pages: {pages_field}\n"
                    prompt += "\nReturn ONLY the properly formatted citation. No extra text."

                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.2, max_tokens=512,
                    )
                    st.session_state.citation_result = r.strip()
                    st.rerun()
            else:
                st.warning("Please fill in at least title, author, and year.")

    with col_right:
        st.markdown("#### Citation")
        if st.session_state.citation_result:
            st.markdown(
                f"""<div style="background:rgba(20,22,38,0.5);
                    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
                    padding:24px;font-family:monospace;font-size:0.9rem;
                    color:#e2e8f0;line-height:1.6;">
                    {st.session_state.citation_result}
                </div>""",
                unsafe_allow_html=True,
            )
            copy_button(st.session_state.citation_result, "Copy Citation")
        else:
            empty_state("📖", "Citation Appears Here",
                        "Fill in the details to generate a properly formatted citation!")
