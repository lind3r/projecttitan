"""
After wire-up: restore the [update.modrinth] block + Modrinth [download] URL
onto each wire-up mod, producing a dual-tracked .pw.toml.

For each .pw.toml that currently has [update.curseforge] but no [update.modrinth]:
  - Pull the pre-wire-up version from `git show HEAD:mods/<name>.pw.toml`
  - If that version had [update.modrinth] + a Modrinth download URL, merge:
    keep CF's [update.curseforge] AND restore MR's [download] + [update.modrinth].
  - The result: `packwiz mr export` uses the Modrinth CDN URL (clean manifest),
    `packwiz cf export` uses the CF project+file IDs (clean manifest).

For drift mods (CF picked a different file than MR had tracked), the merged file
ships MR's original version to Modrinth users and CF's picked version to
CurseForge users — same mod, different version. Not strict binary parity but
keeps both packs free of bundled-mod bloat.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODS_DIR = REPO_ROOT / "mods"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def git_show_head(path: Path) -> str | None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def merge_pw(current_text: str, head_text: str) -> tuple[str | None, str]:
    """Return (merged_text, reason). merged_text is None if no merge applied."""
    current = tomllib.loads(current_text)
    head = tomllib.loads(head_text)

    current_cf = current.get("update", {}).get("curseforge")
    current_mr = current.get("update", {}).get("modrinth")
    head_mr = head.get("update", {}).get("modrinth")
    head_dl = head.get("download", {})

    if current_mr and current_cf:
        return None, "already dual-tracked"
    if not current_cf:
        return None, "no CF tracking on current"
    if not head_mr:
        return None, "HEAD had no MR tracking (was CF-only or URL-only)"
    if "url" not in head_dl or "hash" not in head_dl:
        return None, "HEAD's download block missing url/hash"

    name = current.get("name", head.get("name", ""))
    filename = head.get("filename", "")  # MR's filename
    side = current.get("side", head.get("side", "both"))

    mr_url = head_dl["url"]
    mr_hash = head_dl["hash"]
    mr_hash_format = head_dl.get("hash-format", "sha512")
    mr_mod_id = head_mr["mod-id"]
    mr_version = head_mr["version"]

    cf_project_id = current_cf["project-id"]
    cf_file_id = current_cf["file-id"]

    merged = (
        f'name = "{name}"\n'
        f'filename = "{filename}"\n'
        f'side = "{side}"\n'
        f'\n'
        f'[download]\n'
        f'url = "{mr_url}"\n'
        f'hash-format = "{mr_hash_format}"\n'
        f'hash = "{mr_hash}"\n'
        f'\n'
        f'[update]\n'
        f'[update.modrinth]\n'
        f'mod-id = "{mr_mod_id}"\n'
        f'version = "{mr_version}"\n'
        f'[update.curseforge]\n'
        f'file-id = {cf_file_id}\n'
        f'project-id = {cf_project_id}\n'
    )
    return merged, "merged"


def main() -> int:
    converted = 0
    drift_count = 0
    skipped: dict[str, int] = {}

    for path in sorted(MODS_DIR.glob("*.pw.toml")):
        current_text = path.read_text(encoding="utf-8")
        head_text = git_show_head(path)
        if head_text is None:
            skipped["not-in-HEAD"] = skipped.get("not-in-HEAD", 0) + 1
            continue

        merged, reason = merge_pw(current_text, head_text)
        if merged is None:
            skipped[reason] = skipped.get(reason, 0) + 1
            continue

        current_filename = tomllib.loads(current_text).get("filename", "")
        head_filename = tomllib.loads(head_text).get("filename", "")
        if current_filename != head_filename:
            drift_count += 1
            tag = f"DRIFT  MR='{head_filename}' CF='{current_filename}'"
        else:
            tag = "OK"

        path.write_text(merged, encoding="utf-8")
        converted += 1
        print(f"{path.name:50s}  {tag}")

    print()
    print(f"Converted to dual-tracked: {converted}  (of which {drift_count} have version drift)")
    for reason, count in sorted(skipped.items()):
        print(f"Skipped ({reason}): {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
