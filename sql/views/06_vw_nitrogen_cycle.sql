DROP VIEW IF EXISTS vw_nitrogen_cycle;

CREATE VIEW vw_nitrogen_cycle AS


WITH nitrogen_metrics AS (

    SELECT
        s.run_id,
        s.simulation_day,

        MAX(
            CASE
                WHEN m.metric_name = 'total_feed_nitrogen_mg'
                THEN m.metric_value
            END
        ) AS FeedNitrogenInput,

        MAX(
            CASE
                WHEN m.metric_name = 'feed_organic_n_input_mg'
                THEN m.metric_value
            END
        ) AS FeedOrganicNInput,

        MAX(
            CASE
                WHEN m.metric_name = 'organic_n_mineralized_mg'
                THEN m.metric_value
            END
        ) AS OrganicNMineralized,

        MAX(
            CASE
                WHEN m.metric_name = 'metabolic_tan_input_mg'
                THEN m.metric_value
            END
        ) AS MetabolicTANInput,

        MAX(
            CASE
                WHEN m.metric_name = 'tan_n_oxidized_mg'
                THEN m.metric_value
            END
        ) AS TANOxidized,

        MAX(
            CASE
                WHEN m.metric_name = 'nitrite_n_oxidized_mg'
                THEN m.metric_value
            END
        ) AS NitriteOxidized

    FROM daily_metric AS m

    JOIN daily_snapshot AS s
        ON m.snapshot_id = s.snapshot_id

    GROUP BY
        s.run_id,
        s.simulation_day
)

SELECT
    run_id,
    simulation_day,

    ROUND(COALESCE(FeedNitrogenInput, 0.0), 3) AS FeedNitrogenInput,
    ROUND(COALESCE(FeedOrganicNInput, 0.0), 3) AS FeedOrganicNInput,
    ROUND(COALESCE(OrganicNMineralized, 0.0), 3) AS OrganicNMineralized,
    ROUND(COALESCE(MetabolicTANInput, 0.0), 3) AS MetabolicTANInput,
    ROUND(COALESCE(TANOxidized, 0.0), 3) AS TANOxidized,
    ROUND(COALESCE(NitriteOxidized, 0.0), 3) AS NitriteOxidized
FROM nitrogen_metrics;