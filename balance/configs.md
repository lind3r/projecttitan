# Project Titan: Config Diff Registry

**Single-source list of every config / kubejs override we ship that differs from a stock install of the same mods.** Companion to `energy.md` (demand curves) and `resources.md` (acquisition paths) — those track *gameplay shape*; this file tracks *the actual settings file deltas* that produce that shape.

Update this file any time you change a config knob, add a kubejs override, or remove a recipe. Format is **what changed → from → to → why**, with a commit ref so the original diff is recoverable.

## Conventions

- "Default" is the stock value as shipped by the mod (verified from the config's own comment, the JAR's bundled default, or the pre-edit value in `git log`).
- Files under `config/<mod>/` and `config/<modid>.cfg` apply globally to all worlds on next restart. Files under `defaultconfigs/` only seed *new* worlds — existing saves freeze a copy. (See CLAUDE.md → "Live ↔ Repo Bridge".)
- `kubejs/data/<mod>/...` overrides are datapack-level and apply to fresh worlds only (vanilla loads worldgen from the datapack registry once at world-create).
- KubeJS recipe edits in `kubejs/server_scripts/` apply globally on next reload.

---

## AdLods (Large Ore Deposits) — replaces vanilla ore-gen

**File:** `config/adlods-common.toml`

| Key                          | Default | Pack | Reason                                                                  | Commit |
|---                           |---:     |---:  |---                                                                      |---     |
| `globalSpawnRateMultiplier`  | 1.0     | 2.0  | Deposits too sparse to find in playtesting.                             | `cf1fa4c` |
| `globalSizeMultiplier`       | 1.0     | 4.0  | Iron motherlode now ~2800-5600 blocks, ancient_debris ~1000-2000.       | `a09433a` |
| `disableVanillaLargeVeins`   | false   | true | AdLods replaces vanilla large veins; prevents double-up.                | `185e7fa` |

**Files:** `config/adlods/VanillaOres/*.cfg` (24 files)

All vanilla ore generation disabled (`S:generation=NONE`) — AdLods deposits are the new acquisition path. Covers coal/iron/copper/gold/diamond/emerald/lapis/redstone, nether ores, ancient_debris, and stone/dirt/gravel/clay variants. (Commit `185e7fa`.)

**Files:** `config/adlods/Deposits/*.cfg` and `config/adlods/Geodes/*.cfg`

Pack-authored deposit definitions (no defaults — AdLods ships empty). 30+ deposit types: vanilla ores, Mekanism (tin/osmium/uranium/lead), Create (zinc), Oritech (nickel/platinum), and amethyst geodes. (Commit `185e7fa`.)

## AdFinders — handheld ore scanners

**File:** `config/adfinders-common.toml`

| Finder  | Key           | Default | Pack | Reason |
|---      |---            |---:     |---:  |---     |
| Gem     | `scanRadius`  | 6       | 12   | Pairs with 2× deposit spawn rate to make finders the primary discovery tool. |
| Gem     | `pingDepth`   | 32      | 64   | "                                                                            |
| Metal   | `scanRadius`  | 8       | 16   | "                                                                            |
| Metal   | `pingDepth`   | 48      | 96   | "                                                                            |
| Mineral | `scanRadius`  | 7       | 14   | "                                                                            |
| Mineral | `pingDepth`   | 40      | 80   | "                                                                            |

(Commit `21050dd`. Scan only runs while a finder is held — cost is bounded.)

## Mekanism — disable ore-gen for AdLods-covered ores

**File:** `config/Mekanism/world.toml`

| Section    | Key              | Default | Pack  | Reason |
|---         |---               |---      |---    |---     |
| `[tin]`    | `shouldGenerate` | true    | false | Replaced by AdLods tin deposits. |
| `[osmium]` | `shouldGenerate` | true    | false | Replaced by AdLods osmium deposits. |
| `[uranium]`| `shouldGenerate` | true    | false | Replaced by AdLods uranium deposits. |
| `[lead]`   | `shouldGenerate` | true    | false | Replaced by AdLods lead deposits. |

Fluorite + salt left at default (true) — neither is in AdLods. (Commit `5a39ae7`.)

## Create + Oritech — datapack ore-gen overrides

These mods ship ore-gen as data-driven biome modifiers, so they're disabled via kubejs datapack overrides (set to `neoforge:none`) rather than a config flag.

