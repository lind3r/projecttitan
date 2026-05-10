# Project Titan: Resource Generation Ledger

**Source of truth for resource (especially mineral/ore) generation across mods.** Future Claude sessions read this file first, then `resources.json`. Sister doc to `energy.md` — same workflow, different domain.

Where `energy.md` tracks **demand curves** (FE/t at each Titan Core tier), this file tracks **acquisition paths**: mining, multipliers, mob loot, structure loot, transmutation, world-gen. Resources don't have a clean "tier demand" axis the way energy does, so the structure here is by **path category** + **renewability**, not by tier.

## Core Distinction: Renewable vs Finite

The single most important axis for this pack is whether a resource path is **renewable** (infinite source, no mining required, scales with energy/time) or **finite** (chunk-bound, exhausts as you mine). The pack ships several renewable ore sources that can trivialize the mining loop. They're called out individually in the [Renewable Systems Watchlist](#renewable-systems-watchlist) below.

| Class                   | Mining required? | Scales with...        | Pack examples                                                              |
|---|---|---|---|
| **Vanilla mining**      | yes              | tools, mobility        | base game; FTB Ultimine speeds it up                                       |
| **Multipliers**         | yes (per ore)    | input throughput       | Mekanism 5x chain, Create crushing, EnderIO SAG Mill, Oritech centrifuge   |
| **Automated mining**    | yes (chunk-bound)| chunk-loaders          | Mekanism Digital Miner, Oritech Deep Drill                                 |
| **Renewable ore**       | **no**           | energy + time          | **IF Laser Drill** ⚠                                                       |
| **Renewable mob loot**  | **no**           | energy + spawners      | EnderIO Powered Spawner, IF Mob Crusher+Duplicator, Apothic Spawners ⚠     |
| **Synthetic mob loot**  | **no**           | energy alone           | **Hostile Neural Networks Loot Fabricator** ⚠                              |
| **Non-violent loot**    | **no**           | mana + time            | Ars Nouveau Drygmy + Mob Jar                                               |
| **Renewable crystals**  | **no**           | growth time            | AE2 Budding Certus Quartz (with Growth Accelerator)                        |
| **Structure loot**      | once per struct  | exploration            | YUNG's, When Dungeons Arise, Towns and Towers + Loot Integrations          |
| **Boss / wave loot**    | per summon       | summoning materials    | Apotheosis Boss Summoner, Cataclysm bosses, Gateways to Eternity           |
| **Crop / biomass**      | no               | farmland + automation  | IF Plant Sower/Gatherer, vanilla crops, Ars Source Berries                 |

⚠ = called out in the watchlist below for the user's review.

## Design Principles

(Inherited from `energy.md`, restated for this domain.)

1. **Lateral options, not linear progression.** Multiple multiplier mods is fine; multiple infinite-ore generators is not. The first one trivializes the others.
2. **Don't fiddle.** Default values stay unless an actual imbalance shows. Adjustments are recorded with a stated reason.
3. **Smallest lever wins.** Mod config TOML > KubeJS recipe edit > FTB Quest cost/reward.

## Multipliers (Ore Doubling/Tripling/etc.)

For each ore mined, how many ingots do you actually get? Verified against installed JAR recipes 2026-05-07.

