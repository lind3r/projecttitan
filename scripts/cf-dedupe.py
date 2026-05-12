"""
Clean up after `packwiz cf add` creating duplicate .pw.toml files.

For 12 of our wire-up adds, packwiz created a new file under the CF slug
(e.g. `mods/applied-energistics-2.pw.toml`) without removing the original
MR-tracked file (e.g. `mods/ae2.pw.toml`). The repo now has both, and both
are exported separately.

For each pair: merge the MR [update.modrinth] + [download] from the OLD file
INTO the NEW (CF-tracked) file, producing a dual-tracked .pw.toml at the
NEW path. Then delete the OLD file.

Pairing is done via scripts/cf-slug-mapping.json (cf_slug → packwiz_name).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODS_DIR = REPO_ROOT / "mods"
MAPPING_PATH = REPO_ROOT / "scripts" / "cf-slug-mapping.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def list_new_pw_files() -> list[Path]:
    """All .pw.toml files in the working tree that are NOT in git HEAD."""
    proc = subprocess.run(
        ["git", "ls-files", "mods/*.pw.toml"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    tracked = {Path(REPO_ROOT) / line.strip() for line in proc.stdout.splitlines() if line.strip()}
    on_disk = set(MODS_DIR.glob("*.pw.toml"))
    return sorted(on_disk - tracked)


def load_mapping() -> dict[str, str]:
    """cf_slug → packwiz_name (the original .pw.toml basename)."""
    with MAPPING_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    mapping = {info["cf_slug"]: name for name, info in data.items() if not name.startswith("_")}
    # packwiz sometimes derives the meta filename from the CF API's `name` field
    # instead of the page slug, so add the variants we hit during wire-up.
    mapping["almostunified"] = "almost-unified"
    mapping["codechicken-lib-1-8"] = "codechicken-lib"
    # YUNG's mods publish NeoForge 1.21.1 builds under separate -neoforge CF
    # projects (the unsuffixed ones are Forge-only for 1.21.1).
    for stem in (
        "yungs-api",
        "yungs-better-desert-temples",
        "yungs-better-dungeons",
        "yungs-better-end-island",
        "yungs-better-jungle-temples",
        "yungs-better-mineshafts",
        "yungs-better-nether-fortresses",
        "yungs-better-ocean-monuments",
        "yungs-better-strongholds",
        "yungs-better-witch-huts",
    ):
        mapping[f"{stem}-neoforge"] = stem
    return mapping


def render_dual_tracked(*, name, filename, side, url, hash_format, hash_, mr_id, mr_ver, cf_pid, cf_fid) -> str:
    return (
        f'name = "{name}"\n'
        f'filename = "{filename}"\n'
        f'side = "{side}"\n'
        f'\n'
        f'[download]\n'
        f'url = "{url}"\n'
        f'hash-format = "{hash_format}"\n'
        f'hash = "{hash_}"\n'
        f'\n'
        f'[update]\n'
        f'[update.modrinth]\n'
        f'mod-id = "{mr_id}"\n'
        f'version = "{mr_ver}"\n'
        f'[update.curseforge]\n'
        f'file-id = {cf_fid}\n'
        f'project-id = {cf_pid}\n'
    )


def main() -> int:
    cf_slug_to_pw_name = load_mapping()
    new_files = list_new_pw_files()
    print(f"Found {len(new_files)} new .pw.toml files created by wire-up.\n")

    merged = 0
    drift_count = 0
    issues: list[str] = []

    for new_path in new_files:
        cf_slug = new_path.stem.removesuffix(".pw")  # 'applied-energistics-2'
        old_name = cf_slug_to_pw_name.get(cf_slug)
        if not old_name:
            issues.append(f"{new_path.name}: no slug-mapping entry for '{cf_slug}'")
            continue
        old_path = MODS_DIR / f"{old_name}.pw.toml"
        if not old_path.exists():
            issues.append(f"{new_path.name}: old file '{old_path.name}' missing — skipping")
            continue

        with new_path.open("rb") as fh:
            new_data = tomllib.load(fh)
        with old_path.open("rb") as fh:
            old_data = tomllib.load(fh)

        new_cf = new_data.get("update", {}).get("curseforge")
        old_mr = old_data.get("update", {}).get("modrinth")
        old_dl = old_data.get("download", {})

        if not new_cf:
            issues.append(f"{new_path.name}: missing [update.curseforge]")
            continue
        if not old_mr or "url" not in old_dl or "hash" not in old_dl:
            issues.append(f"{old_path.name}: missing MR tracking or download URL")
            continue

        old_filename = old_data.get("filename", "")
        new_filename = new_data.get("filename", "")
        drift = old_filename != new_filename
        if drift:
            drift_count += 1

        merged_text = render_dual_tracked(
            name=new_data.get("name", old_data.get("name", "")),
            filename=old_filename,  # MR's filename matches MR's URL
            side=new_data.get("side", old_data.get("side", "both")),
            url=old_dl["url"],
            hash_format=old_dl.get("hash-format", "sha512"),
            hash_=old_dl["hash"],
            mr_id=old_mr["mod-id"],
            mr_ver=old_mr["version"],
            cf_pid=new_cf["project-id"],
            cf_fid=new_cf["file-id"],
        )
        new_path.write_text(merged_text, encoding="utf-8")
        old_path.unlink()

        tag = f"DRIFT  MR={old_filename!r}  CF={new_filename!r}" if drift else "OK"
        print(f"{old_path.name:48s} -> {new_path.name:48s}  {tag}")
        merged += 1

    print()
    print(f"Merged: {merged}  (of which {drift_count} have drift)")
    if issues:
        print("\nISSUES:")
        for s in issues:
            print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
