from __future__ import annotations
from typing import List, Tuple
import re
import streamlit as st
import os

CALLOUT_RE = re.compile(r"^>\s*\[!(NOTE|TIP|INFO|WARNING|DANGER)\]\s*(.*)$", re.IGNORECASE)

def inject_styles():
    # Load external stylesheet and inject helper classes
    css_path = os.path.join(os.getcwd(), "streamlit_app", "styles.css")
    css = ""
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
    except Exception:
        pass
    st.markdown(
        f"""
        <style>
        {css}
        .callout {{ border-left: 4px solid var(--primary-color,#2563eb); padding: .75rem 1rem; background: rgba(37,99,235,.05); border-radius: .5rem; margin: .75rem 0; }}
        .callout.tip {{ border-color: #10b981; background: rgba(16,185,129,.06); }}
        .callout.info {{ border-color: #3b82f6; background: rgba(59,130,246,.06); }}
        .callout.warn {{ border-color: #f59e0b; background: rgba(245,158,11,.06); }}
        .callout.danger {{ border-color: #ef4444; background: rgba(239,68,68,.06); }}
        .toc a {{ text-decoration: none; color: inherit; }}
        .toc .lvl-2 {{ margin-left: .25rem; }}
        .toc .lvl-3 {{ margin-left: 1.25rem; opacity: .9; }}
        .toc .lvl-4 {{ margin-left: 2rem; opacity: .8; }}
        .muted {{ color: rgba(0,0,0,.6); }}
        .kbd {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; padding: 2px 6px; border: 1px solid #e5e7eb; border-bottom-width: 2px; border-radius: 6px; background: #f9fafb; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


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
            out_val = st.checkbox("", key=f"chk_{slug}_{i}", value=values[i] if i < len(values) else False)
        with c2:
            st.write(item)
        out.append(out_val)
    return out