| Mod                | Machine chain                                                       | Multiplier (ore block) | Multiplier (raw drop) | Notes |
|---|---|---:|---:|---|
| Vanilla            | Furnace                                                             | 1×                     | 1×                    | Baseline                                                                  |
| Mekanism (T2)      | Enrichment Chamber                                                  | 2×                     | 2×                    | One machine, simplest chain                                              |
| Mekanism (T3)      | Purification Chamber → Crusher → Enrichment                         | 3×                     | 2×                    | Ore-block path gives 3 clumps; raw-drop path gives 2 (recipe-verified)   |
| Mekanism (T4)      | Chemical Injection Chamber → T3 chain                               | 4×                     | ~2.67×                | Ore-block: 4 shards. Raw-drop: 8 shards per 3 raw                        |
| Mekanism (T5)      | Chemical Dissolution → Crystallizer → T4 chain                      | 5×                     | ~2.67× (no slurry path) | Headline 5× requires silk-touched ore blocks fed to Dissolution         |
| Create             | Crushing Wheels (or Millstone)                                      | 2×                     | 2×                    | Crushed ore → wash to nuggets; standard ore-doubling                     |
| EnderIO            | SAG Mill (no grinding ball)                                         | 2×                     | 2×                    | Bonus chance varies by recipe                                            |
| EnderIO            | SAG Mill + Dark Steel grinding ball                                 | up to 3×               | up to 3×              | Grinding ball boosts main + bonus output chances                         |
| Oritech            | Pulverizer                                                          | 2×                     | 2×                    | Simple crush                                                              |
| Oritech            | Fragment Forge → Centrifuge → Atomic Forge                          | up to ~3×              | up to ~3×             | Multi-step; needs more verification on terminal multiplier                |
| Industrial Foregoing | (no native ore-multiplier machine)                                | 1×                     | 1×                    | IF replaces ore *acquisition* (Laser Drill) rather than multiplying it    |

**Headline:** Mekanism is the ceiling at 5× (silk touch). Create / EnderIO / Oritech all sit at 2×–3×. The pack has plenty of multiplier coverage; no need to add another doubler mod.

## Automated Mining (Chunk-Bound)

These move the player out of the mine, but they still consume the world's ore. They scale until you've mined out every chunk you've loaded — then you have to migrate the machine.

| Mod          | Machine          | Mechanism                                                     | Renewable? | Notes |
|---|---|---|---|---|
| Mekanism     | Digital Miner    | 32-block radius scan, configurable filters, silk-touch upgrade | finite    | Pairs with Anchor Upgrade for chunk loading; depletes scanned region |
| Oritech      | Deep Drill       | Multiblock placed on resource node                             | finite    | Bound to discovered nodes; can move to fresh nodes                   |
| Create       | Mechanical Drill | Single-block auto-mine in front                                | finite    | Useful for cobble generators (renewable) but not ores                 |

These are the "right" way to scale ore acquisition once you have power: they're powerful but not infinite, and they push the player to keep exploring.

## Renewable Systems Watchlist

These bypass mining entirely. The user flagged this category specifically. Each is rated by potency (how badly it trivializes the resource loop) and given a disable lever.

### ⚠ TIER 0 — Critical (review before they go live in a real playthrough)

#### IF Laser Drill + Ore Laser Base
- **What it does:** Multiblock infinite ore generator. Laser Drill aims at a Laser Base; Base consumes 1000 FE per operation (every ~5s with 50t cooldown × 100t base progress) and outputs ores from a weighted pool. Laser Lenses (colored items) bias the pool toward specific ores; `catalystModifier = 8` adds +8 weight per lens.
- **Renewable:** YES — power in, ores out, forever. No mining ever.
- **Why it matters:** This is the single most disruptive resource path in the pack. With even modest power generation (~20k FE/t = 4 active drills), a player can produce more iron/gold/diamond per minute than any mining route, and the output never depletes.
- **Disable levers (smallest first):**
  1. **Recipe removal via KubeJS** — block the Laser Base recipe so the multiblock can't be built. (Recipe-locked, no TOML toggle.)
  2. **Power-cost increase** — `config/industrialforegoing/machine-resource-production.toml` → `LaserDrillConfig.powerPerOperation` (currently 1000 FE) → 50,000+ FE. Doesn't disable but throttles to "viable late, not trivializing early."
  3. **Lens weight nerf** — `OreLaserBaseConfig.catalystModifier` (currently 8) → 1. Forces players to use many lenses to bias output, reducing ore-targeting efficiency.
