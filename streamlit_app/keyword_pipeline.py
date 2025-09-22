from __future__ import annotations
import os
import re
import json
import time
import csv
from typing import List, Dict, Tuple, Any


# 1) Seed expansion
def expand_seeds(
    seeds: List[str],
    prefix_mods: List[str] | None = None,
    suffix_mods: List[str] | None = None,
    max_per_seed: int | None = 200,
) -> List[str]:
    """
    Create variants for each seed by prepending/appending modifiers.
    Keeps it small and safe by limiting total expansions per seed.
    """
    prefix_mods = [m.strip() for m in (prefix_mods or []) if m.strip()]
    suffix_mods = [m.strip() for m in (suffix_mods or []) if m.strip()]
    out: List[str] = []
    for seed in [s.strip() for s in seeds if s and s.strip()]:
        # Always include the raw seed
        out.append(seed)
        variants: List[str] = []
        for p in prefix_mods:
            variants.append(f"{p} {seed}")
        for s in suffix_mods:
            variants.append(f"{seed} {s}")
        # Cross-combine one prefix + one suffix
        for p in prefix_mods:
            for s in suffix_mods:
                variants.append(f"{p} {seed} {s}")
                if max_per_seed and len(variants) >= max_per_seed:
                    break
            if max_per_seed and len(variants) >= max_per_seed:
                break
        # Apply per-seed max
        if max_per_seed is not None:
            variants = variants[:max_per_seed]
        out.extend(variants)
    return out


# 2) Normalize + dedupe
_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^a-z0-9\s-]")

def normalize_keyword(k: str) -> str:
    k = k.strip().lower()
    k = _PUNCT_RE.sub("", k)
    k = _WS_RE.sub(" ", k)
    return k.strip()


def normalize_and_dedupe(keywords: List[str]) -> List[str]:
    seen = set()
    out = []
    for k in keywords:
        n = normalize_keyword(k)
        if not n:
            continue
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


# 3) Simple clustering via Jaccard similarity on token sets
def _token_set(s: str) -> set:
    return set(s.split())


def cluster_keywords(keywords: List[str], threshold: float = 0.5, max_keywords: int = 1000) -> Tuple[List[Dict[str, Any]], List[List[int]]]:
    """
    Naive O(n^2) clustering by Jaccard similarity. Suitable for <= ~1000 items.
    Returns:
      - rows: list of dicts {id, keyword, tokens}
      - clusters: list of lists of row indices belonging to each cluster
    """
    if not keywords:
        return [], []
    if len(keywords) > max_keywords:
        keywords = keywords[:max_keywords]
    rows = [{"id": i, "keyword": k, "tokens": _token_set(k)} for i, k in enumerate(keywords)]
    n = len(rows)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        ai = rows[i]["tokens"]
        for j in range(i + 1, n):
            bj = rows[j]["tokens"]
            inter = len(ai & bj)
            if inter == 0:
                continue
            union_size = len(ai | bj)
            jacc = inter / union_size if union_size else 0.0
            if jacc >= threshold:
                union(i, j)

    # Build clusters
    clusters_map: Dict[int, List[int]] = {}
    for i in range(n):
        r = find(i)
        clusters_map.setdefault(r, []).append(i)
    clusters = list(clusters_map.values())
    # Sort clusters by size desc
    clusters.sort(key=lambda c: len(c), reverse=True)
    return rows, clusters


# 4) Intent detection (heuristic)
INTENT_PATTERNS = {
    "informational": [r"\bhow\b", r"\bwhat\b", r"\bguide\b", r"\bdefinition\b", r"\bexamples\b", r"\bwhy\b"],
    "commercial": [r"\bbest\b", r"\btop\b", r"\bvs\b", r"\breview\b", r"\bcompare\b", r"\balternatives?\b"],
    "transactional": [r"\bbuy\b", r"\bprice\b", r"\bcost\b", r"\bnear me\b", r"\bdeal\b", r"\bdiscount\b", r"\border\b"],
    "navigational": [r"\.com\b", r"\.co\b", r"\bhomepage\b", r"\blogin\b", r"\bcontact\b"],
}


def detect_intent(keyword: str) -> str:
    for label, pats in INTENT_PATTERNS.items():
        for pat in pats:
            if re.search(pat, keyword):
                return label
    return "unspecified"


