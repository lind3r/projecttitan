"""
One-shot helper: rebuild mods/*.pw.toml from the JARs actually installed in
the Prism instance, using Modrinth's hash-lookup API.

Why: an earlier batch packwiz add with -y produced wrong matches (search
ranking picked addons or unrelated projects with similar names). This script
goes from the source of truth (the actual JAR file) to the exact Modrinth
project + version, so the tracked set is guaranteed to match the install.

Outputs a list of JARs Modrinth doesn't know — those are CurseForge-only and
need a fallback step (packwiz cf add or a URL from the user).
"""

import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PRISM_MODS = str(Path.home() / "AppData/Roaming/PrismLauncher/instances/projecttitan/minecraft/mods")
OUT_MODS = str(Path(__file__).resolve().parent.parent / "mods")
SKIP = {"projecttitancore-0.1.0.jar"}  # our own mod, tracked separately via GitHub release
USER_AGENT = "project-titan/0.1 (packwiz-bootstrap)"


def post_json(url, body):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def hash_jar(path):
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha1(data).hexdigest()


def main():
    jars = {}
    for fn in sorted(os.listdir(PRISM_MODS)):
        if fn in SKIP or not fn.endswith(".jar"):
            continue
        jars[fn] = hash_jar(os.path.join(PRISM_MODS, fn))

    print(f"hashing {len(jars)} JARs done")

    versions = post_json(
        "https://api.modrinth.com/v2/version_files",
        {"hashes": list(jars.values()), "algorithm": "sha1"},
    )

    project_ids = sorted({v["project_id"] for v in versions.values()})
    ids_param = urllib.parse.quote(json.dumps(project_ids))
    projects_list = get_json(f"https://api.modrinth.com/v2/projects?ids={ids_param}")
    projects = {p["id"]: p for p in projects_list}

    print(f"matched {len(versions)} of {len(jars)} on Modrinth")

    matched, unmatched = [], []
    for fn, sha1 in jars.items():
        if sha1 not in versions:
            unmatched.append(fn)
            continue
        v = versions[sha1]
        proj = projects[v["project_id"]]
        file_info = next(f for f in v["files"] if f["hashes"]["sha1"] == sha1)

        slug = proj["slug"]
        pw_path = os.path.join(OUT_MODS, f"{slug}.pw.toml")
        title = proj["title"].replace('"', '\\"')
        content = (
            f'name = "{title}"\n'
            f'filename = "{file_info["filename"]}"\n'
            f'side = "both"\n'
            f'\n'
            f'[download]\n'
            f'url = "{file_info["url"]}"\n'
            f'hash-format = "sha512"\n'
            f'hash = "{file_info["hashes"]["sha512"]}"\n'
            f'\n'
            f'[update]\n'
            f'[update.modrinth]\n'
            f'mod-id = "{proj["id"]}"\n'
            f'version = "{v["id"]}"\n'
        )
        with open(pw_path, "w", encoding="utf-8") as f:
            f.write(content)
        matched.append((fn, slug))

    print()
    print("=== matched ===")
    for fn, slug in matched:
        print(f"  {fn}  ->  {slug}")
    print()
    print("=== unmatched (Modrinth has no record of these JARs) ===")
    for fn in unmatched:
        print(f"  {fn}")
    print()
    print(f"Wrote {len(matched)} .pw.toml files. {len(unmatched)} need CurseForge fallback.")


if __name__ == "__main__":
    main()
