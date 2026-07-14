DROP VIEW IF EXISTS vw_dashboard_overview;

CREATE VIEW vw_dashboard_overview AS
SELECT
    r.run_id,
    r.tank_id,
    t.tank_name AS TankName,
    s.simulation_day AS Day,
    s.tan_mass_mg AS TAN,
    s.nitrite_mass_mg AS Nitrite,
    s.nitrate_mass_mg AS Nitrate,
    CAST(COALESCE(w.water_change_fraction, 0.0) AS REAL)
        AS WaterChangeFraction,
    CAST(COALESCE(w.water_change_fraction, 0.0) * 100.0 AS REAL)
        AS WaterChangePercent,
    COALESCE(f.feeding_enabled, 0) AS Feeding,
    COALESCE(m.maintenance_enabled, 0) AS Maintenance
FROM daily_snapshot AS s
JOIN simulation_run AS r
    ON s.run_id = r.run_id
JOIN tank AS t
    ON r.tank_id = t.tank_id
LEFT JOIN water_change_plan AS w
    ON s.run_id = w.run_id
   AND s.simulation_day = w.simulation_day
LEFT JOIN feeding_plan AS f
    ON s.run_id = f.run_id
   AND s.simulation_day = f.simulation_day
LEFT JOIN maintenance_plan AS m
    ON s.run_id = m.run_id
   AND s.simulation_day = m.simulation_day;