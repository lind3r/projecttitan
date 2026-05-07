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

The other 119 mods all have 1-to-1 packwiz tracking matching the live install exactly, verified by JAR hash (Modrinth) or exact filename (CurseForge).

### Tracking Quirks

- **Inventory Sorter** is tracked at file ID 7188660 (`inventorysorter-1.21.1-24.0.24.jar`). CF lists 24.0.24 as a 1.21.8 release, but the JAR is in the 1.21.1 NeoForge install and confirmed working in-game by the user 2026-05-07. `packwiz update` may try to swap it for 24.0.20 (the highest release CF officially tags as 1.21.1) — leave it pinned unless 24.0.24 actually breaks.

## Mods Backlog (To Add)

_Empty as of 2026-05-07 — all previously queued mods are installed and tracked. New entries land here when the user installs more in Prism and asks for a sync._

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
- Costs scale aggressively, however current costs of recipes are TBD.
- **Trophy items are gone.** The mod no longer ships `projecttitancore:trophy_tier_X`, so the `the_titan_core.snbt` quests still gating on those items are broken until re-tasked. Plan: Tier-ups can also trigger world changes. Defer wiring this until `projecttitancore` exposes the event hook.

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

**Status snapshot (2026-05-07):** 7 chapters, 52 quests shipped (38 originally + 14 added 2026-05-07: 2 each in energy/resource/gearing/magic/foes/travel/other). 38 new mods installed in this sync round (see `## Mods` above) — backlog below expanded with starter quests for the ones that warrant the "build + use" loop. Library/UI mods (Almost Unified, Crafting Tweaks, Enchantment Descriptions, FindMe, GuideME, Inventory Essentials, Inventory Sorter, Overflowing Bars, Pick Up Notifier) are intentionally questless.

**TODO — new chapter: `storage`.** Pull the storage-progression spokes out of `other` and into a dedicated chapter. Candidates to migrate/author: Sophisticated Storage tiers, Functional Storage drawers, Metal Barrels, AE2 ME network, ExtendedAE pattern providers, Sophisticated Backpacks tiering, Item Collectors. Hub idea: "Pack It Away". Decide order before authoring (likely vanilla → drawers → barrels → AE2 → ExtendedAE).

