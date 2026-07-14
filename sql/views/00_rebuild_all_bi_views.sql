-- ============================================================
-- AquaTwin BI Views
-- Explicit SQLite types for ODBC / Power BI compatibility
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- Drop dependent views first
-- ============================================================

DROP VIEW IF EXISTS vw_latest_actions;
DROP VIEW IF EXISTS vw_dashboard_overview;
DROP VIEW IF EXISTS vw_filter_performance;
DROP VIEW IF EXISTS vw_nitrogen_cycle;
DROP VIEW IF EXISTS vw_water_change_effect;
DROP VIEW IF EXISTS vw_water_quality_summary;


-- ============================================================
-- 01. Water Quality Summary
-- Grain: One simulation run-day snapshot
-- ============================================================

CREATE VIEW vw_water_quality_summary AS

SELECT
    CAST(simulation_day AS INTEGER) AS Day,
    CAST(organic_n_mass_mg AS REAL) AS Organic,
    CAST(tan_mass_mg AS REAL) AS TAN,
    CAST(nitrite_mass_mg AS REAL) AS Nitrite,
    CAST(nitrate_mass_mg AS REAL) AS Nitrate

FROM daily_snapshot;


-- ============================================================
-- 02. Water Change Effect
-- Grain: One simulation run-day
-- ============================================================

CREATE VIEW vw_water_change_effect AS

SELECT
    CAST(s.simulation_day AS INTEGER) AS Day,

    CAST(
        COALESCE(w.water_change_fraction, 0.0)
        AS REAL
    ) AS WaterChangeFraction,

    CAST(
        COALESCE(w.water_change_fraction, 0.0) * 100.0
        AS REAL
    ) AS WaterChangePercent,

    CAST(s.tan_mass_mg AS REAL) AS TAN,
    CAST(s.nitrite_mass_mg AS REAL) AS Nitrite,
    CAST(s.nitrate_mass_mg AS REAL) AS Nitrate

FROM daily_snapshot AS s

LEFT JOIN water_change_plan AS w
    ON s.run_id = w.run_id
   AND s.simulation_day = w.simulation_day;


-- ============================================================
-- 03. Dashboard Overview
-- Grain: One simulation run-day
-- ============================================================

CREATE VIEW vw_dashboard_overview AS

SELECT
    CAST(r.run_id AS TEXT) AS run_id,
    CAST(r.tank_id AS TEXT) AS tank_id,
    CAST(t.tank_name AS TEXT) AS TankName,

    CAST(s.simulation_day AS INTEGER) AS Day,

    CAST(s.tan_mass_mg AS REAL) AS TAN,
    CAST(s.nitrite_mass_mg AS REAL) AS Nitrite,
    CAST(s.nitrate_mass_mg AS REAL) AS Nitrate,

    CAST(
        COALESCE(w.water_change_fraction, 0.0)
        AS REAL
    ) AS WaterChangeFraction,

    CAST(
        COALESCE(w.water_change_fraction, 0.0) * 100.0
        AS REAL
    ) AS WaterChangePercent,

    CAST(
        COALESCE(f.feeding_enabled, 0)
        AS INTEGER
    ) AS Feeding,

    CAST(
        COALESCE(m.maintenance_enabled, 0)
        AS INTEGER
    ) AS Maintenance

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


-- ============================================================
-- 04. Latest Actions
-- Grain: One row per simulation run
-- ============================================================

CREATE VIEW vw_latest_actions AS

WITH latest_day AS (

    SELECT
        CAST(run_id AS TEXT) AS run_id,
        MAX(CAST(Day AS INTEGER)) AS LatestDay

    FROM vw_dashboard_overview

    GROUP BY
        run_id
)

SELECT
    CAST(d.run_id AS TEXT) AS run_id,
    CAST(d.tank_id AS TEXT) AS tank_id,
    CAST(d.TankName AS TEXT) AS TankName,

    CAST(d.Day AS INTEGER) AS LatestDay,

    CAST(
        COALESCE(d.Feeding, 0)
        AS INTEGER
    ) AS Feeding,

    CAST(
        COALESCE(d.WaterChangePercent, 0.0)
        AS REAL
    ) AS WaterChangePercent,

    CAST(
        COALESCE(d.Maintenance, 0)
        AS INTEGER
    ) AS Maintenance