| File                                                            | Effect                                                          |
|---                                                              |---                                                              |
| `kubejs/data/create/neoforge/biome_modifier/zinc_ore.json`      | Disable Create zinc ore-gen. (Striated_ores left intact — those are scoria/tuff/andesite decoration.) |
| `kubejs/data/oritech/neoforge/biome_modifier/ore_nickel.json`   | Disable Oritech nickel ore-gen.                                 |
| `kubejs/data/oritech/neoforge/biome_modifier/ore_platinum.json` | Disable Oritech overworld platinum ore-gen. (`ore_platinum_end` left intact since AdLods is overworld-only; `resource_node_*` left intact — that's the surface-boulder gameplay feature, not raw ore.) |

(Commit `5a39ae7`.)

## Industrial Foregoing / Mekanism / Oritech / CC:Tweaked — recipe removals

**File:** `kubejs/server_scripts/balance_resources.js`

Removed crafting recipes (machines remain in JEI but uncraftable in survival):

| Item                              | Reason                                                                  |
|---                                |---                                                                      |
| `industrialforegoing:laser_drill` | Renewable infinite-ore generator (Tier 0 watchlist in `resources.md`).  |
| `industrialforegoing:ore_laser_base` | "                                                                    |
| `mekanism:digital_miner`          | No-automated-mining policy — pushes players to AdLods + hand mining.    |
| `oritech:deep_drill_block`        | "                                                                       |
| `computercraft:turtle_normal`     | "                                                                       |
| `computercraft:turtle_advanced`   | " (computers/peripherals/modems/disks remain craftable.)                |

(Commits `e7e31ac` (initial), `2fd2b19` (Mek/Oritech/CC additions).)

## Applied Energistics 2 — channel capacity

**File:** `config/ae2-common.toml`

| Key        | Default   | Pack | Reason                                                                                                       | Commit |
|---         |---        |---   |---                                                                                                           |---     |
| `channels` | `DEFAULT` | `X4` | Cabling effort, not channel math, is the design constraint. Glass/Covered = 32 ch, Dense = 128 ch. Mentioned in the AE2 intro and Bric-a-Brac quests so players know the stock-AE2 numbers in the Guide are 4× off. | (this commit) |

## L_Ender's Cataclysm — disable per-hit / DPS damage caps on Trial bosses

**File:** `config/cataclysm-common.toml`

Cataclysm ships per-boss anti-cheese caps that throttle late-game weapons (a 700-dmg Chaotic Draconic sword was landing at 5 dmg/swing — `damage_cap` clamped the hit, then `dps_cap` throttled subsequent swings). Caps make sense for solo boss-fight design but are wrong for the post-T10 Titan Trial gauntlet where the player is intentionally apex-tier. Note: change is global, so these three bosses are also nerfed in their native arenas — acceptable given the pack's late-game scale.

| Section                                | Key          | Default    | Pack       | Reason |
|---                                     |---           |---:        |---:        |---     |
| `[mobs.ender_guardian.cap_config]`     | `damage_cap` | 22.0       | 999999.0   | See above. |
| `[mobs.ender_guardian.cap_config]`     | `dps_cap`    | 13.0       | 999999.0   | "       |
| `[mobs.netherite_monstrosity.cap_config]` | `damage_cap` | 25.0    | 999999.0   | "       |
| `[mobs.netherite_monstrosity.cap_config]` | `dps_cap`   | 20.0    | 999999.0   | "       |
| `[mobs.ignis.cap_config]`              | `damage_cap` | 20.0       | 999999.0   | "       |
| `[mobs.ignis.cap_config]`              | `dps_cap`    | 14.0       | 999999.0   | "       |

`nature_heal` (passive regen, 25.0) and Ignis's `healing_multiplier` (lifesteal, 1.0) **left at default** — confirmed in playtest 2026-05-10 that with caps removed the regen is a fight-pacing feature, not a wall. To compensate, the Trial wave's `max_health` modifier is bumped — see next section.

## projecttitancore Titan Trial — wave HP override

**File:** `kubejs/data/projecttitancore/gateways/titan_trial.json` (datapack override of the bundled `data/projecttitancore/gateways/titan_trial.json` from the mod JAR)

| Modifier                                   | Default (mod) | Pack    | Reason |
|---                                         |---:           |---:     |---     |
| `minecraft:generic.max_health` (`add_multiplied_total`) | 1.0 (=2× HP) | 9.0 (=10× HP) | Compensate for the Cataclysm cap removal above. With per-hit caps gone the bosses die faster, so 5× the HP keeps the gauntlet a real fight. Datapack override (vs. editing the mod) so future tuning needs only an edit + reload, no mod rebuild. |

`attack_damage` modifier left at +100% (2×). All other fields (entities, rewards, rules, spawn algorithm) match the mod's bundled JSON — datapack overrides are full-file replacements, not partial patches.

---

## Update workflow

When you touch a config:

1. **Make the edit** — usually inline an explanatory comment in the config itself ("Project Titan: …") so the file is self-documenting in-game and readable to anyone forking the pack.
2. **Add or update the row in this file** — file path, key, default, new, one-sentence reason, commit short hash (`git log -1 --pretty=%h`).
3. **Cross-link** to `resources.md` / `energy.md` if the change is part of a broader gameplay decision tracked there.
4. **Commit** with the change so this file moves in lockstep with the underlying knob.

When auditing whether the registry is in sync with reality:

```bash
git log --oneline -- 'config/**' 'defaultconfigs/**' 'kubejs/**'
```

Anything since the last entry here may be missing.
