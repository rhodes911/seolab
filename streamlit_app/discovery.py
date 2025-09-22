from __future__ import annotations
import os
import glob
import re
import frontmatter
from typing import List


def scan_ellie_content(ellie_root: str, limit: int = 500) -> List[str]:
    """Traverse Ellie content and extract candidate topics from titles and H1–H3.

    Returns a deduped list of 2–7 word topics.
    """
    if not (ellie_root and os.path.isdir(ellie_root)):
        return []
    content_globs = [
        os.path.join(ellie_root, "content", "**", "*.md"),
        os.path.join(ellie_root, "content", "**", "*.mdx"),
    ]
    files: List[str] = []
    for gp in content_globs:
        files.extend(glob.glob(gp, recursive=True))
    files = files[: max(0, int(limit))]

    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    seen = set()
    out: List[str] = []
    for f in files:
        try:
            post = frontmatter.load(f)
            fm = post.metadata or {}
            seo = fm.get("seo") or {}
            parts = []
            for k in ["title", "metaTitle"]:
                v = seo.get(k) or fm.get(k)
                if isinstance(v, str) and v.strip():
                    parts.append(v.strip())
            body = getattr(post, "content", "") or ""
            for _, txt in heading_re.findall(body):
                parts.append(txt.strip())
            for t in parts:
                t2 = re.sub(r"\s*[\|–\-·•]\s*.*$", "", t).strip()
                t2 = re.sub(r"[^A-Za-z0-9\s]+", " ", t2).strip()
                t2 = re.sub(r"\s+", " ", t2)
                if 2 <= len(t2.split()) <= 7:
                    key = t2.lower()
                    if key not in seen:
                        seen.add(key)
                        out.append(t2)
        except Exception:
            continue
    return out


def extract_topics_from_text(raw_text: str) -> List[str]:
    """Extract candidate topics from pasted competitor headings/titles.

    Heuristics: heading markers, title-case lines, 2–7 words, cleaned/deduped.
    """
    raw = raw_text or ""
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    heading_like: List[str] = []
    for l in lines:
        if l.startswith(('#', '##', '###')):
            heading_like.append(l.lstrip('#').strip())
        else:
            if 2 <= len(l.split()) <= 8 and sum(1 for w in l.split() if w[:1].isupper()) >= 2:
                heading_like.append(l)
    seen = set()
    out: List[str] = []
    for t in heading_like:
        t2 = re.sub(r"\s*[\|–\-·•]\s*.*$", "", t).strip()
        t2 = re.sub(r"[^A-Za-z0-9\s]+", " ", t2).strip()
        t2 = re.sub(r"\s+", " ", t2)
        if 2 <= len(t2.split()) <= 7:
            k = t2.lower()
            if k not in seen:
                seen.add(k)
                out.append(t2)
    return out
