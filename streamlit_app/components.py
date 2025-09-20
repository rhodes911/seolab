from __future__ import annotations
from typing import List, Tuple, Dict, Any, Optional
import re
import streamlit as st
import os
import json
from state import get_quiz_state, set_quiz_result, get_notes, set_note, get_meta, set_meta

CALLOUT_RE = re.compile(r"^>\s*\[!(NOTE|TIP|INFO|WARNING|DANGER)\]\s*(.*)$", re.IGNORECASE)

def inject_styles():
    # Load external stylesheet (relative to this file) and inject helper classes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, "styles.css")
    css = ""
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
    except Exception:
        pass
    style_block = (
        "<style>\n"
        + css
        + "\n"
        + ".callout { border-left: 4px solid var(--primary-color,#2563eb); padding: .75rem 1rem; background: rgba(37,99,235,.05); border-radius: .5rem; margin: .75rem 0; }\n"
        + ".callout.tip { border-color: #10b981; background: rgba(16,185,129,.06); }\n"
        + ".callout.info { border-color: #3b82f6; background: rgba(59,130,246,.06); }\n"
        + ".callout.warn { border-color: #f59e0b; background: rgba(245,158,11,.06); }\n"
        + ".callout.danger { border-color: #ef4444; background: rgba(239,68,68,.06); }\n"
        + ".toc a { text-decoration: none; color: inherit; }\n"
        + ".toc .lvl-2 { margin-left: .25rem; }\n"
        + ".toc .lvl-3 { margin-left: 1.25rem; opacity: .9; }\n"
        + ".toc .lvl-4 { margin-left: 2rem; opacity: .8; }\n"
        + ".muted { color: rgba(0,0,0,.6); }\n"
        + ".kbd { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace; padding: 2px 6px; border: 1px solid #e5e7eb; border-bottom-width: 2px; border-radius: 6px; background: #f9fafb; }\n"
        + ".preset-tip { border-left: 4px solid #6366f1; background: rgba(99,102,241,.06); padding: .75rem 1rem; border-radius: .5rem; margin: .75rem 0; }\n"
        + ".group-title { font-weight: 600; margin-top: .5rem; opacity: .85; }\n"
        + ".small-muted { color: rgba(0,0,0,.6); font-size: .9em; }\n"
        + ".section-notes { margin: 1rem 0 2rem; padding-left: 1rem; border-left: 3px solid #f0f0f0; }\n"
        + "</style>"
    )
    st.markdown(style_block, unsafe_allow_html=True)


def render_callouts(md_lines: List[str]) -> List[str]:
    rendered: List[str] = []
    for line in md_lines:
        m = CALLOUT_RE.match(line)
        if m:
            kind = m.group(1).upper()
            text = m.group(2)
            klass = {
                "NOTE": "",
                "TIP": "tip",
                "INFO": "info",
                "WARNING": "warn",
                "DANGER": "danger",
            }.get(kind, "")
            rendered.append(f'<div class="callout {klass}"><strong>{kind.title()}:</strong> {text}</div>')
        else:
            rendered.append(line)
    return rendered


def render_toc(headings: List[Tuple[int,str,str]]):
    with st.sidebar:
        st.markdown("### On this page")
        toc_lines = ["<div class='toc'>"]
        for depth, text, hid in headings:
            if depth < 2: 
                continue
            depth = min(depth, 4)
            toc_lines.append(f"<div class='lvl-{depth}'><a href='#{hid}'>{text}</a></div>")
        toc_lines.append("</div>")
        st.markdown("\n".join(toc_lines), unsafe_allow_html=True)


def checklist(title: str, items: List[str], slug: str, values: List[bool]) -> List[bool]:
    """Legacy simple checklist renderer kept for backward compatibility."""
    st.markdown(f"#### {title}")
    cols = st.columns([1,4])
    with cols[0]:
        st.caption("Mark done")
    with cols[1]:
        st.caption("Item")
    out: List[bool] = []
    for i, item in enumerate(items):
        c1, c2 = st.columns([1, 4])
        with c1:
            out_val = st.checkbox(
                label=str(item) if item else "Item",
                value=values[i] if i < len(values) else False,
                key=f"chk_{slug}_{i}",
                label_visibility="collapsed",
            )
        with c2:
            st.write(item)
        out.append(out_val)
    return out


