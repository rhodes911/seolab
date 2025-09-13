from __future__ import annotations
import os, re, json
from typing import Dict, List, Tuple, Optional
import frontmatter

# Resolve project root (parent of streamlit_app) and content directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONTENT_DIR = os.path.join(BASE_DIR, "content")

HEADING_RE = re.compile(r"^(#{2,6})\s+(.+)$")

class Lesson:
    def __init__(self, slug: str, fm: dict, content: str, headings: List[Tuple[int,str,str]], content_with_anchors: Optional[str] = None, checklist_items: Optional[List[str]] = None):
        self.slug = slug
        self.frontmatter = fm
        self.content = content
        self.headings = headings
        self.content_with_anchors = content_with_anchors or content
        self.checklist_items = checklist_items or []


def _slug_for(path: str) -> str:
    return path.replace(CONTENT_DIR + os.sep, "").replace("\\", "/").rsplit(".",1)[0]


def _extract_headings(md: str) -> List[Tuple[int,str,str]]:
    heads = []
    for line in md.splitlines():
        m = HEADING_RE.match(line)
        if not m: continue
        depth = len(m.group(1))
        text = m.group(2).strip()
        hid = re.sub(r"[^a-z0-9\s-]", "", text.lower())
        hid = re.sub(r"\s+", "-", hid)
        heads.append((depth, text, hid))
    return heads


def _inject_anchors(md: str, headings: List[Tuple[int, str, str]]) -> str:
    if not headings:
        return md
    lines = md.splitlines()
    out = []
    hi = 0
    for line in lines:
        m = HEADING_RE.match(line)
        if m and hi < len(headings):
            depth, text, hid = headings[hi]
            # Only add anchors for matching text to keep alignment
            if text == m.group(2).strip():
                out.append(f"{line} <a id=\"{hid}\"></a>")
                hi += 1
                continue
        out.append(line)
    return "\n".join(out)


CHECK_ITEM_RE = re.compile(r"^\s*-\s*\[[ xX]?\]\s+(.*)$")
def _extract_checklist(md: str, headings: List[Tuple[int,str,str]]) -> List[str]:
    # Find the region under an H2 'Checklist' until next H2
    lines = md.splitlines()
    items: List[str] = []
    in_section = False
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            depth = len(m.group(1))
            text = m.group(2).strip().lower()
            if depth == 2 and text == "checklist":
                in_section = True
                continue
            if depth == 2 and in_section:
                break
        if in_section:
            im = CHECK_ITEM_RE.match(line)
            if im:
                items.append(im.group(1).strip())
    return items


def load_index() -> Dict:
    lessons: List[Lesson] = []
    for root, _, files in os.walk(CONTENT_DIR):
        for f in files:
            if not f.endswith((".md", ".mdx")): continue
            full = os.path.join(root, f)
            post = frontmatter.load(full)
            slug = _slug_for(full)
            heads = _extract_headings(post.content)
            content_with_anchors = _inject_anchors(post.content, heads)
            checklist_items = _extract_checklist(post.content, heads)
            lessons.append(Lesson(slug, post.metadata, post.content, heads, content_with_anchors, checklist_items))
    # sort by category then order then title
    lessons.sort(key=lambda l: (l.frontmatter.get("category",""), l.frontmatter.get("order", 0), l.frontmatter.get("title","")))
    by_slug = {l.slug: l for l in lessons}
    by_cat: Dict[str,List[str]] = {}
    all_slugs: List[str] = []
    for l in lessons:
        all_slugs.append(l.slug)
        c = l.frontmatter.get("category","uncategorized")
        by_cat.setdefault(c, []).append(l.slug)
    return {"lessons": lessons, "by_slug": by_slug, "by_cat": by_cat, "all": all_slugs}


def prev_next(index: Dict, slug: str):
    all_slugs: List[str] = index["all"]
    i = all_slugs.index(slug) if slug in all_slugs else -1
    prev = index["by_slug"].get(all_slugs[i-1]) if i > 0 else None
    nxt = index["by_slug"].get(all_slugs[i+1]) if 0 <= i < len(all_slugs)-1 else None
    return prev, nxt
