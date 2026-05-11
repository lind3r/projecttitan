"""
Phase 1 of the CurseForge availability sweep.

Enumerates every Modrinth-only mod in the pack, queries the Modrinth API for
its canonical title + slug, and writes a JSON file at scripts/cf-candidates.json
mapping each mod's packwiz name to an ordered list of candidate CurseForge
slugs.

We don't probe CurseForge here — CF sits behind Cloudflare and rejects
urllib/curl with 403 regardless of headers. The actual CF hits get done
out-of-band via WebFetch (which uses a real browser engine).
"""

from __future__ import annotations

import json
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Force UTF-8 stdout so mod titles with emoji don't crash on Windows cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MODS_DIR = REPO_ROOT / "mods"
OUTPUT_PATH = Path(__file__).resolve().parent / "cf-candidates.json"

MR_API = "https://api.modrinth.com/v2/project/"
USER_AGENT = "project-titan-cf-sweep/1.0 (lind3r@gmail.com)"


@dataclass
class Mod:
    name: str
    mr_id: str | None
    has_cf: bool
    has_url: bool


def load_mods() -> list[Mod]:
    mods: list[Mod] = []
    for path in sorted(MODS_DIR.glob("*.pw.toml")):
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        update = data.get("update", {})
        mr = update.get("modrinth")
        cf = update.get("curseforge")
        has_url = (
            "download" in data
            and "url" in data["download"]
            and not mr
            and not cf
        )
        mods.append(
            Mod(
                name=path.stem.removesuffix(".pw"),
                mr_id=mr["mod-id"] if mr else None,
                has_cf=bool(cf),
                has_url=has_url,
            )
        )
    return mods


def http_get_json(url: str) -> dict | None:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def slugify(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def candidate_cf_slugs(mr_name: str, mr_slug: str, mr_title: str) -> list[str]:
    """Ordered candidate CF slugs for this mod. De-duplicated, preserving order."""
    cands: list[str] = []

    def add(s: str) -> None:
        s = s.strip("-")
        if s and s not in cands:
            cands.append(s)

    add(slugify(mr_name))
    if mr_slug:
        add(slugify(mr_slug))
    if mr_title:
        add(slugify(mr_title))
        no_paren = re.sub(r"\(.*?\)", "", mr_title).strip()
        if no_paren:
            add(slugify(no_paren))
        # strip "API" / "Lib" suffix variants
        no_suffix = re.sub(r"\s+(API|Lib|Library)$", "", mr_title, flags=re.IGNORECASE).strip()
        if no_suffix:
            add(slugify(no_suffix))
        # "Mod Name" -> "mods-name" sometimes pluralized; rarely useful, skip
    return cands


def main() -> int:
    mods = load_mods()
    mr_only = [m for m in mods if m.mr_id and not m.has_cf]
    cf_already = [m for m in mods if m.has_cf]
    url_only = [m for m in mods if m.has_url]

    print(f"Total .pw.toml files: {len(mods)}")
    print(f"Already CF-tracked:   {len(cf_already)}")
    print(f"MR-only (to check):   {len(mr_only)}")
    print(f"URL-only:             {len(url_only)} ({', '.join(m.name for m in url_only)})")
    print()
    print("Fetching Modrinth project info...")

    result: dict[str, dict] = {}
    for i, m in enumerate(mr_only, 1):
        info = http_get_json(f"{MR_API}{m.mr_id}") or {}
        mr_title = info.get("title", "")
        mr_slug = info.get("slug", "")
        cands = candidate_cf_slugs(m.name, mr_slug, mr_title)
        result[m.name] = {
            "mr_title": mr_title,
            "mr_slug": mr_slug,
            "mr_id": m.mr_id,
            "candidates": cands,
        }
        print(f"[{i:3d}/{len(mr_only)}] {m.name:48s}  {mr_title}  -> {cands}")
        time.sleep(0.1)  # be polite to Modrinth

    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print()
    print(f"Wrote {OUTPUT_PATH}")
    print(f"{len(result)} mods queued for CurseForge probing via WebFetch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