def enhanced_checklist(title: str, items: List[Any], slug: str, values: List[bool]) -> List[bool]:
    """
    Enhanced checklist supporting:
    - items as strings or dicts { text, why?, group? }
    - optional grouping headers
    - progress indicator
    """
    st.markdown(f"#### {title}")
    # Normalize items
    norm_items: List[Dict[str, Any]] = []
    for it in items:
        if isinstance(it, str):
            norm_items.append({"text": it, "why": None, "group": None})
        elif isinstance(it, dict):
            norm_items.append({
                "text": str(it.get("text", "")).strip(),
                "why": (str(it.get("why")).strip() if it.get("why") else None),
                "group": (str(it.get("group")).strip() if it.get("group") else None),
            })
        else:
            norm_items.append({"text": str(it), "why": None, "group": None})

    total = len(norm_items)
    done = sum(1 for i, _ in enumerate(norm_items) if i < len(values) and values[i])
    pct = (done / total) if total else 0.0
    st.progress(pct, text=f"Completed {done}/{total}")

    # Render items, grouped if applicable
    current_group = object()
    out_vals: List[bool] = []
    for i, it in enumerate(norm_items):
        grp = it.get("group")
        if grp and grp != current_group:
            st.markdown(f"<div class='group-title'>{grp}</div>", unsafe_allow_html=True)
            current_group = grp
        c1, c2 = st.columns([1, 4])
        with c1:
            val = st.checkbox(
                label=it["text"] or "Item",
                value=values[i] if i < len(values) else False,
                key=f"e_chk_{slug}_{i}",
                label_visibility="collapsed",
            )
        with c2:
            st.write(it["text"]) 
            if it.get("why"):
                st.caption(it["why"])  # small rationale
        out_vals.append(val)

    if total and done == total:
        st.success("Nice! All checklist items completed.")
    return out_vals


def preset_selector(presets: Dict[str, Any], key: str) -> Optional[str]:
    """
    Renders a scenario/preset selector.
    presets schema:
      { 'options': [ { 'key': 'local', 'label': 'Local', 'description': '...' }, ...], 'default': 'general' }
    Returns selected key or None.
    """
    opts = presets.get("options") or []
    if not opts:
        return None
    labels = [o.get("label", o.get("key", "")) for o in opts]
    keys = [o.get("key") for o in opts]
    default_key = presets.get("default") or (keys[0] if keys else None)
    try:
        default_idx = keys.index(default_key) if default_key in keys else 0
    except Exception:
        default_idx = 0
    selected_label = None
    try:
        if hasattr(st, "segmented_control"):
            selected_label = st.segmented_control(
                "Context",
                labels,
                selection_mode="single",
                default=labels[default_idx],
                key=f"preset_{key}"
            )
        else:
            selected_label = st.radio("Context", labels, index=default_idx, key=f"preset_{key}")
    except Exception:
        selected_label = st.radio("Context", labels, index=default_idx, key=f"preset_{key}")
    # Map label back to key
    label_to_key = {lab: k for lab, k in zip(labels, keys)}
    selected_key = label_to_key.get(selected_label, keys[default_idx] if keys else None)
    # Optional tip
    tips: Dict[str, str] = presets.get("tips") or {}
    tip = tips.get(selected_key)
    if tip:
        label = next((o.get("label", o.get("key")) for o in opts if o.get("key") == selected_key), selected_key)
        st.markdown(f"<div class='preset-tip'><strong>{label}</strong>: {tip}</div>", unsafe_allow_html=True)
    return selected_key


