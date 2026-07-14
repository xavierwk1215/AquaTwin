-- ============================================================
-- 07. Filter Performance Chart
-- Purpose: Power BI presentation view for TAN / NO2 comparison
-- Grain: One simulation run-day-process
-- ============================================================

DROP VIEW IF EXISTS vw_filter_performance_chart;

CREATE VIEW vw_filter_performance_chart AS

SELECT
    CAST(f.run_id AS TEXT) AS run_id,
    CAST(r.tank_id AS TEXT) AS tank_id,
    CAST(f.simulation_day AS INTEGER) AS simulation_day,
    CAST(1 AS INTEGER) AS ProcessSort,
    CAST('TAN' AS TEXT) AS Process,
    CAST(f.TANCapacity AS REAL) AS Capacity,
    CAST(f.TANActual AS REAL) AS Actual,
    CAST(f.TANPotential AS REAL) AS Potential,
    CAST(
        f.TANCapacityUtilizationPercent
        AS REAL
    ) AS CapacityUtilization,
    CAST(
        f.TANPotentialRealizationPercent
        AS REAL
    ) AS PotentialRealization,
    CAST(f.TANStatus AS TEXT) AS Status

FROM vw_filter_performance AS f

JOIN simulation_run AS r
    ON f.run_id = r.run_id

UNION ALL

SELECT
    CAST(f.run_id AS TEXT) AS run_id,
    CAST(r.tank_id AS TEXT) AS tank_id,
    CAST(f.simulation_day AS INTEGER) AS simulation_day,
    CAST(2 AS INTEGER) AS ProcessSort,
    CAST('NO2' AS TEXT) AS Process,
    CAST(f.NO2Capacity AS REAL) AS Capacity,
    CAST(f.NO2Actual AS REAL) AS Actual,
    CAST(f.NO2Potential AS REAL) AS Potential,
    CAST(
        f.NO2CapacityUtilizationPercent
        AS REAL
    ) AS CapacityUtilization,
    CAST(
        f.NO2PotentialRealizationPercent
        AS REAL
    ) AS PotentialRealization,
    CAST(f.NO2Status AS TEXT) AS Status

FROM vw_filter_performance AS f

JOIN simulation_run AS r
    ON f.run_id = r.run_id;


-- ============================================================
-- Validation
-- ============================================================

SELECT
    run_id,
    tank_id,
    simulation_day,
    ProcessSort,
    Process,
    Capacity,
    Actual,
    Potential,
    CapacityUtilization,
    PotentialRealization,
    Status

FROM vw_filter_performance_chart

ORDER BY
    run_id,
    simulation_day,
    ProcessSort;