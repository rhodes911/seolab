from __future__ import annotations
import os, re
import streamlit as st
from content_loader import load_index, prev_next
from state import get_progress, set_checklist, set_completed, export_json, import_json, reset_all
from components import (
    inject_styles,
    render_callouts,
    render_toc,
    checklist,
    enhanced_checklist,
    preset_selector,
    decision_tree_navigator,
    quiz_block,
    notes_for_sections,
    meta_preview_widget,
)
from case_study import case_study_builder

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
                
                # Add dynamic section links if applicable
                dyn_links = []
                if lesson.frontmatter.get("quizzes"):
                    dyn_links.append(f"  - [Quizzes]({href}#quizzes)")
                if lesson.frontmatter.get("meta_preview"):
                    dyn_links.append(f"  - [Meta Preview]({href}#meta-preview)")
                dyn_links.append(f"  - [Notes]({href}#notes)")
                
                if dyn_links:
                    st.markdown("\n".join(dyn_links))
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

# Optional: scenario/context presets
selected_preset = None
presets_cfg = lesson.frontmatter.get("presets")
if isinstance(presets_cfg, dict):
    selected_preset = preset_selector(presets_cfg, key=slug)
    # Show a subtle banner under the title with current context
    if selected_preset:
        label = next((o.get("label", o.get("key")) for o in presets_cfg.get("options", []) if o.get("key") == selected_preset), selected_preset)
        tip = (presets_cfg.get("tips") or {}).get(selected_preset)
        banner = f"<div class='preset-tip'><strong>Context:</strong> {label}"
        if tip:
            banner += f" — {tip}"
        banner += "</div>"
        st.markdown(banner, unsafe_allow_html=True)

# Inline preset token replacement: {{preset:key|text}}
TOKEN_RE = re.compile(r"\{\{preset:([a-zA-Z0-9_-]+)\|(.*?)\}\}")

def _apply_preset_tokens(text: str, preset: str | None) -> str:
    if not text:
        return text
    def _sub(m: re.Match[str]):
        key = m.group(1)
        val = m.group(2)
        if key == "default":
            return val if not preset else ""
        return val if (preset and preset == key) else ""
    return TOKEN_RE.sub(_sub, text)

# ToC
render_toc(lesson.headings)

# Render content (apply preset-aware inline tokens first)
lines = [
    _apply_preset_tokens(line, selected_preset)
    for line in lesson.content_with_anchors.splitlines()
]
lines = render_callouts(lines)

# Process the content into sections for selective rendering
sections = []
h1_content = []
current_section = None
current_content = []
heading_pattern = re.compile(r'^(#{1,6})\s+(.+?)\s*(?:<a id="([^"]+)"></a>)?$')
h1_found = False

for line in lines:
    match = heading_pattern.match(line)
    
    if match:
        level = len(match.group(1))
        heading = match.group(2)
        heading_id = match.group(3) if match.group(3) else re.sub(r"[^a-z0-9\s-]", "", heading.lower()).replace(" ", "-")
        
        # Handle H1 (title) - just add to h1_content
        if level == 1:
            if h1_found:
                # Skip duplicate title
                continue
            h1_found = True
            h1_content.append(line)
            continue
            
        # Save previous section if exists
        if current_section:
            sections.append({
                "level": current_section["level"],
                "heading": current_section["heading"],
                "id": current_section["id"],
                "content": current_content
            })
        
        # Start new section
        current_section = {
            "level": level,
            "heading": heading,
            "id": heading_id
        }
        current_content = [line]
    else:
        # Add content to appropriate section
        if current_section:
            current_content.append(line)
        else:
            h1_content.append(line)

# Don't forget the last section
if current_section:
    sections.append({
        "level": current_section["level"],
        "heading": current_section["heading"],
        "id": current_section["id"],
        "content": current_content
    })

# Render content in order
if h1_content:
    # Render the title/introduction section
    st.markdown("\n".join(h1_content), unsafe_allow_html=True)

# Now render each H2+ section with notes immediately following
for idx, section in enumerate(sections):
    # Only add notes to H2 sections
    if section["level"] == 2:
        # Render the section content
        st.markdown("\n".join(section["content"]), unsafe_allow_html=True)
        
        # Add notes immediately after this section
        with st.container():
            notes_for_sections(
                slug, 
                [(section["level"], section["heading"], section["id"])], 
                show_heading=False, 
                mode="inline", 
                suffix=f"_{idx}"  # Use index to ensure unique keys
            )
        
        # Add a separator except after the last section
        if idx < len(sections) - 1:
            st.markdown('<hr class="section-separator"/>', unsafe_allow_html=True)
    else:
        # Just render other heading levels without notes
        st.markdown("\n".join(section["content"]), unsafe_allow_html=True)
        