- **Recommendation:** Remove the recipe via KubeJS. The mod has plenty of other useful machines (mob loop, plant farm, Bioreactor) — losing only the Laser Drill keeps IF playable while closing the worst exploit.

#### Hostile Neural Networks — Loot Fabricator
- **What it does:** Collect data on a mob (right-click 50× or kill 50×), then feed the trained data model to a Loot Fabricator. The Fabricator synthesizes that mob's loot with only FE input — **no mob ever has to spawn or die again.**
- **Renewable:** YES, fully synthetic.
- **Cost:** 256 FE/t (`config/hostilenetworks.cfg` → `Loot Fab Power Cost`). At ~5k FE per fabrication cycle, a single 1k FE/t generator runs it indefinitely.
- **Why it matters:** This is the canonical "infinite mob loot" mod. Once a player has data models for Wither Skeletons (skulls), Endermen (pearls), Withers, etc., resource scarcity for those drops is over. The 256 FE/t default cost is so low it doesn't gate progression at all.
- **Disable levers (smallest first):**
  1. **Power-cost increase** — `config/hostilenetworks.cfg` → `Loot Fab Power Cost` 256 → 10,000+ FE/t. Pushes Fabricator into "endgame convenience" rather than "early-game replacement for mob farms."
  2. **Disable model attune via right-click** — `Right Click To Attune = false`. Forces players to actually kill mobs to train models (still renewable but at least requires the kill phase).
  3. **Mod removal** — entire mod is one feature; if the cost knob doesn't satisfy you, drop the mod.
- **Mineral leak surface (revisited 2026-05-08):** narrow. HNN cannot synthesize diamond, emerald (at scale), netherite, copper, coal, or elytra — none of those mobs exist or their drops are too rare. What HNN **can** trivialize for T1-T10: iron (Iron Golem), gold (Zombified Piglin), and **nether stars (Wither model)**. The diamond/emerald/netherite/elytra walls remain regardless.
- **Status (2026-05-10):** **Reverted to defaults.** `Loot Fab Power Cost` back to **256 FE/t** stock; the per-model `sim_cost` curve in the data files (range 32 → 4096+ FE/t, median 128) is the actual per-recipe gate. Combined with the narrow mineral-leak surface above, the default cost doesn't materially trivialize T1-T10 — Wither nether-stars are the only meaningful leak and they require getting a Wither kill to train the model first. Revisit if playtesting shows a problem.

#### Apothic Spawners (silk-touched + modified vanilla spawners)
- **What it does:** With Silk Touch (level 1, default), break any vanilla spawner and place it elsewhere. The mod adds 16 craftable Spawner Modifier items that strip spawn conditions (Ignore Players/Light/Conditions), drop spawn delay, raise caps, and amplify drops (Echoing). The mod does **not** add a "change mob" modifier — captured spawners keep their original mob type.
- **Renewable:** YES — once captured, infinite mob spawning indefinitely.
- **Mob types reachable:** vanilla dungeon mobs only (zombie / skeleton / spider / cave spider / blaze / magma cube / silverfish). No wither skeleton, no creeper, no enderman — those still require IF Mob Duplicator or EIO Powered Spawner with a Soul Vial.
- **Mineral impact:** **low.** None of the reachable mob types drop ore. Indirect impact via zombie iron drops + Echoing modifier multipliers, but that's small relative to the T1-T10 mineral curve. Bigger impact is XP / mob-drop flood (great for Apotheosis affix gear via Salvaging, fast enchanting).
- **Status (2026-05-08):** **Re-enabled at default (`Spawner Silk Level = 1`).** Reasoning: with the IF Laser Drill blocked and HNN Loot Fab pushed to T5 power, captured-spawner farms are no longer the dominant cheese — they're a reasonable mid-game step. The pack's main concern is mineral demand at T1-T10, and Apothic Spawners doesn't move that needle. If the XP / Apotheosis-loot flood turns out to be a problem in playtesting, revisit and disable.