#### energy_generation
- [x] Hub — Spark of Industry
- [x] Create — Kinetic Conversion (Alternator)
- [x] Mekanism — Industrial Heat (Heat Generator)
- [x] EnderIO — Stirling Cycle (Stirling Generator)
- [x] Mekanism — Solar Array (Solar Generator)
- [x] EnderIO — Photovoltaic (Energetic Photovoltaic Module)
- [x] Mekanism — Gas-Burning Generator (mid-tier, requires Ethene)
- [x] Create — Steam Engine (1.21+ Create's mid-game power)
- [ ] Industrial Foregoing — Bioreactor + Biofuel Generator (alt biofuel path)
- [ ] Oritech — Generator (Oritech's own tech tree entry)
- [ ] Draconic Evolution — Draconium Capacitor (mid-tier Draconic power storage)
- [ ] Flux Networks — Flux Plug + Flux Point (wireless power transport setup)

#### resource_generation
- [x] Hub — Productive Earth
- [x] Mekanism — Strip Without the Strip (Digital Miner)
- [x] Mekanism — Quintuple Down (5x ore chain)
- [x] Create — Pressing Matters (Press + Mixer)
- [x] AE2 — Bootstrapping AE2 (Inscriber)
- [x] Create — Crushing Wheels (ore doubling alternative)
- [ ] Mekanism — Quantum Entangloporter (item shuttling)
- [ ] AE2 — first ME network (Controller + Drive + Crafting Terminal as separate quest)
- [ ] ExtendedAE — Ex Pattern Provider (high-throughput AE2 autocraft)
- [ ] ME Requester — Auto-restock requester terminal
- [x] Industrial Foregoing — Plant Sower + Plant Gatherer (auto crop loop)
- [ ] Mob Grinding Utils — Mob Masher farm (spawner-fed loot)
- [ ] Hostile Neural Networks — Deep Learner + Predictor (mob essence automation)

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
- [x] Tool Belt — Equip a Tool Belt
- [x] Mining Gadgets — Build & fire a Mining Gadget
- [ ] Draconic Evolution — Wyvern-tier gear (chestplate or sword)
- [ ] Cosmetic Armor Reworked — Equip a cosmetic over real armor

#### magic
- [x] Hub — Mana Spring
- [x] Inscribe & Cast — Scribe's Table + Mage's Spell Book
- [x] The Workshop — Enchanting Apparatus + Imbuement Chamber
- [x] Mana on Tap — Source Jar + Relay + Volcanic Sourcelink
- [x] First Ritual — Ritual Brazier + Ritual of Awakening
- [x] Cultivate — Magebloom seed + harvest
- [x] Ars Nouveau — Drygmy Charm / familiar pet (mob loot automation)
- [x] Ars Nouveau — Mage Robes set (Sorcerer tier — entry loadout)

#### strong_foes
- [x] Hub — Worthy Adversary
- [x] Apotheosis — Summon a Boss (Boss Summoner)
- [x] Apothic Spawners — Spawner Husbandry
- [x] Cataclysm — Slay the Harbinger
- [x] Cataclysm — Slay the Leviathan
- [x] Alex's Mobs — Hunt the Bone Serpent
- [x] Cataclysm — Slay the Ender Guardian
- [x] Cataclysm — Slay Ignis (Netherite Monstrosity still open)
- [ ] Apotheosis — Kill an affixed mob (any rare-tier)
- [ ] Gateways to Eternity — Open & clear a Gateway pylon
- [ ] Draconic Evolution — Slay the Chaos Guardian (endgame boss)

#### travel_the_world
- [x] Hub — Distant Horizons
- [x] Visit the Nether
- [x] Visit the End
- [x] Find a Stronghold (Yung's Better Strongholds)
- [x] Amethyst Rainforest (Terralith biome)
- [x] Craft a Globe (Supplementaries)
- [x] Towns and Towers — find a populated town
- [x] When Dungeons Arise — find a dungeon structure (Bandit Towers as the canonical pick)
- [ ] Tectonic — visit a Tectonic-only biome

#### other (QoL/utility)
- [x] Hub — Quality of Life
- [x] Farmers Delight — Hot Kitchen (Cooking Pot + Skillet)
- [x] Supplementaries — Worldly Trinkets (Sack + Globe)
- [x] Quark — Pocket Tools (Backpack + Trowel)
- [x] Sophisticated Storage — Tier Up Storage (Iron Barrel)
- [x] Pipez — Pipework (Item Pipe + Improved Upgrade)
- [ ] Macaws (doors/windows/roofs/etc.) — building blocks
- [ ] Curios — equip any curio item
- [ ] Chisel Modern — chisel a block variant (decorative)
- [x] Functional Storage — Storage Drawer (compact storage tier)
- [ ] Metal Barrels — Iron Barrel (mid-tier vanilla-style storage)
- [ ] Item Collectors — Place an Item Collector over a farm
- [x] Simple Magnets — Equip a magnet
- [x] CC: Tweaked — Boot a Computer (Computer + Turtle)
- [ ] Spice of Life: Carrot Edition — Eat 10 distinct foods (diet variety)
- [ ] Crafting Station — Place & use a Crafting Station
- [ ] Trash Cans — Configure a filtered trash can

#### the_titan_core (main spine)

**10 tiers locked 2026-05-07.** Demand targets per tier in `balance/energy.md`. T1-T10 all wired 2026-05-07 — task = obtain that tier's Titan Shard. The recipe-driven energy demand is the implicit gate (see `Don't use forge_energy tasks` rule above).

| Tier | Demand FE/t | Task item                               | Reward |
|---|---:|---|---|
| T1  |        1,000 | `projecttitancore:mote_of_the_titan`     | 16 iron_block + 16 xp_bottle |
| T2  |        4,000 | `projecttitancore:ember_of_the_titan`    | 16 iron_block + 16 copper_block + 32 xp_bottle |
| T3  |       16,000 | `projecttitancore:spark_of_the_titan`    | 16 copper_block + 16 gold_block + 1 totem_of_undying |
| T4  |       60,000 | `projecttitancore:pulse_of_the_titan`    | 16 gold_block + 16 diamond_block + 2 totem_of_undying |
| T5  |      250,000 | `projecttitancore:echo_of_the_titan`     | 16 diamond_block + 16 emerald_block + 1 nether_star |
| T6  |    1,000,000 | `projecttitancore:will_of_the_titan`     | 16 diamond_block + 8 netherite_block + 2 nether_star + 1 beacon |
| T7  |    4,000,000 | `projecttitancore:voice_of_the_titan`    | 16 emerald_block + 16 netherite_block + 4 nether_star + 2 beacon |
| T8  |   15,000,000 | `projecttitancore:soul_of_the_titan`     | 16 netherite_block + 8 nether_star + 4 beacon + 1 elytra |
| T9  |   60,000,000 | `projecttitancore:ascendant_shard`       | 32 netherite_block + 16 nether_star + 8 beacon + 2 elytra |
| T10 |  200,000,000 | `projecttitancore:heart_of_the_titan`    | 64 netherite_block + 32 nether_star + 16 beacon + 4 elytra |

Reward design: each tier hands the player a head start on the *next* tier's bulk ingredient (T1 reward is iron because T2's recipe needs iron, etc.) plus a tier-themed luxury item that scales with demand. T10 is overflowing capstone loot — no further tier to bulk-prep for.

- [ ] Hook the per-tier-up world responses (mob HP scaling, blood moons, gateway tears, etc.) once `projecttitancore` ships the `onTierAdvanced(int)` event. Sketch in the mod repo's CLAUDE.md under "World Response on Craft / Tier-Up".

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
- TODO: Investigate why `Bash(grep ...)` and `Bash(... | head ...)` calls still trigger permission prompts even though they look like they should be auto-allowed. User asked 2026-05-07; suspects a stale CLI session and plans to restart. If prompts persist after restart, broaden the allow list in `.claude/settings.local.json` (e.g. `Bash(grep *)`, `Bash(* | head *)`).

## Diagnosing Crashes

Primary log: `C:\Users\lind3\AppData\Roaming\PrismLauncher\instances\projecttitan\minecraft\logs\latest.log`

Search for `FATAL` or `ERROR` — the **first** one is always the root cause. Everything after is cascading noise.
