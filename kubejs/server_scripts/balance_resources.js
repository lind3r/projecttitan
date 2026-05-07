// Resource-balance recipe overrides. See balance/resources.md (Renewable Watchlist)
// and balance/resources-CHANGELOG.md for the decision history.

ServerEvents.recipes(event => {
    // Industrial Foregoing — disable infinite-ore generator (Tier 0 watchlist item).
    // The Laser Drill + Ore Laser Base multiblock turns FE into ore indefinitely.
    // Removing the recipes makes the multiblock un-buildable in survival.
    // Lenses are left craftable; they're inert without the base.
    event.remove({ output: 'industrialforegoing:laser_drill' })
    event.remove({ output: 'industrialforegoing:ore_laser_base' })
})
