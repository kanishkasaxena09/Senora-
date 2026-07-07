"""
Mind Map — AI-generated hierarchical concept maps.
"""

import json

import streamlit as st

from api import call_groq, parse_json_response
from components import page_header, empty_state, copy_button
import html as html_lib


def render() -> None:
    page_header("🧠", "AI Mind Map Generator",
                "Generate visual concept maps from any topic.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Generate Mind Map")
        topic = st.text_input(
            "Topic:",
            placeholder="e.g., Photosynthesis, French Revolution, Machine Learning",
            key="mm_topic",
        )
        depth = st.slider("Depth:", 2, 5, 3, key="mm_depth")

        if st.button("✨ Generate Mind Map", use_container_width=True,
                     type="primary", key="mm_generate"):
            if topic:
                with st.spinner("Generating mind map..."):
                    prompt = (
                        f'Generate a hierarchical mind map for: "{topic}"\n'
                        "Return ONLY JSON in this exact format:\n"
                        '{\n  "central": "Main Topic",\n'
                        '  "branches": [\n'
                        '    {"name": "Branch 1", "sub_branches": ["Sub 1", "Sub 2"]},\n'
                        '    {"name": "Branch 2", "sub_branches": ["Sub 1", "Sub 2"]}\n'
                        "  ]\n}\n\n"
                        f"Generate {depth} levels of depth with 3-5 branches at each level."
                    )
                    r = call_groq(
                        messages=[{"role": "user", "content": prompt}],
                        model=st.session_state.selected_model,
                        temperature=0.3, max_tokens=2048,
                        response_format={"type": "json_object"},
                    )
                    data = parse_json_response(r)
                    if data and isinstance(data, dict):
                        st.session_state.mind_map_data = data
                        st.rerun()
                    else:
                        st.error("Failed to parse mind map data.")
                        st.code(r[:500])
            else:
                st.warning("Enter a topic.")

    with col_right:
        st.markdown("#### Mind Map")
        data = st.session_state.mind_map_data
        if data:
            central = html_lib.escape(str(data.get("central", "Topic")))
            html_parts = [
                '<div class="mind-map-container">',
                '<div style="text-align:center;margin-bottom:24px;">',
                f'<div class="mind-map-node" style="font-size:1.2rem;padding:14px 28px;">',
                f'🎯 {central}</div></div>',
            ]

            for branch in data.get("branches", []):
                name = html_lib.escape(str(branch.get("name", "")))
                html_parts.append(f'<div style="margin:16px 0;">')
                html_parts.append(f'<div class="mind-map-node">{name}</div>')
                html_parts.append('<div style="margin-top:8px;">')
                for sub in branch.get("sub_branches", []):
                    safe_sub = html_lib.escape(str(sub))
                    html_parts.append(f'<div class="mind-map-branch">{safe_sub}</div>')
                html_parts.append("</div></div>")

            html_parts.append("</div>")
            st.markdown("".join(html_parts), unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            copy_button(json.dumps(data, indent=2), "Copy JSON")
        else:
            empty_state("🧠", "No Mind Map Yet",
                        "Enter a topic and generate a visual concept map!")
