"""Walk mods/*.pw.toml and emit a friend-shareable modlist.

Outputs two files at the repo root:
  - MODLIST.md  — pretty markdown with links
  - MODLIST.txt — plain "Name (filename)" one per line

Run from the modpack repo root:
  python scripts/gen_modlist.py
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MODS_DIR = REPO / "mods"


def parse_mod(path: Path) -> dict:
    with path.open("rb") as f:
        data = tomllib.load(f)
    name = data.get("name", path.stem)
    filename = data.get("filename", "")
    side = data.get("side", "both")
    url = data.get("download", {}).get("url", "")

    update = data.get("update", {})
    project_url = ""
    if "modrinth" in update:
        mod_id = update["modrinth"].get("mod-id", "")
        if mod_id:
            project_url = f"https://modrinth.com/mod/{mod_id}"
    elif "curseforge" in update:
        project_id = update["curseforge"].get("project-id", "")
        if project_id:
            project_url = f"https://www.curseforge.com/projects/{project_id}"

    return {
        "name": name,
        "filename": filename,
        "side": side,
        "download_url": url,
        "project_url": project_url,
    }


def main() -> int:
    mods = sorted(
        (parse_mod(p) for p in MODS_DIR.glob("*.pw.toml")),
        key=lambda m: m["name"].lower(),
    )

    md = REPO / "MODLIST.md"
    txt = REPO / "MODLIST.txt"

    with md.open("w", encoding="utf-8") as f:
        f.write("# Project Titan — Modlist\n\n")
        f.write(f"Total mods: **{len(mods)}**  \n")
        f.write("Minecraft 1.21.1 / NeoForge 21.1.228\n\n")
        for i, m in enumerate(mods, 1):
            link = m["project_url"] or m["download_url"]
            if link:
                f.write(f"{i}. [{m['name']}]({link}) — `{m['filename']}`\n")
            else:
                f.write(f"{i}. {m['name']} — `{m['filename']}`\n")

    with txt.open("w", encoding="utf-8") as f:
        f.write(f"Project Titan — {len(mods)} mods (MC 1.21.1 / NeoForge 21.1.228)\n")
        f.write("=" * 60 + "\n\n")
        for i, m in enumerate(mods, 1):
            f.write(f"{i:3d}. {m['name']}  ({m['filename']})\n")

    print(f"Wrote {md.relative_to(REPO)} and {txt.relative_to(REPO)} ({len(mods)} mods)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
