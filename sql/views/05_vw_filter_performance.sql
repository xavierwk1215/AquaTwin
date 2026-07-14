DROP VIEW IF EXISTS vw_filter_performance;

CREATE VIEW vw_filter_performance AS

WITH filter_metrics AS (

    SELECT
        s.run_id,
        s.simulation_day,

        MAX(
            CASE
                WHEN m.metric_name = 'biofilter_tan_capacity_mg_day'
                THEN m.metric_value
            END
        ) AS TANCapacity,

        MAX(
            CASE
                WHEN m.metric_name = 'potential_tan_n_oxidized_mg'
                THEN m.metric_value
            END
        ) AS TANPotential,

        MAX(
            CASE
                WHEN m.metric_name = 'tan_n_oxidized_mg'
                THEN m.metric_value
            END
        ) AS TANActual,

        MAX(
            CASE
                WHEN m.metric_name = 'biofilter_nitrite_capacity_mg_day'
                THEN m.metric_value
            END
        ) AS NO2Capacity,

        MAX(
            CASE
                WHEN m.metric_name = 'potential_nitrite_n_oxidized_mg'
                THEN m.metric_value
            END
        ) AS NO2Potential,

        MAX(
            CASE
                WHEN m.metric_name = 'nitrite_n_oxidized_mg'
                THEN m.metric_value
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
        run_id,
        simulation_day,

        TANCapacity,
        TANPotential,
        TANActual,

        ROUND(
            TANActual / NULLIF(TANCapacity, 0),
            3
        ) AS TANCapacityUtilizationPercent,

        ROUND(
            TANActual / NULLIF(TANPotential, 0),
            3
        ) AS TANPotentialRealizationPercent,

        NO2Capacity,
        NO2Potential,
        NO2Actual,

        ROUND(
            NO2Actual / NULLIF(NO2Capacity, 0),
            3
        ) AS NO2CapacityUtilizationPercent,

        ROUND(
            NO2Actual / NULLIF(NO2Potential, 0),
            3
        ) AS NO2PotentialRealizationPercent

    FROM filter_metrics
)

SELECT
    run_id,
    simulation_day,

    TANCapacity,
    TANPotential,
    TANActual,
    TANCapacityUtilizationPercent,
    TANPotentialRealizationPercent,

    CASE
        WHEN TANCapacityUtilizationPercent >= 0.90
            THEN 'Saturated'
        WHEN TANCapacityUtilizationPercent >= 0.70
            THEN 'Busy'
        ELSE 'Healthy'
    END AS TANStatus,

    NO2Capacity,
    NO2Potential,
    NO2Actual,
    NO2CapacityUtilizationPercent,
    NO2PotentialRealizationPercent,

    CASE
        WHEN NO2CapacityUtilizationPercent >= 0.90
            THEN 'Saturated'
        WHEN NO2CapacityUtilizationPercent >= 0.70
            THEN 'Busy'
        ELSE 'Healthy'
    END AS NO2Status

FROM filter_performance;