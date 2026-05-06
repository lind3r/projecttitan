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

## Mods Backlog (To Add)

Queued for the next sync round — install in Prism first, then run the packwiz sync workflow below.

- Almost Unified
- Chisel Modern
- Crafting Station: J/EMI Edition Updated
- Crafting Tweaks
- Cosmetic Armor Reworked
- Draconic Evolution
- Enchantment Descriptions
- ExtendedAE
- FindMe
- Flux Networks
- Functional Storage
- Gateways to Eternity
- GuideME
- Hostile Neural Networks
- Industrial Foregoing
- Inventory Essentials
- Inventory Sorter
- Item Collectors
- ME Requester
- Metal Barrels
- Mining Gadgets
- Mob Grinding Utils
- Oritech
- Overflowing Bars
- Pick Up Notifier
- Simple Magnets
- Spice of Life: Carrot Edition
- Tool Belt
- Trash Cans

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

### Quest Design Vision

The pack targets experienced modded MC players who expect to scale heavily. First-time-modded-MC accessibility is **not** a goal.

**Quest philosophy:**
- Few quests, high signal. Quests are *directions to go*, not exhaustive checklists.
- Every reward must be substantial enough to justify building the machine and engaging with the mod.
- "Introduce a mod" quests require both *building* the machine AND *using* it (e.g., obtain a sample of its output) — proving the system is live, not just crafted.
- **Don't use `forge_energy` tasks** to gate quests on FE generation — Titan Core crafting recipes already require energy, the gate is redundant. (Stripped from the energy chapter for this reason.)

**Main questline (`the_titan_core` chapter):**
- Strictly linear: T1 → T2 → ... → T10 (10 tiers, locked 2026-05-07).
- Demand targets and ceiling coverage per tier live in `balance/energy.md`. Reward scaling tracks that demand curve.
- Costs scale aggressively (T1 reward is 64×9 iron blocks — that level of expense is intentional, not a bug).
- **Trophy items are gone.** The mod no longer ships `projecttitancore:trophy_tier_X`, so the `the_titan_core.snbt` quests still gating on those items are broken until re-tasked. Plan: replace with events emitted by the Titan Core block on tier transitions; tier-ups can also trigger world changes. Defer wiring this until `projecttitancore` exposes the event hook.

**Side chapters (`energy_generation`, `resource_generation`, `magic`, `gearing_up`, `strong_foes`, `travel_the_world`, `other`):**
- Hub-and-spoke: one entry quest (checkmark task, hexagon shape) fans out to multiple mod-specific paths.
- Paths are independent (OR-style) — players can do one, several, or all to stack rewards.
- Spokes are positioned at x=4, y=−5 to +5 in increments of 2.
- Energy generation example: hub → Create alternator path → Mekanism heat-gen path → Ender IO Stirling path.

**Authoring conventions:**
- User does visual layout polish in the in-game editor (faster visually) — Claude matches SNBT to whatever the editor produces.
- Claude does bulk SNBT/lang edits, dependency wiring, mass rebalances, and content authoring.
- Loop: Claude edits SNBT → user runs `/ftbquests reload` → user reports issues → Claude fixes.
- **Verify item IDs against the live JAR before writing SNBT.** Pattern: `unzip -p <mods/MyMod.jar> assets/<modid>/lang/en_us.json | grep -oE '"item\.<modid>\.[a-z_]+":\s*"[^"]*"'`. The `Bash(unzip *)` permission is allowed in `.claude/settings.local.json` so peeking is unrestricted.
- Quest IDs are 16 hex characters. Generate fresh ones when writing new quests; never reuse. **Watch out:** the in-game editor may regenerate Claude-authored IDs on next save — re-read SNBT after the user has touched a chapter, and update lang keys to match.
- All titles, subtitles, and descriptions live in `config/ftbquests/quests/lang/en_us.snbt`, not inline in chapter SNBT. Multi-line descriptions use `quest.<id>.description.0`, `.description.1`, etc.

### Quest Backlog

**Status snapshot (2026-05-06):** 7 chapters, 38 quests shipped. All major mods have at least one starter quest. Iteration phase from here — user testing in-game, Claude patching IDs/balance/layout based on feedback.

