DROP VIEW IF EXISTS vw_water_change_effect;

CREATE VIEW vw_water_change_effect AS
SELECT
    s.simulation_day AS Day,
    CAST(w.water_change_fraction AS REAL) AS WaterChangeFraction,
    CAST(w.water_change_fraction * 100.0 AS REAL) AS WaterChangePercent,
    s.tan_mass_mg AS Tan,
    s.nitrite_mass_mg AS Nitrite,
    s.nitrate_mass_mg AS Nitrate
FROM daily_snapshot AS s
JOIN water_change_plan AS w
    ON s.run_id = w.run_id
   AND s.simulation_day = w.simulation_day
ORDER BY s.simulation_day;