# Checklist (prefer frontmatter-defined enhanced checklist if present)
check_items = lesson.frontmatter.get("checklist") or lesson.checklist_items
if check_items:
    prog = get_progress()
    prev_map = prog.get("checklist", {}).get(slug, {})
    # Normalize items for key lookup and optional preset filtering
    norm_items = []
    for it in check_items:
        if isinstance(it, dict):
            # Optional preset filtering: 'only' (list) or 'preset' (single)
            only = it.get("only") or it.get("preset")
            include = True
            if selected_preset and only:
                if isinstance(only, (list, tuple, set)):
                    include = selected_preset in only
                else:
                    include = (selected_preset == only)
            if include:
                # Apply inline tokens to text/why
                new_it = dict(it)
                if new_it.get("text"):
                    new_it["text"] = _apply_preset_tokens(str(new_it.get("text")), selected_preset)
                if new_it.get("why"):
                    new_it["why"] = _apply_preset_tokens(str(new_it.get("why")), selected_preset)
                norm_items.append(new_it)
        else:
            norm_items.append(_apply_preset_tokens(str(it), selected_preset))

    # Build previous values map based on item text
    labels = [it.get("text") if isinstance(it, dict) else str(it) for it in norm_items]
    prev_vals = [bool(prev_map.get(lbl, False)) for lbl in labels]
    # Use enhanced checklist if any dict present
    if any(isinstance(it, dict) for it in norm_items):
        out_vals = enhanced_checklist("Checklist", norm_items, slug, prev_vals)
    else:
        out_vals = checklist("Checklist", labels, slug, prev_vals)
    colA, colB = st.columns([1,3])
    with colA:
        save = st.button("Save Checklist", key=f"save_{slug}")
    with colB:
        mark_done = st.toggle("Mark lesson complete", value=prog.get("completed", {}).get(slug, False), key=f"done_{slug}")
    if save:
        set_checklist(slug, labels, out_vals)
        st.success("Saved.")
    set_completed(slug, mark_done)

# Decision Tree Navigator (optional, frontmatter-driven)
tree = lesson.frontmatter.get("decision_tree")
if isinstance(tree, dict) and tree.get("nodes"):
    decision_tree_navigator(tree, state_key=slug)

# Quizzes (optional)
quizzes = lesson.frontmatter.get("quizzes")
if isinstance(quizzes, list) and quizzes:
    st.markdown("---\n<a id='quizzes'></a>", unsafe_allow_html=True)
    st.markdown("### Check your understanding")
    for q in quizzes:
        if isinstance(q, dict):
            quiz_block(slug, q, key_prefix=f"{slug}_")

# Meta Preview (optional)
meta_cfg = lesson.frontmatter.get("meta_preview")
if meta_cfg is True or isinstance(meta_cfg, dict):
    st.markdown("---\n<a id='meta-preview'></a>", unsafe_allow_html=True)
    st.markdown("### 🧪 Meta Preview")
    meta_preview_widget(slug, show_heading=False)

# Case Study Builder (optional)
case_study_cfg = lesson.frontmatter.get("case_study")
if case_study_cfg is True or isinstance(case_study_cfg, dict):
    st.markdown("---\n<a id='case-study'></a>", unsafe_allow_html=True)
    
    # Get context from presets if available
    context = ""
    if selected_preset:  # Use the selected_preset variable that's already defined earlier
        context = selected_preset
    
    # Add the case study builder
    case_study_builder(slug, context)

# Notes per section (always available)
st.markdown("---\n<a id='notes'></a>", unsafe_allow_html=True)
st.markdown("### 🗒️ Your Notes Summary")
notes_for_sections(slug, lesson.headings, show_heading=False, mode="summary")

# Prev / Next
prev, nxt = prev_next(INDEX, slug)
cols = st.columns(2)
with cols[0]:
    if prev:
        st.link_button("⬅ Previous", f"?slug={prev.slug}")
with cols[1]:
    if nxt:
        st.link_button("Next ➡", f"?slug={nxt.slug}")
