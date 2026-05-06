#!/usr/bin/env python3
"""
Audit energy-generator-related keys across config/*.toml files.

Outputs balance/energy-discovered.json — a draft list of generator outputs and
related values found by pattern matching. This is *discovery*, not curation;
the curated source of truth lives in balance/energy.json.

Strategy:
- Walk config/ recursively, parse each .toml line-by-line (no real toml lib —
  the format is simple and we want to preserve raw values + comments).
- Within each file, track section headers and capture (key, value) pairs that
  match either:
    (a) section header strongly suggests a generator (solar_generator,
        fission_reactor, alternator, stirlingGenerator, etc.) — then capture
        all numeric keys in that section, since key names vary widely
        (e.g. EnderIO uses `energetic`, `pulsating`, `vibrant` as keys);
    (b) key name itself contains an unambiguous energy-generation signal
        (fe_at_max_rpm, solarGeneration, fuelEnergy, generation, etc.) —
        catches generator data even when section is generic like [general].
- Emit JSON grouped by mod id (derived from file path).

The script is idempotent — re-run after any config / mod change.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
OUT_PATH = ROOT / "balance" / "energy-discovered.json"

# Section names that strongly indicate a generator block.
# Match against the FULL section path (after dot-splitting), so
# `[energy.stirlingGenerator]` is matched on `stirlingGenerator`.
GEN_SECTION_RE = re.compile(
    r"""(?xi)
    (?:^|\.)(
        generator
      | generation
      | alternator
      | solar(?:_?generator)?
      | advanced[_]?solar
      | bio(?:_?generator)?
      | heat[_]?generator
      | wind[_]?generator
      | gas[_]?generator
      | fission(?:_?reactor)?
      | fusion(?:_?reactor)?
      | turbine
      | stirling(?:Generator)?
      | photovoltaic\w*
      | soul[_]?engine
      | reactor
      | capacitor[_]?bank
      | accumulator
      | tesla[_]?coil
    )\b
    """
)

# Key names that on their own indicate a generator/energy output value,
# usable even when the section header is generic (like [general]).
GEN_KEY_RE = re.compile(
    r"""(?xi)
    (
        ^fe_at | ^feAt
      | generation\b
      | generator_(?:efficiency|max_output|capacity)
      | energyPer\w+
      | fuelEnergy
      | burn(?:_)?(?:Rate|Speed|Time)
      | ^solar\w*Gen
      | ^heat\w*Gen
      | ^bio\w*Gen
      | ^wind\w*Gen
      | _per_tick$ | PerTick$
      | fe_per_
    )
    """
)

# Subdirectories that produce nothing useful but lots of noise.
SKIP_DIRS = {
    "ars_nouveau",  # one .toml per spell glyph, none are generators
    "patchouli_books",
    "ftbquests",
    "ftbteams",
    "ftbchunks",
    "kubejs",
    "crash-reports",
    "logs",
    "defaultconfigs",
}

NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")
SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]")
KV_RE = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*=\s*(.+?)\s*$")


def parse_toml(path: Path):
    """Yield (section, key, value, lineno, leading_comments) tuples."""
    section = ""
    pending_comments: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            pending_comments = []
            continue
        if stripped.startswith("#"):
            pending_comments.append(stripped.lstrip("#").strip())
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1)
            pending_comments = []
            continue
        m = KV_RE.match(line)
        if not m:
            pending_comments = []
            continue
        key, val = m.group(1), m.group(2)
        yield section, key, val, lineno, list(pending_comments)
        pending_comments = []


def is_numeric(value: str) -> bool:
    return bool(NUMBER_RE.match(value))


def mod_id_for(rel_path: Path) -> str:
    """Best-effort mod id from path. config/Mekanism/x.toml -> mekanism.
    config/createaddition-common.toml -> createaddition."""
    parts = rel_path.parts
    if len(parts) > 1:
        return parts[0].lower()
    name = parts[-1].rsplit(".", 1)[0]
    name = re.sub(
        r"-(common|server|client|startup|neoforge|forge|1[._]21|mixin).*$",
        "",
        name,
    )
    return name.lower()


def scan_file(path: Path):
    hits = []
    for section, key, val, lineno, comments in parse_toml(path):
        if not is_numeric(val):
            continue
        sec_match = bool(GEN_SECTION_RE.search(section))
        key_match = bool(GEN_KEY_RE.search(key))
        if not (sec_match or key_match):
            continue
        hits.append(
            {
                "section": section,
                "key": key,
                "value": val,
                "line": lineno,
                "comment": " ".join(comments)[:240],
                "match": "section" if sec_match else "key",
            }
        )
    return hits


def main() -> int:
    if not CONFIG_DIR.is_dir():
        print(f"config dir not found: {CONFIG_DIR}", file=sys.stderr)
        return 2
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    findings: dict[str, list[dict]] = {}
    files_scanned = 0
    files_with_hits = 0
    total_hits = 0

    for path in sorted(CONFIG_DIR.rglob("*.toml")):
        rel = path.relative_to(CONFIG_DIR)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files_scanned += 1
        hits = scan_file(path)
        if not hits:
            continue
        files_with_hits += 1
        total_hits += len(hits)
        mod = mod_id_for(rel)
        findings.setdefault(mod, []).append(
            {
                "file": rel.as_posix(),
                "entries": hits,
            }
        )

    payload = {
        "_meta": {
            "files_scanned": files_scanned,
            "files_with_hits": files_with_hits,
            "total_hits": total_hits,
            "tool": "scripts/audit-energy.py",
            "note": "Discovery dump. Curated truth lives in balance/energy.json.",
        },
        "mods": dict(sorted(findings.items())),
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Scanned {files_scanned} files. "
        f"{files_with_hits} contained energy data. "
        f"{total_hits} total entries. "
        f"Wrote {OUT_PATH.relative_to(ROOT).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