def decision_tree_navigator(tree: Dict[str, Any], state_key: str):
    """
    Generic decision tree navigator.
    Schema:
      { 'title': '...', 'start': 'start', 'nodes': [
          { 'id': 'start', 'type': 'question', 'text': '...', 'options': [ {'label':'Yes','next':'n2'}, ... ] },
          { 'id': 'n2', 'type': 'outcome', 'title': '...', 'description': '...' }
      ]}
    """
    if not tree:
        return
    st.markdown(f"### {tree.get('title','Guided Navigator')}")
    nodes_by_id: Dict[str, Any] = {n.get('id'): n for n in (tree.get('nodes') or [])}
    start_id = tree.get('start') or (tree.get('nodes')[0].get('id') if tree.get('nodes') else None)
    if not start_id:
        st.info("Navigator not configured.")
        return

    # Maintain path in session state
    path_key = f"dt_path_{state_key}"
    if path_key not in st.session_state:
        st.session_state[path_key] = [start_id]
    path: List[str] = st.session_state[path_key]

    current = nodes_by_id.get(path[-1])
    if not current:
        st.session_state[path_key] = [start_id]
        current = nodes_by_id.get(start_id)

    # Render
    # Breadcrumb of visited nodes
    crumbs: List[str] = []
    for nid in path:
        n = nodes_by_id.get(nid)
        if not n: continue
        if n.get('type') == 'question':
            crumbs.append(n.get('text','').strip() or 'Question')
        else:
            crumbs.append(n.get('title','Result').strip())
    if crumbs:
        st.caption(" › ".join(crumbs))
    st.caption(f"Step {len(path)} of {sum(1 for n in nodes_by_id.values() if n.get('type')=='question')} (questions)")
    if current.get('type') == 'question':
        st.write(current.get('text',''))
        options = current.get('options') or []
        labels = [o.get('label','Option') for o in options]
        # Unique key per step
        choice = st.radio("Choose one", labels, key=f"dt_choice_{state_key}_{len(path)}")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Next", key=f"dt_next_{state_key}_{len(path)}"):
                try:
                    idx = labels.index(choice)
                    nxt = options[idx].get('next')
                    if nxt and nxt in nodes_by_id:
                        path.append(nxt)
                except Exception:
                    pass
        with col2:
            if len(path) > 1 and st.button("Back", key=f"dt_back_{state_key}_{len(path)}"):
                path.pop()
    else:
        st.subheader(current.get('title','Result'))
        if current.get('description'):
            st.write(current['description'])
        # Reset/back controls
        col1, col2 = st.columns([1,1])
        with col1:
            if len(path) > 1 and st.button("Back", key=f"dt_back_{state_key}_{len(path)}"):
                path.pop()
        with col2:
            if st.button("Restart", key=f"dt_restart_{state_key}"):
                st.session_state[path_key] = [start_id]


def quiz_block(slug: str, quiz: Dict[str, Any], key_prefix: str = ""):
    """
    Render a simple quiz block.
    Schema example:
      { id, question, type: 'single'|'multi'|'tf', options: [ {text, correct?, explain?}, ...] }
    """
    qid = quiz.get("id") or f"quiz_{abs(hash(str(quiz)))}"
    qstate = get_quiz_state(slug).get(qid)
    st.markdown(f"#### 🧠 {quiz.get('question','Quiz')}" )
    qtype = (quiz.get("type") or "single").lower()
    opts = quiz.get("options") or []
    labels = [o.get("text","Option") for o in opts]
    correct_indices = {i for i,o in enumerate(opts) if o.get("correct")}
    explain = [o.get("explain") for o in opts]
    key_base = f"{key_prefix}{qid}"
    selection = None
    if qtype in ("single","tf"):
        selection = st.radio("Choose one", labels, key=f"{key_base}_radio")
        chosen_idx = labels.index(selection) if selection in labels else None
        submitted = st.button("Check", key=f"{key_base}_check")
        if submitted and chosen_idx is not None:
            is_correct = chosen_idx in correct_indices
            set_quiz_result(slug, qid, chosen_idx, 1 if is_correct else 0, 1)
            st.success("Correct!" if is_correct else "Not quite.")
            if explain[chosen_idx]:
                st.caption(explain[chosen_idx])
    elif qtype == "multi":
        checks = [st.checkbox(lbl, key=f"{key_base}_chk_{i}") for i,lbl in enumerate(labels)]
        submitted = st.button("Check", key=f"{key_base}_check")
        if submitted:
            chosen = {i for i, v in enumerate(checks) if v}
            is_correct = (chosen == correct_indices)
            set_quiz_result(slug, qid, list(chosen), len(chosen & correct_indices), len(correct_indices))
            st.success("Great job!" if is_correct else "Close—review the options above.")
            for i, exp in enumerate(explain):
                if exp:
                    st.caption(f"• {labels[i]} — {exp}")