FROM vw_dashboard_overview AS d

JOIN latest_day AS l
    ON d.run_id = l.run_id
   AND d.Day = l.LatestDay;


-- ============================================================
-- 05. Filter Performance
-- Grain: One simulation run-day
-- ============================================================

CREATE VIEW vw_filter_performance AS

WITH filter_metrics AS (

    SELECT
        CAST(s.run_id AS TEXT) AS run_id,
        CAST(s.simulation_day AS INTEGER) AS simulation_day,

        MAX(
            CASE
                WHEN m.metric_name =
                    'biofilter_tan_capacity_mg_day'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS TANCapacity,

        MAX(
            CASE
                WHEN m.metric_name =
                    'potential_tan_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS TANPotential,

        MAX(
            CASE
                WHEN m.metric_name =
                    'tan_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS TANActual,

        MAX(
            CASE
                WHEN m.metric_name =
                    'biofilter_nitrite_capacity_mg_day'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS NO2Capacity,

        MAX(
            CASE
                WHEN m.metric_name =
                    'potential_nitrite_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS NO2Potential,

        MAX(
            CASE
                WHEN m.metric_name =
                    'nitrite_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS NO2Actual

    FROM daily_metric AS m

    JOIN daily_snapshot AS s
        ON m.snapshot_id = s.snapshot_id

    WHERE m.metric_name IN (
        'biofilter_tan_capacity_mg_day',
        'potential_tan_n_oxidized_mg',
        'tan_n_oxidized_mg',
        'biofilter_nitrite_capacity_mg_day',
        'potential_nitrite_n_oxidized_mg',
        'nitrite_n_oxidized_mg'
    )

    GROUP BY
        s.run_id,
        s.simulation_day
),

filter_performance AS (

    SELECT
        CAST(run_id AS TEXT) AS run_id,
        CAST(simulation_day AS INTEGER) AS simulation_day,

        CAST(TANCapacity AS REAL) AS TANCapacity,
        CAST(TANPotential AS REAL) AS TANPotential,
        CAST(TANActual AS REAL) AS TANActual,

        CAST(
            ROUND(
                TANActual /
                NULLIF(TANCapacity, 0.0),
                3
            )
            AS REAL
        ) AS TANCapacityUtilizationPercent,

        CAST(
            ROUND(
                TANActual /
                NULLIF(TANPotential, 0.0),
                3
            )
            AS REAL
        ) AS TANPotentialRealizationPercent,

        CAST(NO2Capacity AS REAL) AS NO2Capacity,
        CAST(NO2Potential AS REAL) AS NO2Potential,
        CAST(NO2Actual AS REAL) AS NO2Actual,

        CAST(
            ROUND(
                NO2Actual /
                NULLIF(NO2Capacity, 0.0),
                3
            )
            AS REAL
        ) AS NO2CapacityUtilizationPercent,

        CAST(
            ROUND(
                NO2Actual /
                NULLIF(NO2Potential, 0.0),
                3
            )
            AS REAL
        ) AS NO2PotentialRealizationPercent

    FROM filter_metrics
)

SELECT
    CAST(run_id AS TEXT) AS run_id,
    CAST(simulation_day AS INTEGER) AS simulation_day,

    CAST(TANCapacity AS REAL) AS TANCapacity,
    CAST(TANPotential AS REAL) AS TANPotential,
    CAST(TANActual AS REAL) AS TANActual,

    CAST(
        TANCapacityUtilizationPercent
        AS REAL
    ) AS TANCapacityUtilizationPercent,

    CAST(
        TANPotentialRealizationPercent
        AS REAL
    ) AS TANPotentialRealizationPercent,

    CAST(
        CASE
            WHEN TANCapacityUtilizationPercent >= 0.90
                THEN 'Saturated'
            WHEN TANCapacityUtilizationPercent >= 0.70
                THEN 'Busy'
            ELSE 'Healthy'
        END
        AS TEXT
    ) AS TANStatus,

    CAST(NO2Capacity AS REAL) AS NO2Capacity,
    CAST(NO2Potential AS REAL) AS NO2Potential,
    CAST(NO2Actual AS REAL) AS NO2Actual,

    CAST(
        NO2CapacityUtilizationPercent
        AS REAL
    ) AS NO2CapacityUtilizationPercent,

    CAST(
        NO2PotentialRealizationPercent
        AS REAL
    ) AS NO2PotentialRealizationPercent,

    CAST(
        CASE
            WHEN NO2CapacityUtilizationPercent >= 0.90
                THEN 'Saturated'
            WHEN NO2CapacityUtilizationPercent >= 0.70
                THEN 'Busy'
            ELSE 'Healthy'
        END
        AS TEXT
    ) AS NO2Status

FROM filter_performance;


-- ============================================================
-- 06. Nitrogen Cycle
-- Grain: One simulation run-day
-- ============================================================

CREATE VIEW vw_nitrogen_cycle AS

WITH nitrogen_metrics AS (

    SELECT
        CAST(s.run_id AS TEXT) AS run_id,
        CAST(s.simulation_day AS INTEGER) AS simulation_day,

        MAX(
            CASE
                WHEN m.metric_name =
                    'total_feed_nitrogen_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS FeedNitrogenInput,

        MAX(
            CASE
                WHEN m.metric_name =
                    'feed_organic_n_input_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS FeedOrganicNInput,

        MAX(
            CASE
                WHEN m.metric_name =
                    'organic_n_mineralized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS OrganicNMineralized,

        MAX(
            CASE
                WHEN m.metric_name =
                    'metabolic_tan_input_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS MetabolicTANInput,

        MAX(
            CASE
                WHEN m.metric_name =
                    'tan_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS TANOxidized,

        MAX(
            CASE
                WHEN m.metric_name =
                    'nitrite_n_oxidized_mg'
                THEN CAST(m.metric_value AS REAL)
            END
        ) AS NitriteOxidized

    FROM daily_metric AS m

    JOIN daily_snapshot AS s
        ON m.snapshot_id = s.snapshot_id

    WHERE m.metric_name IN (
        'total_feed_nitrogen_mg',
        'feed_organic_n_input_mg',
        'organic_n_mineralized_mg',
        'metabolic_tan_input_mg',
        'tan_n_oxidized_mg',
        'nitrite_n_oxidized_mg'
    )

    GROUP BY
        s.run_id,
        s.simulation_day
)

SELECT
    CAST(run_id AS TEXT) AS run_id,
    CAST(simulation_day AS INTEGER) AS simulation_day,

    CAST(
        ROUND(
            COALESCE(FeedNitrogenInput, 0.0),
            3
        )
        AS REAL
    ) AS FeedNitrogenInput,

    CAST(
        ROUND(
            COALESCE(FeedOrganicNInput, 0.0),
            3
        )
        AS REAL
    ) AS FeedOrganicNInput,

    CAST(
        ROUND(
            COALESCE(OrganicNMineralized, 0.0),
            3
        )
        AS REAL
    ) AS OrganicNMineralized,

    CAST(
        ROUND(
            COALESCE(MetabolicTANInput, 0.0),
            3
        )
        AS REAL
    ) AS MetabolicTANInput,

    CAST(
        ROUND(
            COALESCE(TANOxidized, 0.0),
            3
        )
        AS REAL
    ) AS TANOxidized,

    CAST(
        ROUND(
            COALESCE(NitriteOxidized, 0.0),
            3
        )
        AS REAL
    ) AS NitriteOxidized

FROM nitrogen_metrics;


-- ============================================================
-- Validation
-- ============================================================

SELECT
    name,
    type

FROM sqlite_master

WHERE type = 'view'
  AND name IN (
      'vw_water_quality_summary',
      'vw_water_change_effect',
      'vw_dashboard_overview',
      'vw_latest_actions',
      'vw_filter_performance',
      'vw_nitrogen_cycle'
  )

ORDER BY
    name;
    