### ⚠ TIER 1 — Powerful, but more gated (decide if you want to nerf)

#### IF Mob Duplicator + Mob Crusher loop
- **What it does:** Mob Crusher kills mobs in 3×3, drops loot + Mob Essence fluid. Mob Duplicator consumes essence + 5000 FE per spawn to produce more of the same mob. Closed loop: spawn → crush → essence → spawn.
- **Renewable:** YES (once you have one mob's essence, you have infinite of that mob).
- **Costs:** Duplicator 5000 FE per spawn + 12 mB essence × mob max-HP. Crusher 50 FE/op + ~50 ticks per kill. Modest power demand.
- **Why it's not Tier 0:** Requires you to *capture* a mob first (essence isn't synthesized from nothing). For wither skeletons, etc., that's a real hurdle. For cows / squids / drowned, it's trivial.
- **Disable levers:** `config/industrialforegoing/machine-agriculture-husbandry.toml` → `MobDuplicatorConfig.powerPerOperation` (currently 5000) → 50,000+ FE; `essenceNeeded` 12 → 100 (8× essence cost).
- **Recommendation:** Leave default. The cap is "as much as you can power" which the pack's energy curve already governs. If you want to slow it down, raise `essenceNeeded` first (preserves the fun, taxes throughput).

#### EnderIO Powered Spawner (with Soul Vial)
- **What it does:** Capture mob in Soul Vial → place vial in Powered Spawner → consume FE to spawn that mob. Combine with killer (spike block, Mekanism Quantum Entangloporter feeding lava, etc.) for closed-loop mob loot.
- **Renewable:** YES.
- **Built-in throttle:** `config/enderio/machines-common.toml` → `maxSpawners = 10` (efficiency loss past 10 in proximity), `maxEntities = 2` (spawning halts if 2 mobs are nearby — forces you to clear them).
- **Why it's not Tier 0:** The proximity caps are already hard limits that prevent megafarms. Energy cost (`energy.poweredSpawner.usage`) per spawn scales with mob health.
- **Disable levers:** Tighten `maxSpawners` to 1, or raise `energy.poweredSpawner.usage`.
- **Recommendation:** Leave default. The proximity caps are doing the job.

#### Gateways to Eternity (gateway pylons)
- **What it does:** Construct a Gateway Pylon, activate it, fight a wave of mobs that drop loot. Pylon can be reactivated indefinitely.
- **Renewable:** YES (waves) — but bounded by the per-activation summoning material cost.
- **Why it's not Tier 0:** Each activation costs an opal/key/etc. and takes player time. Not AFK-able the way spawner farms are.
- **Recommendation:** Leave default. Acts more like a "boss arena" than a passive farm.

### Tier 2 — Quietly renewable, mostly fine

| System                                   | Renewable? | Severity | Notes |
|---|---|---|---|
| AE2 Budding Certus Quartz                | yes        | low      | Slow growth (hours per cluster); limited per budding block tier; pack-typical and expected by AE2 players |
| Ars Nouveau Drygmy + Mob Jar             | yes        | low      | One mob per Jar, slow drop rate, mana cost. Single stream per setup |
| Apotheosis Boss Summoner                  | yes        | low      | Per-summon material cost; cooldown via summoning items |
| Cataclysm bosses                         | semi       | low      | Per-boss summoning recipe; high-quality but bounded loot |
| Mekanism Solar Neutron Activator         | yes        | low      | Transmutes Polonium → Plutonium etc.; needs upstream Fission waste — gated by reactor |
| IF Plant Sower + Gatherer + Bioreactor   | yes        | low      | Crops/food only, not minerals. Acceptable. |
| Iron golem farms (vanilla)               | yes        | low      | Always available; pack doesn't change this |
| Cobblestone generators (vanilla)         | yes        | low      | Always available; feeds Create / IF Mechanical Dirt etc. |
| Quark Ender Biotite (per dragon respawn) | semi       | low      | Bounded by dragon-fight cadence |
| Apotheosis Salvaging Table               | no (lossy) | low      | Item recycling; not net-positive resource generation |

