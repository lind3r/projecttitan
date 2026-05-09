# Project Titan: Energy Balance Ledger

**Source of truth for energy generation balance across mods.** Future Claude sessions read this file first, then `energy.json`, then the tail of `CHANGELOG.md`. Never re-derive — read the ledger.

## Tier Targets

Sustained FE/t demand at each Titan Core tier (10 tiers, locked 2026-05-07). Numbers are **sustained**, not peak (spiky generators like wind use average expected output).

| Tier | Demand (FE/t)     | Scale archetype                  | Quest mapping            |
|---|---:|---|---|
| T1  |            1,000  | one starter generator            | introductory             |
| T2  |            5,000  | small array of starters          | finishing the entry mod  |
| T3  |           25,000  | small farm / cluster             | early-mid mod content    |
| T4  |          125,000  | first dedicated power room       | mid mod content          |
| T5  |          625,000  | scaled fuel-burning array        | mid-tier mod content     |
| T6  |        3,000,000  | full late-mod power room         | late mod tech            |
| T7  |       15,000,000  | nuclear entry                    | nuclear path begins      |
| T8  |       75,000,000  | full nuclear pipeline            | late-tier mod content    |
| T9  |      400,000,000  | deep nuclear / sub-fusion        | endgame approach         |
| T10 |    2,000,000,000  | fusion-array / endgame           | Mekanism Fusion-class    |

Spacing is ~5× per tier — entry generator (1k FE/t) up to a 2 GFE/t apex that demands either a multi-Fusion array or a top-tuned Draconic Reactor. T10 is bumped from 200M to 2 GFE/t (10×) so a single Fusion no longer trivially carries it; T9 jumps proportionally so the gap stays consistent. Per-tier energy values are clamped at the recipe layer to `Integer.MAX_VALUE` (~2.147 GFE/t) — the buffer/receive arithmetic in `TitanCoreBlockEntity` long-promotes and clamps to avoid int overflow.

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

For each tier, which mods have a realistic path to that demand. Populated from `energy.json` → `ceiling_tier` field per generator. Last updated 2026-05-07 (post Oritech / IF / Draconic Evolution add).

> ⚠ **STALE — needs re-audit (2026-05-09 rebalance).** Demand column reflects the new ~5×/tier curve, but the per-mod ceiling assessments below were judged against the previous 4×/tier targets (T10 = 200M FE/t). Treat T4-T10 entries as **over-optimistic**; in particular, T9-T10 at the new scale are firmly multi-Fusion-array territory, not single-Fusion. Re-run `python scripts/audit-energy.py` and reconcile before relying on coverage counts.

| Tier | Demand          | Mekanism                                  | Createaddition          | EnderIO                              | AE2                  | Industrial Foregoing            | Oritech                          | Draconic Evolution           | Coverage |
|---|---:|---|---|---|---|---|---|---|---|
| T1  |          1,000  | any starter (Solar/Bio/Heat/Wind)         | Alternator (~3)         | Stirling / any Photovoltaic          | Vibration Ch. (~13)  | Pitiful (~33) / Biofuel (~7)     | basic (~31) / bio (~16) / fuel (~4) | Reactor (sub-peak idle)      | **7 mods** |
| T2  |          5,000  | Adv Solar (~34) / Bio (~30) / Heat farm   | Alternator (~12)        | Octadic Stirling (~34) / Vibrant PV (~63) | Vibration Ch. (~50) | Biofuel array (~25)              | fuel (~16) / bio (~62)           | Reactor                      | **7 mods** |
| T3  |         25,000  | Bio array (~115) / Adv Solar field (~134) | Alternator (~45 — peak) | Vibrant PV (~250 — impractical)      | ✗                    | ✗ (~100 gens, impractical)       | Reactor (25k cap)                | Reactor                      | **5 mods** |
| T4  |        125,000  | 2× Gas-Burning w/ Ethene (~145k)          | ✗                       | ✗                                    | ✗                    | ✗                                | ✗ (~234, impractical)            | Reactor (low-mid tuning)     | **2 mods** |
| T5  |        625,000  | 9× Gas-Burning w/ Ethene (~650k)          | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | Reactor (mid tuning)         | **2 mods** |
| T6  |      3,000,000  | Fission low-burn + Turbine                | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | Reactor (high tuning)        | **2 mods** |
| T7  |     15,000,000  | Fission + Turbine moderate                | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | Reactor (peak band)          | **2 mods** |
| T8  |     75,000,000  | Fission + Turbine peak (~25M ceiling) ⚠   | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | ✗ (above stable peak)        | **0 mods** ⚠⚠ |
| T9  |    400,000,000  | Fusion peak (~200M) ⚠ — needs scaled array | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | ✗ (only via unsafe tunings)  | **0 mods** ⚠⚠ |
| T10 |  2,000,000,000  | Multi-Fusion array (10× Fusion peak)      | ✗                       | ✗                                    | ✗                    | ✗                                | ✗                                | ✗ (only via unsafe tunings)  | **1 mod** ⚠ |

⚠ = Lateral-options failure. Player has no choice but Mekanism past T8.
⚠⚠ = New rebalance (2026-05-09) likely creates a coverage gap at T8-T9 — needs audit and possibly mod additions or per-generator buffs to close.

**Gap filling:** when a tier has only one mod with coverage, the player has no choice — that's a lateral-options failure. Resolve by adding a mod, not by buffing. The Draconic Evolution add (2026-05-07) closed the T4-T8 single-mod stretch — those tiers had a non-Mekanism path against the old 200M apex. After the 2026-05-09 rebalance to 2 GFE/t apex, the picture has likely shifted: re-audit suggests T8 may have lost Draconic coverage and T9-T10 demand multi-Fusion arrays. Don't act on this yet — re-run the audit and verify per-generator ceilings before sizing the response.

### Recommended Mods to Close Gaps (not yet installed)

Candidates the user could still consider, now narrowed to the T9-T10 endgame gap:

1. **Bigger Reactors** (Extreme/Big Reactors fork for 1.21) — Yellorium reactor + Turbine, an alternative endgame approach. Could realistically reach T9 with a maxed turbine setup; T10 is Mekanism-Fusion-class either way.
2. **NuclearCraft: Neoteric** — fission/fusion alternative; deep mechanics. T9-T10 alt for players who want non-Mekanism nuclear endgame.
3. **Create: New Age** — Create-style electromagnetic generators. Wouldn't reach T9-T10 but gives Create-only players a longer runway through T4-T6 alongside Draconic.

The T4-T8 gap that previously motivated **Powah** and **Industrial Foregoing** as candidates is now covered by Draconic Evolution + Industrial Foregoing (already installed). The remaining gap is narrow: only the top two tiers, and the design already accepts Mekanism Fusion as the literal "endgame anchor."

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
