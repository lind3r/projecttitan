"""
Add [update.modrinth] tracking to every currently-CF-only .pw.toml in the pack.

For each .pw.toml that has [update.curseforge] but no [update.modrinth]:
  1. Compute (or read) the JAR's sha1; query Modrinth's
     `/v2/version_file/<sha1>?algorithm=sha1` endpoint for an exact match.
  2. If a match is found, rewrite the .pw.toml as dual-tracked: keep the
     existing [update.curseforge] block, swap [download] to use the Modrinth
     CDN URL + sha512 hash, and add an [update.modrinth] block.
  3. If no hash match, fall back to a slug-based lookup via /v2/project/<slug>;
     if Modrinth has the project but a different file, leave the .pw.toml
     CF-only and report.

Result: `packwiz mr export` references mod URLs by Modrinth CDN for the newly
matched mods, eliminating raw bundling for them in the .mrpack.
"""

from __future__ import annotations

import json
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODS_DIR = REPO_ROOT / "mods"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MR_API = "https://api.modrinth.com/v2"
USER_AGENT = "project-titan-mr-lookup/1.0 (lind3r@gmail.com)"


def http_get_json(url: str) -> dict | list | None:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except (urllib.error.URLError, TimeoutError):
        return None


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


def slugify(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def lookup_modrinth_by_hash(sha1: str) -> dict | None:
    """Return version dict if Modrinth has an exact-file match, else None."""
    return http_get_json(f"{MR_API}/version_file/{sha1}?algorithm=sha1")


def lookup_modrinth_by_slug(slug: str) -> dict | None:
    """Return project dict if Modrinth has the slug, else None."""
    return http_get_json(f"{MR_API}/project/{slug}")


def find_matching_version(project_slug_or_id: str, target_filename: str) -> dict | None:
    """Search a project's versions for one whose primary file matches target_filename."""
    versions = http_get_json(f"{MR_API}/project/{project_slug_or_id}/version") or []
    for v in versions:
        for f in v.get("files", []):
            if f.get("filename") == target_filename:
                return v
    return None


def main() -> int:
    converted = 0
    not_on_mr: list[tuple[str, str]] = []      # (pw_name, reason)
    different_file: list[tuple[str, str]] = [] # mod on MR but no matching version
    skipped = 0

    paths = sorted(MODS_DIR.glob("*.pw.toml"))
    for path in paths:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        update = data.get("update", {})
        if update.get("modrinth"):
            skipped += 1
            continue
        cf = update.get("curseforge")
        if not cf:
            skipped += 1
            continue

        dl = data.get("download", {})
        sha1 = dl.get("hash") if dl.get("hash-format") == "sha1" else None
        filename = data.get("filename", "")
        name = data.get("name", "")
        pw_name = path.stem.removesuffix(".pw")

        # 1) Try Modrinth hash lookup
        match: dict | None = None
        if sha1:
            match = lookup_modrinth_by_hash(sha1)
        if match:
            project_id = match["project_id"]
            version_id = match["id"]
            primary = next((f for f in match["files"] if f.get("primary")), match["files"][0])
            mr_url = primary["url"]
            mr_hash = primary["hashes"]["sha512"]
            mr_filename = primary["filename"]
            print(f"{pw_name:48s}  HASH MATCH  project={project_id} ver={version_id}")
        else:
            # 2) Try slug fallback to confirm presence + search versions by filename
            project = None
            for s in (slugify(pw_name), slugify(name)):
                project = lookup_modrinth_by_slug(s)
                if project:
                    break
            if not project:
                # Try removing trailing "-forge" / "(...)" markers
                stripped = re.sub(r"-(forge|neoforge|fabric)$", "", slugify(pw_name))
                project = lookup_modrinth_by_slug(stripped)
            if not project:
                not_on_mr.append((pw_name, "no slug match"))
                print(f"{pw_name:48s}  NOT ON MR")
                time.sleep(0.2)
                continue
            version = find_matching_version(project["slug"], filename)
            if not version:
                different_file.append((pw_name, f"project '{project['slug']}' exists but no version with file '{filename}'"))
                print(f"{pw_name:48s}  ON MR BUT FILE MISMATCH (project={project['slug']})")
                time.sleep(0.2)
                continue
            project_id = project["id"]
            version_id = version["id"]
            primary = next((f for f in version["files"] if f.get("primary")), version["files"][0])
            mr_url = primary["url"]
            mr_hash = primary["hashes"]["sha512"]
            mr_filename = primary["filename"]
            print(f"{pw_name:48s}  SLUG MATCH  project={project['slug']} ver={version_id}")

        merged = render_dual_tracked(
            name=name,
            filename=mr_filename,
            side=data.get("side", "both"),
            url=mr_url,
            hash_format="sha512",
            hash_=mr_hash,
            mr_id=project_id,
            mr_ver=version_id,
            cf_pid=cf["project-id"],
            cf_fid=cf["file-id"],
        )
        path.write_text(merged, encoding="utf-8")
        converted += 1
        time.sleep(0.2)

    print()
    print(f"Converted: {converted}")
    print(f"Skipped (already dual-tracked or no CF): {skipped}")
    if different_file:
        print("\nOn Modrinth but no matching file (kept CF-only):")
        for n, why in different_file:
            print(f"  {n}: {why}")
    if not_on_mr:
        print("\nNot on Modrinth (kept CF-only):")
        for n, why in not_on_mr:
            print(f"  {n}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
