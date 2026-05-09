// Resource-balance recipe overrides. See balance/resources.md (Renewable Watchlist)
// and balance/resources-CHANGELOG.md for the decision history.

ServerEvents.recipes(event => {
    // Industrial Foregoing — disable infinite-ore generator (Tier 0 watchlist item).
    // The Laser Drill + Ore Laser Base multiblock turns FE into ore indefinitely.
    // Removing the recipes makes the multiblock un-buildable in survival.
    // Lenses are left craftable; they're inert without the base.
    event.remove({ output: 'industrialforegoing:laser_drill' })
    event.remove({ output: 'industrialforegoing:ore_laser_base' })

    // No-automated-mining policy: the pack pushes players toward AdLods deposits
    // and hand-mining. These three machines bypass that loop:
    //   - Mekanism Digital Miner: filtered chunk-strip miner.
    //   - Oritech Deep Drill ("Bedrock Extractor" in-game): mines resource nodes for free ore.
    //   - CC: Tweaked Turtles: scriptable mining/placing robot.
    // Computers, peripherals, modems, and disks stay craftable — only the
    // mining-arm variants are gated. Both turtle tiers cover the upgrade-overlay
    // recipes that bake in tools/modems on craft.
    event.remove({ output: 'mekanism:digital_miner' })
    event.remove({ output: 'oritech:deep_drill_block' })
    event.remove({ output: 'computercraft:turtle_normal' })
    event.remove({ output: 'computercraft:turtle_advanced' })
})
