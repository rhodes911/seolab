from __future__ import annotations
import argparse
import json
import os
import time
from typing import Any, Dict, List

from keyword_pipeline import pipeline_run


def load_seeds_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_timestamp_dir(base_out: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = os.path.join(base_out, ts)
    os.makedirs(out, exist_ok=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Run keyword pipeline using a seeds JSON file.")
    ap.add_argument("--seeds-json", required=True, help="Path to seeds JSON (with seeds, prefix_modifiers, suffix_modifiers)")
    ap.add_argument("--out-dir", required=True, help="Base output dir; a timestamped subfolder will be created here")
    ap.add_argument("--jaccard", type=float, default=0.5, help="Jaccard similarity threshold (0.1-0.9)")
    ap.add_argument("--max-per-seed", type=int, default=200, help="Max expansions per seed")
    ap.add_argument("--max-keywords", type=int, default=1000, help="Max keywords to cluster")
    args = ap.parse_args()

    data = load_seeds_json(args.seeds_json)
    seeds: List[str] = data.get("seeds", [])
    prefix: List[str] = data.get("prefix_modifiers", [])
    suffix: List[str] = data.get("suffix_modifiers", [])

    if not seeds:
        raise SystemExit("No seeds found in JSON.")

    run_dir = ensure_timestamp_dir(args.out_dir)
    out = pipeline_run(
        seeds=seeds,
        prefix_mods=prefix,
        suffix_mods=suffix,
        jaccard_threshold=float(args.jaccard),
        max_per_seed=int(args.max_per_seed),
        max_keywords=int(args.max_keywords),
        run_dir=run_dir,
    )
    print(json.dumps({"run_dir": out["run_dir"], "counts": {
        "expanded": len(out["expanded"]),
        "normalized": len(out["normalized"]),
        "clusters": len(out["clusters"]),
        "keywords": len(out["keywords"]),
    }}, indent=2))


if __name__ == "__main__":
    main()
