# Project Titan: Energy Balance Ledger

**Source of truth for energy generation balance across mods.** Future Claude sessions read this file first, then `energy.json`, then the tail of `CHANGELOG.md`. Never re-derive — read the ledger.

## Tier Targets

Sustained FE/t demand at each Titan Core tier (10 tiers, locked 2026-05-07). Numbers are **sustained**, not peak (spiky generators like wind use average expected output).

| Tier | Demand (FE/t)   | Scale archetype                  | Quest mapping            |
|---|---:|---|---|
| T1  |          1,000  | one starter generator            | introductory             |
| T2  |          4,000  | small array of starters          | finishing the entry mod  |
| T3  |         16,000  | small farm / cluster             | early-mid mod content    |
| T4  |         60,000  | first dedicated power room       | mid mod content          |
| T5  |        250,000  | scaled fuel-burning array        | mid-tier mod content     |
| T6  |      1,000,000  | full late-mod power room         | late mod tech            |
| T7  |      4,000,000  | nuclear entry                    | nuclear path begins      |
| T8  |     15,000,000  | full nuclear pipeline            | late-tier mod content    |
| T9  |     60,000,000  | deep nuclear / sub-fusion        | endgame approach         |
| T10 |    200,000,000  | fusion / endgame                 | Mekanism Fusion-class    |

Spacing is ~4× per tier — the same span (entry generator → fusion endgame) as before, split into 10 equal geometric jumps instead of 5.

## Design Principles

1. **Lateral options, not linear progression.** A player committed to one mod should have a viable path through every tier they can plausibly reach. If a mod can't reach a given tier, **add a mod that fills the gap** rather than buffing existing generators beyond their design.
2. **Don't fiddle.** Default values stay unless an actual imbalance shows. Adjustments are recorded in `CHANGELOG.md` with a stated reason.
3. **Smallest lever wins.** Mod config TOML > KubeJS > recipe edits > FTB Quest cost/reward.

## Unit Conventions

All ledger values are normalized to **FE/t** (Forge Energy per tick). Source-mod conversions:

| Mod | Native unit | FE conversion |
|---|---|---|
| Mekanism | Joules (J/t) | 1 J = 0.4 FE (default `JOULES_PER_FE` in `Mekanism/general.toml`) |
| EnderIO | uI/t | 1 uI = 1 FE |
| Createaddition | FE/t | 1:1 (native FE) |
| Create | SU (Stress Units) | not energy — separate kinetic system, not balanced here |

## Lever Priority

When applying a balance change, prefer the lever lowest in this list:

1. **Mod config TOML** (`config/<mod>-*.toml` or `config/<Mod>/<file>.toml`) — most mods expose direct multipliers; takes effect on game restart
2. **KubeJS server scripts** (`kubejs/server_scripts/`) — for cases where TOML doesn't expose the value
3. **Recipe edits** (KubeJS or datapack) — change generator cost rather than output
4. **FTB Quest cost/reward** — last resort, progression-side

## Ceiling Coverage Table

For each tier, which mods have a realistic path to that demand. Populated from `energy.json` → `ceiling_tier` field per generator. Last updated 2026-05-07.

| Tier | Demand        | Mekanism                                | Createaddition          | EnderIO                              | AE2                  | Coverage |
|---|---:|---|---|---|---|---|
| T1  |       1,000  | any starter (Solar/Bio/Heat/Wind)        | Alternator (~3)         | Stirling / any Photovoltaic          | Vibration Ch. (~13)  | **4 mods** |
| T2  |       4,000  | Adv Solar (~34) / Bio (~30) / Heat farm  | Alternator (~12)        | Octadic Stirling (~34) / Vibrant PV (~63) | Vibration Ch. (~50) | **4 mods** |
| T3  |      16,000  | Bio array (~115) / Adv Solar field (~134)| Alternator (~45 — peak) | Vibrant PV (~250 — impractical)      | ✗                    | **3 mods** |
| T4  |      60,000  | 1× Gas-Burning w/ Ethene (72k)           | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T5  |     250,000  | 4× Gas-Burning w/ Ethene (~290k)         | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T6  |   1,000,000  | 14× Gas-Burning Ethene / Fission low-burn| ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T7  |   4,000,000  | Fission moderate burn + Turbine          | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T8  |  15,000,000  | Fission + Turbine peak (~25M ceiling)    | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T9  |  60,000,000  | Fusion sub-peak injection                | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |
| T10 | 200,000,000  | Fusion peak                              | ✗                       | ✗                                    | ✗                    | **1 mod** ⚠ |

⚠ = Lateral-options failure. Player has no choice but Mekanism past T3.

**Gap filling:** when a tier has only one mod with coverage, the player has no choice — that's a lateral-options failure. Resolve by adding a mod, not by buffing. Going from 5→10 tiers widened the granularity of the gap but didn't change the underlying coverage problem: 7 of 10 tiers are Mekanism-only.

### Recommended Mods to Close Gaps (not yet installed)

Candidates the user should consider, ordered by how cleanly they fill the T4-T10 gap:

1. **Powah** — well-balanced Energizing Rod chain; Reactor multiblock at the upper end. Covers roughly T4-T8 in one mod. Ideal headline addition.
2. **Create: New Age** — Create-style electromagnetic generators with proper scaling (alternators, dynamos, reactors). Lets Create-only players actually reach T5-T7.
3. **Bigger Reactors** (Extreme/Big Reactors fork for 1.21) — Yellorium reactor + Turbine, alternative endgame to Mekanism. T7-T10.
4. **Industrial Foregoing** — Bioreactor + Petrified Fuel Generator + Pitiful Generator = breadth at T1-T3.
5. **NuclearCraft: Neoteric** — fission/fusion alternative; deep mechanics. T6-T10 alt for players who want non-Mekanism nuclear.

A pragmatic minimum to fix the picture: add **Powah** and **Create: New Age**, leave Mekanism's nuclear top-end as a parallel rather than the only path.

## Workflow for Future Sessions

1. Read this file (design principles + tier targets).
2. Read `energy.json` (current per-generator data).
3. Read tail of `CHANGELOG.md` (recent decisions with reasons).
4. **Diagnose first.** If user reports imbalance, find the relevant generator entry in `energy.json`, compute realistic per-block output, compare against tier target.
5. **Apply with smallest lever** (see Lever Priority).
6. **Record in CHANGELOG.md** — date, mod, generator, old → new, reason.
7. After mod changes (add/remove/update), re-run `python scripts/audit-energy.py` to refresh `energy-discovered.json`, then reconcile with `energy.json`.

## Re-running the Audit

```
python scripts/audit-energy.py
```

Outputs `balance/energy-discovered.json`. The script is idempotent — re-run after any mod add/remove or live config edit. Diff against `energy.json` to surface drift.

## Known Ghost Configs

These config files exist in `config/` but the corresponding mod is not installed. Safe to ignore in audit output; clean up if convenient.

- `config/generatorgalore-server.toml` — Generator Galore was removed; config is leftover.
