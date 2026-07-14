DROP VIEW IF EXISTS vw_latest_actions;

CREATE VIEW vw_latest_actions AS

WITH latest_day AS (

    SELECT
        run_id,
        MAX(Day) AS LatestDay

    FROM vw_dashboard_overview

    GROUP BY run_id

)

SELECT
    d.run_id,
    d.tank_id,
    d.TankName,
    d.Day AS LatestDay,
    d.Feeding,
    d.WaterChangePercent,
    d.Maintenance

FROM vw_dashboard_overview AS d

JOIN latest_day AS l

    ON d.run_id = l.run_id
   AND d.Day = l.LatestDay;