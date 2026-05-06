# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Titan** is the Minecraft modpack itself. The custom anchor mod (`projecttitancore`) lives in a sibling repo at `C:\Users\lind3\clones\project-titan-core\`. Don't confuse the two — modpack here, mod there.

The pack targets **Minecraft 1.21.1** on **NeoForge 21.1.228**. Distribution is **Modrinth-primary** (`.mrpack`); CurseForge export is available via packwiz when needed.

## Repo Layout

```
project-titan/
  pack.toml             # packwiz: name, MC + NeoForge versions
  index.toml            # packwiz: hashes of every tracked file
  .packwizignore        # files packwiz should NOT index (dev-only)
  mods/                 # packwiz .pw.toml metadata, ONE per mod (no JARs)
  config/               # JUNCTION → live Prism instance config/
  defaultconfigs/       # JUNCTION → live Prism instance defaultconfigs/
  kubejs/               # JUNCTION → live Prism instance kubejs/
  scripts/              # dev helpers, not shipped with the pack
  CLAUDE.md             # this file
```

The repo IS the pack source. Players never see anything from this repo directly — they install a `.mrpack` we export.

## Live ↔ Repo Bridge (Junctions)

The Prism instance at `C:\Users\lind3\AppData\Roaming\PrismLauncher\instances\projecttitan\minecraft\` has three NTFS junctions pointing back into this repo:

| Prism path | → | Repo path |
|---|---|---|
| `minecraft\config` | → | `config\` |
| `minecraft\defaultconfigs` | → | `defaultconfigs\` |
| `minecraft\kubejs` | → | `kubejs\` |

This means: edits made in-game (FTB Quests editor, mod GUI config screens) **save into the repo**. Edits made here in the repo are **immediately live** in the Prism instance. No copy step.

**Verify junctions with:**
```powershell
Get-Item "C:\Users\lind3\AppData\Roaming\PrismLauncher\instances\projecttitan\minecraft\config" | Format-List Name, LinkType, Target
```

**Recreate a junction if broken** (e.g. after launcher reinstall):
```powershell
New-Item -ItemType Junction `
  -Path   "C:\Users\lind3\AppData\Roaming\PrismLauncher\instances\projecttitan\minecraft\config" `
  -Target "C:\Users\lind3\clones\project-titan\config"
