from __future__ import annotations
import streamlit as st
from content_loader import load_index
from state import get_progress

st.set_page_config(page_title="SEO Lab • Dashboard", page_icon="📊", layout="wide")

INDEX = load_index()
progress = get_progress()
completed = progress.get("completed", {})

st.title("Dashboard")

# Overall
total = len(INDEX["all"]) or 1
count = sum(1 for s in INDEX["all"] if completed.get(s))
st.metric("Overall completion", f"{count}/{total}", delta=f"{int(count/total*100)}%")

# Per-category
st.header("By category")
for cat, slugs in INDEX["by_cat"].items():
    done = sum(1 for s in slugs if completed.get(s))
    st.progress(done / (len(slugs) or 1), text=f"{cat.title()}: {done}/{len(slugs)}")

# Recent / Next suggestions (simple heuristic)
st.header("Suggestions")
for slug in INDEX["all"][:3]:
    lesson = INDEX["by_slug"][slug]
    status = "✅ Done" if completed.get(slug) else "⬜ Not started"
    st.write(f"- [{lesson.frontmatter.get('title', slug)}](../app?slug={slug}) — {status}")
