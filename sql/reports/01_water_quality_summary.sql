SELECT
    simulation_day AS Day,
    organic_n_mass_mg AS Organic,
    tan_mass_mg AS Tan,
    nitrite_mass_mg AS Nitrite,
    nitrate_mass_mg AS Nitrate
FROM daily_snapshot
ORDER BY simulation_day;