```

## packwiz Commands

```bash
packwiz mr add <slug>            # add a Modrinth mod (primary)
packwiz cf add <slug>            # CurseForge fallback
packwiz remove <name>            # drop a mod
packwiz update --all             # bump every mod to latest acceptable version
packwiz refresh                  # rehash files after manual edits
packwiz list                     # show every tracked mod
packwiz mr export                # produce .mrpack for distribution
packwiz cf export                # produce CurseForge .zip
packwiz settings acceptable-versions --add 1.21   # already added; lets us pick up mods tagged "1.21" only
```

`packwiz refresh` is the one to run after manually editing files in `config/`, `kubejs/`, etc. — it updates `index.toml` so the next export reflects current state. (Editing through the live game touches the same files via the junction; refresh covers both.)

## Mods Not Yet in packwiz

Only **Project Titan Core** (`projecttitancore-*.jar`) — our own mod, no published release artifact yet. Add via `packwiz url add` once a release is cut.

The other 81 mods all have 1-to-1 packwiz tracking matching the live install exactly, verified by JAR hash (Modrinth) or exact filename (CurseForge).

## Syncing packwiz to the Prism Install

**Workflow is one-directional.** The user adds/removes mods through Prism first (mod browser, manual JAR drops, etc.), then asks Claude to make packwiz reflect the new state. Don't drive it the other way — packwiz operations don't auto-update the dev instance's `mods/` folder.

**Audit is the first step. Always run this before adding or removing anything:**

```bash
PRISM=/c/Users/lind3/AppData/Roaming/PrismLauncher/instances/projecttitan/minecraft/mods
PACKWIZ=/c/Users/lind3/clones/project-titan/mods
ls "$PRISM" | grep -v projecttitancore | sort > /tmp/installed.txt
grep -h '^filename = ' "$PACKWIZ"/*.pw.toml | sed 's/filename = //;s/"//g' | sort > /tmp/tracked.txt
comm -23 /tmp/installed.txt /tmp/tracked.txt   # newly added (need to track)
comm -13 /tmp/installed.txt /tmp/tracked.txt   # removed/replaced (need to drop or fix)
```

**To track newly-installed mods:** run `python scripts/rebuild-pw-from-hashes.py` first — it hashes every JAR and pulls exact project+version from Modrinth. Safe to re-run anytime; it overwrites all `.pw.toml` from current ground truth. For JARs Modrinth doesn't know (CurseForge-only), ask the user for the project URL and use `packwiz cf add <url>` — URLs, not slugs, since `-y` on a guessed slug silently takes wrong matches (lesson hard-earned 2026-05-06; full reasoning in `feedback_packwiz_add.md` memory). The `vanilla-loot-addon-for-loot-integrations` slug is the existence proof that slug guessing fails for non-obvious names.

**To drop a removed mod:** `packwiz remove <name>` where `<name>` is the `.pw.toml` basename (e.g. `alexs-mobs(1.21.1)`). After, `packwiz refresh` and commit.

**After any sync:** `packwiz refresh` to re-hash the index, then commit and push. Standing authorization applies.

## Bumping Mod Versions

`packwiz update --all` checks Modrinth/CF for newer versions of every tracked mod (within the acceptable-versions filter) and updates `.pw.toml` files in place.

Caveat: this is the one operation that *creates* drift between packwiz tracking and the dev `mods/` folder, since the dev instance won't auto-fetch new JARs. After bumping, either spin up a `.mrpack` test instance to verify new versions, or manually drop new JARs into the dev instance's `mods/`.

## .mrpack Round-Trip Test

`packwiz mr export` produces `Project Titan-<version>.mrpack` at the repo root (gitignored). Importing into a fresh Prism instance via **Add Instance → Import** is the canonical end-to-end test before publishing — confirms all download URLs resolve, hashes match, and overrides land correctly. Verified working 2026-05-06; the imported instance will be missing `projecttitancore` (deferred) and won't have repo junctions, so treat it as a disposable player-simulation, not a parallel dev instance.

## World Testing Workflow

Two worlds to keep around in the Prism saves dir:
- **fresh-test** — for "does the pack boot, do quests start" smoke tests on a clean world.
- **progressed-test** — for mid-game balance work.

When you change a config in `config/` or `defaultconfigs/`:
- **`config/`** — mod-global, takes effect on next game restart for *all* worlds.
- **`defaultconfigs/`** — only seeds *new* worlds. Existing saves freeze a copy in `<save>/serverconfig/` and ignore further changes here.

To push updated `defaultconfigs/` into an existing save, run:

```powershell
scripts\sync-world-configs.ps1 -World "fresh-test"
scripts\sync-world-configs.ps1 -World "fresh-test" -DryRun   # preview only
```

## FTB Quests Editing

Quest data lives at `config\ftbquests\quests\` (junctioned, so versioned). Two editing modes:

- **In-game editor** — open the Quest Book, toggle edit mode (you need OP / single-player). Layout, descriptions, dependencies, rewards. Saves SNBT to disk on chapter close. **Best for visual layout.**
- **Direct SNBT edits** — for bulk renames, mass-rebalancing rewards, or mechanical changes across many quests.

Hot-reload exists: `/ftbquests reload` re-reads the SNBT files without a restart.

## Distribution

- **Primary:** Modrinth (`.mrpack`) — open API, no third-party-distribution toggle, broader launcher compat.
- **Secondary:** CurseForge — only if/when we want presence there. `packwiz cf export` produces a compatible zip from the same source.

Don't pick one exclusively at the source level. The pack is built once; we choose at export time.

## Build & Workflow Reminders

- Don't commit `*.jar` — packwiz tracks mods through metadata only.
- Don't edit `index.toml` by hand. Run `packwiz refresh` instead.
- Never run anything that mutates the Prism instance without remembering the junctions go both ways.
- After any change here, **boot the Prism instance once** to confirm the pack still loads — junctions can be silently broken by launcher operations.
- Standing commit/push authorization granted in the sibling `project-titan-core` repo applies here too unless the user says otherwise.

## Diagnosing Crashes

Primary log: `C:\Users\lind3\AppData\Roaming\PrismLauncher\instances\projecttitan\minecraft\logs\latest.log`

Search for `FATAL` or `ERROR` — the **first** one is always the root cause. Everything after is cascading noise.
