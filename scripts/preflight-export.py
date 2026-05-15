#!/usr/bin/env python3
"""
Pre-export safety check. Run before `packwiz mr export` / `packwiz cf export`.

Reads index.toml, groups what's shipping by top-level dir, and flags anything
whose path matches known client-state naming conventions (Embeddium options,
JEI sort orders, Jade prefs, NeoForge -client halves, JEI world bookmarks,
ForgeEndertech per-biome state, etc.).

Exit codes:
  0 --clean, safe to export
  1 --suspect files matched, review before exporting
  2 --script error (no index.toml, parse failure, etc.)

Usage:
  python scripts/preflight-export.py
  python scripts/preflight-export.py --verbose   # list every shipping file
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.toml"

# Patterns that almost always represent per-player runtime state, not pack design.
# Add to .packwizignore (with `config/**/` prefix) when a new pattern is discovered.
SUSPECT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"-options\.(json|txt)$"), "client render/UI options"),
    (re.compile(r"sort-order", re.IGNORECASE), "personal sort order"),
    (re.compile(r"bookmark", re.IGNORECASE), "JEI/etc. bookmarks"),
    (re.compile(r"hotbar", re.IGNORECASE), "JEI cheat-mode hotbar state"),
    (re.compile(r"history", re.IGNORECASE), "lookup/search history"),
    (re.compile(r"-client\.(toml|snbt|ini|json)$"), "NeoForge -client.* per-player config"),
    (re.compile(r"^config/jei/world/"), "JEI per-world cheat state"),
    (re.compile(r"^config/jade/(plugins|sort-order)\.json$"), "Jade plugin/tooltip prefs"),
    (re.compile(r"^config/forgeendertech/Biomes/"), "ForgeEndertech per-biome scan state"),
    (re.compile(r"^config/ars_nouveau/search_index/"), "Ars Nouveau Lucene index"),
]


def classify(path: str) -> str | None:
    for pat, label in SUSPECT_PATTERNS:
        if pat.search(path):
            return label
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="list every shipping file, not just the dir summary")
    args = ap.parse_args()

    if not INDEX.exists():
        print(f"ERROR: index.toml not found at {INDEX}", file=sys.stderr)
        print("Run `packwiz refresh` first.", file=sys.stderr)
        return 2

    with INDEX.open("rb") as fh:
        data = tomllib.load(fh)

    files = data.get("files", [])
    if not files:
        print("ERROR: no [[files]] entries in index.toml", file=sys.stderr)
        return 2

    by_dir: dict[str, list[str]] = {}
    suspects: list[tuple[str, str]] = []
    for entry in files:
        path = entry.get("file", "")
        if not path:
            continue
        top = path.split("/", 1)[0] if "/" in path else "<root>"
        by_dir.setdefault(top, []).append(path)
        label = classify(path)
        if label:
            suspects.append((path, label))

    total = sum(len(v) for v in by_dir.values())
    print(f"=== packwiz export preflight -- {total} files in index.toml ===")
    print()
    for top in sorted(by_dir, key=lambda d: (-len(by_dir[d]), d)):
        print(f"  {top}/  ({len(by_dir[top])} files)")
    print()

    if args.verbose:
        print("--- full shipping manifest ---")
        for top in sorted(by_dir):
            for path in sorted(by_dir[top]):
                print(f"  {path}")
        print()

    if suspects:
        print(f"FAIL: {len(suspects)} file(s) match client-state patterns:")
        print()
        for path, label in suspects:
            print(f"  [{label}]")
            print(f"    {path}")
        print()
        print("Action: if these are intentional pack design, edit SUSPECT_PATTERNS")
        print("in this script to exclude them. Otherwise add the path (or a glob)")
        print("to .packwizignore and re-run `packwiz refresh`.")
        return 1

    print("OK: no suspect client-state patterns in shipping manifest. Safe to export.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