These are the systems that *could* be flagged but are either self-throttling, mod-typical, or not minerals.

## World-gen Ore Additions

| Mod          | Adds                                                                  | Notes |
|---|---|---|
| Mekanism     | Tin, Osmium, Lead, Uranium, Fluorite (overworld); Salt (underground)  | Standard Mekanism world-gen                                                  |
| Create       | Zinc                                                                  | New ore for brass crafting                                                   |
| Draconic Evolution | Draconium (overworld + Nether + End); Chaos Crystals (Chaos Islands, ~10k blocks apart) | Chaos Crystals require defeating Chaos Guardian per island |
| Quark        | Corundum (color variants), Ender Biotite                              | Corundum can grow on Corundum blocks; Biotite renews per dragon kill         |
| AE2          | Certus Quartz, Charged Certus Quartz                                  | Charged Certus is rare; budding-block growth is the late-game source         |
| Apotheosis   | Gem materials drop from affixed mobs (not world-gen ore)              | Indirect — gems flow via mob drops                                            |
| Terralith / Tectonic | (none — biome/terrain mods only)                              | Don't add ores; can shift vanilla ore distribution by biome shape            |

## Structure Loot

`Loot Integrations` + `Vanilla Loot Addon for Loot Integrations` modify YUNG's, When Dungeons Arise, Towns and Towers, and vanilla structures' loot tables — modded items get a 3× weight bias. This means **structure exploration is a real resource path**, not just a vanilla curiosity. Most loot is gear, but rare-tier modded materials show up in mid-tier chests.

| Source                       | Renewable? | Loot tier |
|---|---|---|
| YUNG's structures (8 modules)| no (per chunk) | low–medium |
| When Dungeons Arise mega-structures | no (per chunk) | medium–high |
| Towns and Towers             | no (per chunk) | medium |
| Vanilla structures + Loot Integrations | no (per chunk) | low–medium with modded boost |

## Mining QoL (Throughput Multipliers)

These don't generate resources — they multiply how much the player can mine per minute.

| Mod              | Effect                                              |
|---|---|
| FTB Ultimine     | Vein-mine up to 64 blocks per swing (Shift+hotkey). 0 cooldown, 20 hunger per block, no XP cost. |
| Mining Gadgets   | AOE laser pickaxe with Fortune/Silk/Magnet/Void upgrades |
| Mekanism Atomic Disassembler / Meka-Tool | Multi-mode tool with vein/3×3 modes |
| FTB Ultimine + Mining Gadgets stacking   | Massively amplifies throughput; no per-block cap |

## Item Collection QoL

| Mod                        | Effect                                                  | Unattended? |
|---|---|---|
| Simple Magnets             | 5-block (basic) / 8-block (advanced) pull radius        | no (player-bound) |
| Item Collectors            | Stationary 5–7 block vacuum into adjacent inventory     | yes         |
| Sophisticated Backpacks    | Pickup + Magnet + Void + Auto-Smelt upgrades; works on Create contraptions | partial |

Item Collectors paired with structure ruins or mob farms are the "set and forget" amplifier.

## Workflow for Future Sessions

1. Read this file (categories + renewability framing).
2. Read `resources.json` (per-machine curated entries).
3. **For balance questions:** identify the path category, then look up the specific machine's entry. If the path is renewable, check the watchlist for whether the user has decided to nerf/disable it.
4. **For "is X covered?" questions:** look up the resource in the multiplier table or the watchlist.
5. **Apply with smallest lever** (mod TOML > KubeJS > recipe edit).
6. **Record decisions:** if the user accepts/rejects a watchlist nerf, note it in the watchlist entry with a date.
