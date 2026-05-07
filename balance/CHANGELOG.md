# Energy Balance Changelog

Append entries top-down (newest first). Each entry: date, scope, change, reason.

## 2026-05-07 — Added Industrial Foregoing, Oritech, Draconic Evolution; Flux Networks (transport-only)

- Four new energy-related mods landed in the install. Audited each, added curated entries to `energy.json`, refreshed Coverage Table.
- **Industrial Foregoing** — 2 generators added:
  - `industrialforegoing.pitiful_generator` — 30 FE/t (furnace fuel). Ceiling **T1**.
  - `industrialforegoing.biofuel_generator` — 160 FE/t, fed by Bioreactor + farm loop. Ceiling **T2** (T3 reachable but ~100 gens is impractical).
- **Oritech** — 6 generator entries added; primary tech-tree path:
  - `basic_generator` 32 FE/t (T1), `bio_generator` 64 FE/t (T2), `lava_generator` 64 FE/t (T2), `fuel_generator` 256 FE/t (T3), `solar_generator` 32 FE/t (T1).
  - `steam_engine` listed as conversion device (50k FE/t transfer cap, 1 FE per mB steam) — excluded from coverage table because it's a transport/routing block, not a primary generator. Marked ceiling_tier `TBD`.
- **Draconic Evolution** — `draconicevolution.reactor` added with `fe_max_realistic = 15M`, ceiling **T8**.
  - Base output values are hardcoded in mod (only multipliers in `config/brandon3055/DraconicEvolution.cfg`); `reactorOutputMultiplier = 1.0` default.
  - Stable late-game tunings (~8000°C, full coil cluster) sit in 5M-15M RF/t. Higher tunings (T9+) exist but the failure mode (multi-chunk explosion) makes them impractical without containment automation, so ceiling stays T8.
  - `draconicevolution.energy_core` added as a storage-reference entry only (T1-T8 multiblock capacitor); `ceiling_tier: null`, excluded from coverage table.
- **Flux Networks** — installed but transport-only (Plug/Point/Controller/Storage). No generation. Not added to `energy.json`.
- **Coverage Table impact (the big one):**
  - T1 went from 4 → **7 mods** of coverage.
  - T2 went from 4 → **7 mods**.
  - T3 went from 3 → **5 mods**.
  - **T4-T8 went from 1 (Mekanism-only) → 2 mods** — Draconic Reactor closes the long single-mod stretch. ⚠ markers removed for T4-T8.
  - T9-T10 remain Mekanism Fusion-only ⚠. Design accepts Fusion as the literal endgame anchor.
- Recommended-mods-to-add list trimmed: Powah and Industrial Foregoing dropped (gap they targeted is now filled or installed). Bigger Reactors / NuclearCraft / Create: New Age remain as optional T9-T10 alternates.
- **No mod-config or recipe changes applied.** This is data ingestion + table refresh, not balance tuning.
- Re-ran `python scripts/audit-energy.py` afterwards: 122 files / 15 hits / 135 entries (up from 82 / 8 / 87). Discovery surfaced **Oritech Reactor** (multiblock, 25k FE/t output cap) which the manual sweep missed — added as `oritech.reactor`, ceiling **T3**. Updated Coverage Table T3 row to use Reactor as the realistic Oritech path instead of a 62-fuel-gen array.
- Discovery script gap noted: it globs `*.toml` only, so Draconic Evolution's legacy `.cfg` config doesn't appear in `energy-discovered.json`. Curation already handled DE manually.

## 2026-05-07 — Re-tiered to 10 tiers; trophy gating removed

- Tier scheme decided: **10 tiers**, replacing the prior 5-tier scaffold.
- New `tier_targets_fe_per_tick` (FE/t, sustained):
  - T1 = 1k, T2 = 4k, T3 = 16k, T4 = 60k, T5 = 250k,
  - T6 = 1M, T7 = 4M, T8 = 15M, T9 = 60M, T10 = 200M.
- Spacing is ~4× per tier — same span (1k → 200M, "starter generator → Fusion peak") split into 10 equal geometric jumps instead of 5.
- T10 anchor lowered from 100M to 200M to match `mekanism.fusion_reactor.fe_max_realistic` exactly (Fusion peak), so the top of the curve is now physical, not aspirational.
- Re-mapped every generator's `ceiling_tier` to the new scale:
  - Mekanism: solar_basic T1→T2, solar_advanced T1→T3, bio_generator T1→T3, heat_generator T1→T2, wind_generator T1→T2, gas_burning_generator T3→T6, industrial_turbine T4→T8, fission_reactor T4→T7, fusion_reactor T5→T10.
  - Createaddition: alternator T2→T3.
  - EnderIO: stirling_generator T1→T2, photovoltaic_pulsating T1→T2, photovoltaic_vibrant T1→T3 (energetic stays T1).
  - AE2: vibration_chamber T1→T2.
- Coverage Table now spans T1-T10. Lateral-options coverage is the same shape as before — tightly multi-mod through T3, then Mekanism-only — but with finer granularity (7 of 10 single-mod tiers). Recommended-mods list re-tagged to new tier numbers.
- **Trophies are gone.** The Titan Core mod no longer has `trophy_tier_X` items, so quest gating must move to a tier-event hook the mod will expose. Existing T1-T3 quests in `the_titan_core.snbt` still reference the old trophy items and need re-tasking — flagged in `CLAUDE.md` Quest Backlog.
- **No mod-config or recipe changes applied.** This is a re-labeling of the demand curve and ceiling table; downstream balance work will follow once the new tier numbers settle in-game.

## 2026-05-06 — Verified Gas-Burning Generator with Ethene

- User reported Ethene energy density via in-game JEI: 11.28 kFE/mB (matches Mekanism Wiki: 28,200 J/mB).
- Mekanism Wiki confirms Gas-Burning Generator max burn rate: 6.4 mB/t at max output, base burn 40 ticks/mB.
- **Computed peak output: 72,192 FE/t per generator with Ethene** (180,480 J/t).
- Updated `mekanism.gas_burning_generator` entry: `fe_per_block` = 72,192; `ceiling_tier` T2 → **T3**; added `fuel_data.ethene` block.
- Updated coverage table: T2 now "1 generator covers it"; T3 reachable at ~7 generators (still Mekanism-only).
- Removed gas-burning from `tbd_verifications`; Soul Engine remains deferred (user skipped).
- **No mod-config or recipe changes applied.**

## 2026-05-06 — Initial scaffold + first audit pass

- Created `balance/` ledger: `energy.md` (narrative + tier targets), `energy.json` (data schema + curated entries), this file.
- Drafted T1–T5 sustained demand targets: 1k / 25k / 500k / 10M / 100M FE/t. ~25× spacing per tier.
- Wrote `scripts/audit-energy.py` to discover generator-related TOML keys across `config/`. First run: 82 files scanned, 8 contained energy data, 87 entries. Output: `balance/energy-discovered.json`.
- Curated 16 generator entries into `energy.json` covering Mekanism (9), Createaddition (1), EnderIO (5), AE2 (1).
- 2 entries flagged TBD: Mekanism Gas-Burning Generator (per-fuel rates not in TOML) and EnderIO Soul Engine (per-soul rates not in TOML). Both need in-game JEI verification.
- **Coverage finding:** T1-T2 has multi-mod paths. T3-T5 is Mekanism-only. Lateral-options failure documented in `energy.md` Coverage Table.
- **No balance changes applied.** This is a measurement scaffold only.