def notes_for_sections(slug: str, headings: List[Tuple[int,str,str]], show_heading: bool = True, mode: str = "summary", suffix: str = ""):
    """
    Render notes editor for each section.
    
    Parameters:
    - slug: Page slug identifier
    - headings: List of (depth, text, id) tuples for headings
    - show_heading: Whether to show the overall heading
    - mode: Either "summary" (show all notes in one place) or "inline" (for section-specific notes)
    - suffix: Optional suffix for widget keys to avoid duplicates
    """
    if show_heading and mode == "summary":
        st.markdown("### 🗒️ Your Notes Summary")

    notes = get_notes(slug)
    
    # For inline mode, only render the given heading (typically just one)
    if mode == "inline":
        for depth, text, hid in headings:
            # Always use expander with the section title
            with st.expander(f"📝 Add notes for: {text}", expanded=False):
                curr = notes.get(hid, "")
                new_val = st.text_area("Your notes for this section", value=curr, key=f"note_{slug}_{hid}_inline{suffix}", height=120)
                if new_val != curr:
                    set_note(slug, hid, new_val)
                    st.caption("✅ Saved locally")
    
    # For summary mode, show all sections in expanders
    else:
        has_notes = False
        for depth, text, hid in headings:
            # Only include H2 headings in the summary
            if depth != 2:
                continue
                
            curr = notes.get(hid, "")
            if curr and curr.strip():
                has_notes = True
                
            with st.expander(f"Section: {text}", expanded=curr.strip() != ""):
                new_val = st.text_area("Your notes", value=curr, key=f"note_{slug}_{hid}", height=120)
                if new_val != curr:
                    set_note(slug, hid, new_val)
                    st.caption("✅ Saved locally")
        
        if not has_notes:
            st.caption("No notes added yet. Add notes to sections as you read through the content.")
            
        # Add export/import section for notes
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Export Notes", key=f"export_notes_{slug}"):
                note_data = get_notes(slug)
                if note_data:
                    st.download_button(
                        "📥 Download Notes", 
                        data=json.dumps(note_data, indent=2),
                        file_name=f"notes-{slug}.json",
                        key=f"download_notes_{slug}"
                    )
                else:
                    st.info("No notes to export")
        
        with col2:
            uploaded = st.file_uploader("Import Notes", key=f"import_notes_{slug}", type=["json"])
            if uploaded:
                try:
                    note_data = json.loads(uploaded.getvalue().decode("utf-8"))
                    for section_id, content in note_data.items():
                        set_note(slug, section_id, content)
                    st.success("Notes imported successfully!")
                except:
                    st.error("Invalid notes file format")


def meta_preview_widget(slug: str, preset_label: Optional[str] = None, show_heading: bool = True):
    if show_heading:
        st.markdown("### 🧪 Meta Preview")
    current = get_meta(slug)
    c1, c2 = st.columns([2,1])
    with c1:
        title = st.text_input("Title", value=current.get("title",""), key=f"meta_title_{slug}")
        url = st.text_input("URL", value=current.get("url",""), key=f"meta_url_{slug}")
        desc = st.text_area("Description", value=current.get("description",""), key=f"meta_desc_{slug}", height=80)
        set_meta(slug, {"title": title, "url": url, "description": desc})
    with c2:
        st.caption(f"Title: {len(title)} chars")
        st.caption(f"Desc: {len(desc)} chars")
    # Preview box
    st.markdown("""
<div style="border:1px solid #e5e7eb; border-radius:8px; padding:12px;">
  <div style="color:#1a0dab; font-size:18px; line-height:1.3;">{title}</div>
  <div style="color:#006621; font-size:14px;">{url}</div>
  <div style="color:#545454; font-size:13px;">{desc}</div>
</div>
""".format(title=title or "Example title", url=url or "example.com/page", desc=desc or "Example description"), unsafe_allow_html=True)
