"""
Wire CurseForge tracking onto every Modrinth-only mod in the pack.

Reads scripts/cf-slug-mapping.json (the verified slug→CF mirror table) and runs
`packwiz cf add <cf-url>` for each mod that still has Modrinth-only tracking,
declining the dependency prompt (we already track deps separately).

Before each add: records the .pw.toml's current `filename`. After the add:
re-reads the new `filename` and compares — any drift means CF picked a
different file than what we had on Modrinth, and we surface that loudly.

The script is idempotent. Re-runs skip mods that are already CF-tracked.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODS_DIR = REPO_ROOT / "mods"
MAPPING_PATH = Path(__file__).resolve().parent / "cf-slug-mapping.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_mapping() -> dict[str, dict]:
    with MAPPING_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_pw(name: str) -> dict | None:
    path = MODS_DIR / f"{name}.pw.toml"
    if not path.exists():
        return None
    with path.open("rb") as fh:
        return tomllib.load(fh)


def is_cf_tracked(pw: dict) -> bool:
    return bool(pw.get("update", {}).get("curseforge"))


def run_cf_add(cf_url: str) -> tuple[bool, str]:
    """Run `packwiz cf add`. Decline the dep prompt by piping 'n\\n'.
    Returns (ok, stdout+stderr).
    """
    proc = subprocess.run(
        ["packwiz", "cf", "add", cf_url],
        cwd=REPO_ROOT,
        input="n\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    # packwiz returns 0 on the prompt-decline path too. Success when output
    # contains "successfully added"; soft-failures land in stdout.
    ok = "successfully added" in output and proc.returncode == 0
    return ok, output.strip()


def main() -> int:
    mapping = load_mapping()
    print(f"Loaded mapping for {len(mapping)} mods.\n")

    skipped: list[str] = []
    converted: list[tuple[str, str, str]] = []   # (name, old filename, new filename)
    drifted: list[tuple[str, str, str]] = []     # filename mismatched after add
    failed: list[tuple[str, str]] = []           # (name, error output)
    missing_pw: list[str] = []

    for i, (name, info) in enumerate(mapping.items(), 1):
        pw = load_pw(name)
        if pw is None:
            print(f"[{i:3d}/{len(mapping)}] {name:48s}  -- no .pw.toml found, skipping")
            missing_pw.append(name)
            continue
        if is_cf_tracked(pw):
            print(f"[{i:3d}/{len(mapping)}] {name:48s}  -- already CF-tracked, skipping")
            skipped.append(name)
            continue

        old_filename = pw.get("filename", "")
        cf_slug = info["cf_slug"]
        cf_url = f"https://www.curseforge.com/minecraft/mc-mods/{cf_slug}"

        print(f"[{i:3d}/{len(mapping)}] {name:48s}  ->  /{cf_slug}", end=" ... ", flush=True)
        ok, output = run_cf_add(cf_url)
        if not ok:
            # extract the most informative line
            short = next(
                (
                    line
                    for line in output.splitlines()
                    if line.strip()
                    and "successfully added" not in line
                    and "Would you like" not in line
                ),
                output[:160],
            )
            print(f"FAILED ({short!r})")
            failed.append((name, short))
            time.sleep(0.5)
            continue

        new_pw = load_pw(name)
        new_filename = (new_pw or {}).get("filename", "")
        if new_filename == old_filename:
            print(f"OK ({new_filename})")
            converted.append((name, old_filename, new_filename))
        else:
            print(f"DRIFT ({old_filename!r} -> {new_filename!r})")
            drifted.append((name, old_filename, new_filename))
        time.sleep(0.5)  # be polite to CF API

    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"Converted cleanly (same filename):  {len(converted)}")
    print(f"Converted with version DRIFT:        {len(drifted)}")
    print(f"FAILED:                              {len(failed)}")
    print(f"Skipped (already CF-tracked):       {len(skipped)}")
    print(f"Missing .pw.toml:                   {len(missing_pw)}")
    print()

    if drifted:
        print("Version-drift cases — CF picked a different file than MR had tracked:")
        for name, old_f, new_f in drifted:
            print(f"  {name:48s}  {old_f}  -->  {new_f}")
        print()

    if failed:
        print("Failed adds — need manual intervention:")
        for name, err in failed:
            print(f"  {name:48s}  {err}")
        print()

    if missing_pw:
        print(f"Mapping lists mods with no .pw.toml: {missing_pw}")
        print()

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