# 5) Scoring (simple heuristic, placeholders for future metrics)
def score_keyword(keyword: str, cluster_size: int, matched_modifiers: int = 0) -> float:
    words = len(keyword.split())
    long_tail_bonus = 0.5 if words >= 3 else 0.0
    cluster_penalty = min(cluster_size, 10) * 0.05  # larger cluster -> more overlap/competition
    modifier_bonus = min(matched_modifiers, 3) * 0.2
    base = 1.0 + long_tail_bonus + modifier_bonus - cluster_penalty
    return round(max(base, 0.0), 3)


def compute_modifier_hits(keyword: str, prefix_mods: List[str], suffix_mods: List[str]) -> int:
    count = 0
    for m in prefix_mods:
        if m and m in keyword:
            count += 1
    for m in suffix_mods:
        if m and m in keyword:
            count += 1
    return count


# 6) Export helpers
def create_run_folder(base_dir: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(base_dir, "reports", "keyword_runs", ts)
    os.makedirs(path, exist_ok=True)
    return path


def write_json(path: str, name: str, data: Any):
    f = os.path.join(path, f"{name}.json")
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)


def write_csv(path: str, name: str, rows: List[Dict[str, Any]]):
    if not rows:
        return
    f = os.path.join(path, f"{name}.csv")
    fieldnames = list(rows[0].keys())
    with open(f, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def pipeline_run(
    seeds: List[str],
    prefix_mods: List[str],
    suffix_mods: List[str],
    jaccard_threshold: float = 0.5,
    max_per_seed: int | None = 200,
    max_keywords: int = 1000,
    base_dir: str | None = None,
    run_dir: str | None = None,
) -> Dict[str, Any]:
    """
    End-to-end run returning all intermediate artifacts for transparency.
    """
    base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if run_dir:
        # If explicit run_dir provided, ensure it exists
        os.makedirs(run_dir, exist_ok=True)
    else:
        run_dir = create_run_folder(base_dir)

    expanded = expand_seeds(seeds, prefix_mods, suffix_mods, max_per_seed=max_per_seed)
    normalized = normalize_and_dedupe(expanded)
    rows, clusters = cluster_keywords(normalized, threshold=jaccard_threshold, max_keywords=max_keywords)

    # Build keyword records with intent and score
    prefix_mods = [m for m in (prefix_mods or []) if m]
    suffix_mods = [m for m in (suffix_mods or []) if m]
    cluster_index: Dict[int, int] = {}
    for ci, member_ids in enumerate(clusters):
        for idx in member_ids:
            cluster_index[idx] = ci

    keywords_out: List[Dict[str, Any]] = []
    for r in rows:
        idx = r["id"]
        kw = r["keyword"]
        ci = cluster_index.get(idx, -1)
        cluster_size = len(clusters[ci]) if ci >= 0 else 1
        intent = detect_intent(kw)
        mod_hits = compute_modifier_hits(kw, prefix_mods, suffix_mods)
        score = score_keyword(kw, cluster_size=cluster_size, matched_modifiers=mod_hits)
        keywords_out.append({
            "keyword": kw,
            "cluster_id": ci,
            "cluster_size": cluster_size,
            "intent": intent,
            "modifier_hits": mod_hits,
            "score": score,
            # Placeholders for future enrichments
            "volume": None,
            "difficulty": None,
            "cpc": None,
        })

    # Sort by score desc then cluster size asc
    keywords_out.sort(key=lambda x: (-x["score"], x["cluster_size"], x["keyword"]))

    # Persist artifacts
    write_json(run_dir, "params", {
        "seeds": seeds,
        "prefix_mods": prefix_mods,
        "suffix_mods": suffix_mods,
        "jaccard_threshold": jaccard_threshold,
        "max_per_seed": max_per_seed,
        "max_keywords": max_keywords,
    })
    write_json(run_dir, "expanded_raw", expanded)
    write_json(run_dir, "normalized", normalized)
    write_json(run_dir, "clusters", clusters)
    write_csv(run_dir, "keywords_scored", keywords_out)

    return {
        "run_dir": run_dir,
        "expanded": expanded,
        "normalized": normalized,
        "rows": rows,
        "clusters": clusters,
        "keywords": keywords_out,
    }