#### energy_generation
- [x] Hub — Spark of Industry
- [x] Create — Kinetic Conversion (Alternator)
- [x] Mekanism — Industrial Heat (Heat Generator)
- [x] EnderIO — Stirling Cycle (Stirling Generator)
- [x] Mekanism — Solar Array (Solar Generator)
- [x] EnderIO — Photovoltaic (Energetic Photovoltaic Module)
- [ ] Mekanism — Gas-Burning Generator (mid-tier, requires Ethene)
- [ ] Create — Steam Engine (1.21+ Create's mid-game power)

#### resource_generation
- [x] Hub — Productive Earth
- [x] Mekanism — Strip Without the Strip (Digital Miner)
- [x] Mekanism — Quintuple Down (5x ore chain)
- [x] Create — Pressing Matters (Press + Mixer)
- [x] AE2 — Bootstrapping AE2 (Inscriber)
- [ ] Create — Crushing Wheels (ore doubling alternative)
- [ ] Mekanism — Quantum Entangloporter (item shuttling)
- [ ] AE2 — first ME network (Controller + Drive + Crafting Terminal as separate quest)

#### gearing_up
- [x] Hub — Sharpen Up
- [x] Apotheosis — First Cut (Gem Cutting Table)
- [x] Apotheosis — Forge & Reforge (Reforging Table)
- [x] Apothic Enchanting — Beyond Vanilla (Hellshelf + Endshelf)
- [x] Mekanism — Take Flight (Jetpack)
- [x] Mekanism — Atomic Disassembler
- [x] Sophisticated Backpacks — Pack Mule (Iron Backpack)
- [ ] Apotheosis — Salvaging Table
- [ ] Mekanism — MekaSuit Helmet (start of MekaSuit progression)
- [ ] Create — Copper Backtank + Diving Helmet

#### magic
- [x] Hub — Mana Spring
- [x] Inscribe & Cast — Scribe's Table + Mage's Spell Book
- [x] The Workshop — Enchanting Apparatus + Imbuement Chamber
- [x] Mana on Tap — Source Jar + Relay + Volcanic Sourcelink
- [x] First Ritual — Ritual Brazier + Ritual of Awakening
- [x] Cultivate — Magebloom seed + harvest
- [ ] Ars Nouveau — Drygmy Charm / familiar pet (mob loot automation)
- [ ] Ars Nouveau — Mage Robes set (full curio loadout)

#### strong_foes
- [x] Hub — Worthy Adversary
- [x] Apotheosis — Summon a Boss (Boss Summoner)
- [x] Apothic Spawners — Spawner Husbandry
- [x] Cataclysm — Slay the Harbinger
- [x] Cataclysm — Slay the Leviathan
- [x] Alex's Mobs — Hunt the Bone Serpent
- [ ] Cataclysm — Slay the Ender Guardian
- [ ] Cataclysm — Slay the Netherite Monstrosity / Ignis
- [ ] Apotheosis — Kill an affixed mob (any rare-tier)

#### travel_the_world
- [x] Hub — Distant Horizons
- [x] Visit the Nether
- [x] Visit the End
- [x] Find a Stronghold (Yung's Better Strongholds)
- [x] Amethyst Rainforest (Terralith biome)
- [x] Craft a Globe (Supplementaries)
- [ ] Towns and Towers — find a populated town
- [ ] When Dungeons Arise — find a dungeon structure
- [ ] Tectonic — visit a Tectonic-only biome

#### other (QoL/utility)
- [x] Hub — Quality of Life
- [x] Farmers Delight — Hot Kitchen (Cooking Pot + Skillet)
- [x] Supplementaries — Worldly Trinkets (Sack + Globe)
- [x] Quark — Pocket Tools (Backpack + Trowel)
- [x] Sophisticated Storage — Tier Up Storage (Iron Barrel)
- [x] Pipez — Pipework (Item Pipe + Improved Upgrade)
- [ ] Chipped — decorative blocks intro
- [ ] Macaws (doors/windows/roofs/etc.) — building blocks
- [ ] Curios — equip any curio item

#### the_titan_core (main spine)

**10 tiers locked 2026-05-07.** Demand targets per tier in `balance/energy.md`. Trophies are gone — the existing T1-T3 quest SNBT still references `projecttitancore:trophy_tier_X` items that the mod no longer exposes, so all three are broken until re-tasked once the tier-transition event hook lands.

| Tier | Demand FE/t | Existing reward (re-task pending) |
|---|---:|---|
| T1  |        1,000 | 64×9 iron blocks (was trophy_tier_1) |
| T2  |        4,000 | 16 gold blocks (was trophy_tier_2)   |
| T3  |       16,000 | 16 diamond blocks (was trophy_tier_3) |
| T4  |       60,000 | TBD                                   |
| T5  |      250,000 | TBD                                   |
| T6  |    1,000,000 | TBD                                   |
| T7  |    4,000,000 | TBD                                   |
| T8  |   15,000,000 | TBD                                   |
| T9  |   60,000,000 | TBD                                   |
| T10 |  200,000,000 | TBD (Fusion-class endgame)            |

- [ ] Re-task T1-T3 quests once `projecttitancore` ships the tier-transition event hook.
- [ ] Author T4-T10 quests as the mod content for each tier becomes available.

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
