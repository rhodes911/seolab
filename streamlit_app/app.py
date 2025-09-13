from __future__ import annotations
import os
import streamlit as st
from content_loader import load_index, prev_next
from state import get_progress, set_checklist, set_completed, export_json, import_json, reset_all
from components import inject_styles, render_callouts, render_toc, checklist

st.set_page_config(page_title="SEO Lab", page_icon="📘", layout="wide")
inject_styles()

INDEX = load_index()

# Sidebar navigation
with st.sidebar:
    st.header("SEO Lab")
    # Build nav by category
    for cat, slugs in INDEX["by_cat"].items():
        with st.expander(cat.title(), expanded=True):
            for slug in slugs:
                lesson = INDEX["by_slug"][slug]
                href = f"?slug={slug}"
                st.markdown(f"- [{lesson.frontmatter.get('title', slug)}]({href})")
    st.markdown("---")
    with st.popover("Export/Import Progress"):
        st.caption("Export your local progress as JSON or import a previous backup.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export JSON"):
                st.download_button("Download", data=export_json(), file_name="seo-lab-progress.json")
        with col2:
            uploaded = st.file_uploader("Import JSON", type=["json"])
            if uploaded is not None:
                text = uploaded.read().decode("utf-8")
                if import_json(text):
                    st.success("Progress imported. Reload the page to see changes.")
                else:
                    st.error("Invalid JSON format.")
        if st.button("Reset All"):
            reset_all()
            st.toast("Progress reset.")

# Read selected slug from query params
params = st.query_params
slug = params.get("slug", [INDEX["all"][0]] if INDEX["all"] else [""])
if isinstance(slug, list):
    slug = slug[0]

if not slug or slug not in INDEX["by_slug"]:
    st.warning("No lessons found.")
    st.stop()

lesson = INDEX["by_slug"][slug]

# Header
st.title(lesson.frontmatter.get("title", slug))
if desc := lesson.frontmatter.get("description"):
    st.markdown(f"<p class='muted'>{desc}</p>", unsafe_allow_html=True)

# ToC
render_toc(lesson.headings)

# Render content
lines = lesson.content_with_anchors.splitlines()
lines = render_callouts(lines)
st.markdown("\n".join(lines), unsafe_allow_html=True)

# Checklist
check_items = lesson.checklist_items or lesson.frontmatter.get("checklist", [])
if check_items:
    prog = get_progress()
    prev_map = prog.get("checklist", {}).get(slug, {})
    prev_vals = [bool(prev_map.get(item, False)) for item in check_items]
    out_vals = checklist("Checklist", check_items, slug, prev_vals)
    colA, colB = st.columns([1,3])
    with colA:
        save = st.button("Save Checklist", key=f"save_{slug}")
    with colB:
        mark_done = st.toggle("Mark lesson complete", value=prog.get("completed", {}).get(slug, False), key=f"done_{slug}")
    if save:
        set_checklist(slug, check_items, out_vals)
        st.success("Saved.")
    set_completed(slug, mark_done)

# Prev / Next
prev, nxt = prev_next(INDEX, slug)
cols = st.columns(2)
with cols[0]:
    if prev:
        st.link_button("⬅ Previous", f"?slug={prev.slug}")
with cols[1]:
    if nxt:
        st.link_button("Next ➡", f"?slug={nxt.slug}")
