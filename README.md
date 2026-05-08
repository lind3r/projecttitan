# Project Titan

A NeoForge modpack for Minecraft 1.21.1 built around a 10-tier progression chain: build the **Titan Core**, feed it shards (Mote → Heart of the Titan), and unlock the world's response one tier at a time. Endgame is the **Titan Trial** — a single-wave Cataclysm-boss gauntlet that drops the Crown of the Titan and closes out the questline.

> ⚠️ **Under active development.** No stable release yet — version 0.1.0 is a working snapshot, content and balance are still in motion. Expect breakage on updates, missing polish, and quests/recipes that may shift.

## At a glance

- **Minecraft:** 1.21.1
- **Loader:** NeoForge 21.1.228
- **Mods:** 121 (full list: [`MODLIST.md`](MODLIST.md))
- **Anchor mod:** [`projecttitancore`](https://github.com/lind3r/projecttitancore) — custom mod developed alongside this pack
- **Quests:** FTB Quests, 10-tier chain (Mote of the Titan → Heart of the Titan → Titan Trial → Coronation)
- **Theme:** holy / divine — ivory marble, gold accents, halos and sunbursts

## Installing

The pack is distributed as a Modrinth `.mrpack` file (built with [packwiz](https://packwiz.infra.link/)). Once a release is cut you'll be able to grab it from the Releases page; in the meantime you can build it yourself:

```bash
# from the repo root
packwiz modrinth export
```

That produces `Project Titan-<version>.mrpack`, which any of these launchers can import directly:

- [Modrinth App](https://modrinth.com/app)
- [Prism Launcher](https://prismlauncher.org/)
- [ATLauncher](https://atlauncher.com/)
- [MultiMC](https://multimc.org/)

Alternatively, [`MODLIST.md`](MODLIST.md) and [`MODLIST.txt`](MODLIST.txt) are human-readable manifests if you just want to see what's in the pack.

## Repository layout

```
mods/                 packwiz mod metadata (one .pw.toml per mod)
config/               default mod configs shipped with the pack
defaultconfigs/       NeoForge per-world config seeds
kubejs/               KubeJS scripts (recipes, events, server-side tweaks)
resourcepacks/        bundled resource packs (currently empty)
balance/              design notes for progression and recipe balance
scripts/              dev helpers (modlist generation, packwiz rebuild, save sync)
pack.toml             packwiz pack manifest
index.toml            packwiz file index
```

## Status

This is a personal project being developed in the open. Everything works at the level it's been tested at, but the pack hasn't yet been through a polish pass — quest text, recipe balance, and the per-tier world response are all WIP. Once the endgame loop is fully wired up and tested end-to-end, expect a tagged 1.0 release.

The shard chain (T1–T10), Titan Trial gateway, and the closing Coronation quest are all implemented but **not yet end-to-end tested in-game** as of 2026-05-08.
