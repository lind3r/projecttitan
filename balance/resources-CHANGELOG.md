# Resource Balance Changelog

Append entries top-down (newest first). Each entry: date, scope, change, reason. Sister doc to `CHANGELOG.md` (energy). See `resources.md` for the framing + watchlist and `resources.json` for the curated machine ledger.

## 2026-05-07 — First-pass renewable nerfs (3 of 3 Tier 0 watchlist items)

User reviewed `resources.md` Renewable Watchlist and authorized changes to all three Tier 0 entries. Tier 1 entries left at default (built-in throttles deemed sufficient).

### 1. Industrial Foregoing — Laser Drill + Ore Laser Base disabled

- **Lever:** KubeJS recipe removal (`kubejs/server_scripts/balance_resources.js`).
- **Effect:** `industrialforegoing:laser_drill` and `industrialforegoing:ore_laser_base` recipes removed; multiblock is un-buildable in survival.
- **Items left intact:** Laser Lenses (`industrialforegoing:laser_lens`, `laser_lens_inverted`) — inert without the base, but craftable so existing player inventories don't error.
- **Items NOT touched:** `industrialforegoing:fluid_laser_base` (the fluid-generation variant — produces water/lava in biomes, not ores). Separate decision; flag for review if infinite-fluid generation becomes a concern.
- **Reason:** Tier 0 watchlist — the dominant infinite-ore exploit in the pack. With ~20k FE/t (4 active drills at default cost), would replace baseline mining outright. Recipe removal is the smallest-scope lever (preserves rest of IF) and the most decisive.
- **Why not the TOML knob:** `LaserDrillConfig.powerPerOperation` would throttle but never disable — players can always scale power. Recipe removal is binary.

### 2. Hostile Neural Networks — Loot Fabricator cost 256 → 25,600 FE/t (100x)

- **Lever:** `config/hostilenetworks.cfg` → `power.Loot Fab Power Cost`.
- **Effect:** Loot Fabricator now demands ~25.6k FE/t to run. At the energy ledger's tier targets, that puts it at T2-T3 power infrastructure (one Mekanism Bio Generator array or Createaddition farm) just to *idle*; actual cycle output requires sustained surplus.
- **Reason:** Tier 0 watchlist — synthetic mob loot at 256 FE/t was effectively free, trivializing all mob-drop scarcity. 100x is more aggressive than the 20x recommendation in `resources.md` because the user wanted a clear "endgame convenience, not mid-game replacement" signal.
- **Why not just disable:** HNN's data-model collection workflow is a fun mechanic on its own (Deep Learner UI, Predictor model trades). Killing it entirely would lose that. The cost bump preserves the flavor while gating the abuse.
- **Other knobs left default:**
  - `Sim Chamber Power Cost` not adjusted (Sim Chamber is the model-training half; cheap is fine since it doesn't produce loot directly).
  - `Right Click To Attune = true` left as-is — disabling would force kill-based training, which is just an annoyance now that Fabricator is throttled.

### 3. Apothic Spawners — Silk capture disabled (Spawner Silk Level: 1 → -1)

- **Lever:** `config/apothic_spawners.cfg` → `general.Spawner Silk Level`.
- **Effect:** Vanilla spawner blocks can no longer be picked up with Silk Touch. Apotheosis's GUI modifier UI still functions on naturally-placed spawners (in-place modification only).
- **Reason:** Tier 0 watchlist — silk-captured vanilla spawners are the canonical decade-old modpack cheese. Closing this pushes players to **EnderIO Powered Spawner** (Soul Vial workflow, energy-throttled, proximity caps) and **IF Mob Duplicator** (essence loop, energy cost) — both intended progression paths the pack already provides.
- **Other knobs left default:**
  - `Capturing Drop Chance = 0.005` left as-is. The Capturing enchant is a separate, less-direct path (probabilistic spawn-egg drop on kill). Low default chance + the rest of the spawner ecosystem nerfed, so this isn't urgent.
  - `Entity Despawn Delay = 600` left as-is.

### Tier 1 watchlist items — no change

Recorded for the audit trail:

- **IF Mob Duplicator + Crusher loop** — left default. With Apothic silk-capture closed, this becomes the *intended* mob-loot path; nerfing it now would over-correct. Reconsider only if it shows up as a problem in playthrough.
- **EnderIO Powered Spawner** — left default. `maxSpawners=10` + `maxEntities=2` already throttle.
- **Gateways to Eternity Pylons** — left default. Per-activation cost makes it more boss-arena than passive farm.

### Verification

- KubeJS recipe removal will take effect on world load / `/reload`. JEI should no longer show recipes for `Laser Drill` or `Ore Laser Base` after reload. If a player has the items pre-tuning, items remain functional but un-craftable.
- TOML changes (HNN, Apothic) take effect on game restart for existing worlds (config is reloaded at startup).
- No `/ftbquests reload` needed — quest data not touched.

### Files changed

- `kubejs/server_scripts/balance_resources.js` (new)
- `config/hostilenetworks.cfg` (cost: 256 → 25600)
- `config/apothic_spawners.cfg` (silk level: 1 → -1)
- `balance/resources.json` (watchlist `user_decision` fields populated)

After this entry: run `packwiz refresh` to update index hashes for distribution.

## 2026-05-07 — Initial scaffold

- Created `balance/resources.md` (narrative + categories + Renewable Watchlist) and `balance/resources.json` (curated per-machine ledger). Sister docs to `energy.md` / `energy.json`.
- Sourced data from four parallel research agents covering Mekanism+IF+Oritech, Create+AE2+EnderIO, mob-loot mods, and world-gen/QoL. Cross-checked load-bearing claims against installed JAR recipes (Mekanism 5x chain — only 5x via silk-touched ore blocks; raw-ore drops cap at ~2.67x via T4 chain) and live config files.
- **Watchlist Tier 0 (3 items):** IF Laser Drill, Hostile Neural Networks Loot Fabricator, Apothic Spawners silk capture. Each flagged with disable levers ranked smallest-first and a `recommendation` field.
- **Watchlist Tier 1 (3 items):** IF Duplicator+Crusher loop, EnderIO Powered Spawner, Gateways Pylons. Each has built-in throttles; recommendation is leave-default.
- **Watchlist Tier 2:** Quietly renewable systems (AE2 Budding Certus, Ars Drygmy, Solar Neutron Activator, IF crops, vanilla iron golem farms, Apotheosis Boss Summoner, Cataclysm bosses, Quark Biotite). Acceptable as-is.
- **No mod-config or recipe changes applied.** Measurement scaffold only.
