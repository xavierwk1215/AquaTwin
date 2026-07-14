-- AquaTwin - Digital Twin Aquarium Simulator
-- Golden Scenario INSERT Package v1.0
-- Source: official two-day deterministic Golden Scenario
-- Target: AquaTwin Core SQLite DDL v1.0
-- Generated: 2026-07-13
-- Corrected reconciliation: 17 Day-1 metrics + 11 Day-2 metrics = 28 metrics; 55 total rows.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- tank: 1 row(s)
INSERT INTO tank (
    tank_id,
    tank_name,
    nominal_volume_l,
    tank_type,
    description,
    is_active,
    created_at,
    updated_at
) VALUES
    ('tank-golden-001', 'Golden Test Tank', 100.0, 'freshwater', 'Deterministic database Golden Scenario tank', 1, '2026-07-13T08:00:00Z', '2026-07-13T08:00:00Z');

-- parameter_set: 1 row(s)
INSERT INTO parameter_set (
    parameter_set_id,
    parameter_set_version,
    model_version,
    organic_n_mineralization_fraction_per_day,
    tan_oxidation_fraction_per_day,
    nitrite_oxidation_fraction_per_day,
    is_official,
    created_at,
    description
) VALUES
    ('ps-golden-001', 'golden-parameters-v1', 'golden-model-v1', 0.2, 0.5, 0.5, 1, '2026-07-13T08:00:00Z', 'Official deterministic Golden Scenario parameter release');

-- simulation_profile: 1 row(s)
INSERT INTO simulation_profile (
    profile_record_id,
    parameter_set_id,
    profile_id,
    profile_name,
    created_at
) VALUES
    ('profile-record-golden-001', 'ps-golden-001', 'golden-profile', 'Golden Scenario Fish', '2026-07-13T08:00:00Z');

-- simulation_profile_parameter: 7 row(s)
INSERT INTO simulation_profile_parameter (
    profile_parameter_id,
    profile_record_id,
    parameter_name,
    parameter_value,
    parameter_unit,
    value_origin,
    created_at
) VALUES
    ('pp-golden-adult-weight', 'profile-record-golden-001', 'adult_weight', 10.0, 'g/fish', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-feed-ratio', 'profile-record-golden-001', 'daily_feed_ratio', 0.01, 'fraction/day', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-digestibility', 'profile-record-golden-001', 'digestibility', 0.8, 'fraction', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-nitrogen-fraction', 'profile-record-golden-001', 'nitrogen_fraction', 0.05, 'fraction', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-oxygen-consumption', 'profile-record-golden-001', 'oxygen_consumption', 1.0, 'mg-O2/g/day', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-waste-factor', 'profile-record-golden-001', 'waste_factor', 1.0, 'fraction', 'assumed', '2026-07-13T08:00:00Z'),
    ('pp-golden-metabolic-tan', 'profile-record-golden-001', 'metabolic_tan_excretion', 0.1, 'mg-N/g/day', 'assumed', '2026-07-13T08:00:00Z');

-- species_simulation_mapping: 1 row(s)
INSERT INTO species_simulation_mapping (
    mapping_id,
    parameter_set_id,
    species_id,
    simulation_profile_id,
    created_at
) VALUES
    ('mapping-golden-001', 'ps-golden-001', 'golden-species', 'golden-profile', '2026-07-13T08:00:00Z');

-- simulation_run: 1 row(s)
INSERT INTO simulation_run (
    run_id,
    tank_id,
    model_version,
    parameter_set_version,
    total_days,
    scenario_name,
    description,
    run_status,
    created_at,
    started_at,
    completed_at,
    updated_at
) VALUES
    ('golden-run-001', 'tank-golden-001', 'golden-model-v1', 'golden-parameters-v1', 2, 'Official Two-Day Golden Scenario', 'Code-backed deterministic scenario for DB, SQL, replay, and BI validation', 'completed', '2026-07-13T08:00:00Z', '2026-07-13T08:01:00Z', '2026-07-13T08:02:00Z', '2026-07-13T08:02:00Z');

-- simulation_initial_state: 1 row(s)
INSERT INTO simulation_initial_state (
    run_id,
    organic_n_mass_mg,
    tan_mass_mg,
    nitrite_mass_mg,
    nitrate_mass_mg,
    created_at
) VALUES
    ('golden-run-001', 0.0, 8.0, 4.0, 10.0, '2026-07-13T08:00:00Z');

-- filter_unit: 1 row(s)
INSERT INTO filter_unit (
    filter_unit_record_id,
    run_id,
    filter_id,
    filter_type,
    rated_flow_l_h,
    actual_flow_l_h,
    maturity_fraction,
    fouling_fraction,
    created_at
) VALUES
    ('filter-unit-record-golden-001', 'golden-run-001', 'golden-filter', 'canister', 500.0, 400.0, 1.0, 0.0, '2026-07-13T08:00:00Z');

-- filter_media: 1 row(s)
INSERT INTO filter_media (
    filter_media_record_id,
    filter_unit_record_id,
    media_type,
    media_volume_l,
    tan_capacity_mg_n_l_media_day,
    nitrite_capacity_mg_n_l_media_day,
    usable_fraction,
    created_at
) VALUES
    ('filter-media-golden-001', 'filter-unit-record-golden-001', 'golden-biological-media', 1.0, 3.0, 2.0, 1.0, '2026-07-13T08:00:00Z');

-- daily_input: 2 row(s)
INSERT INTO daily_input (
    daily_input_record_id,
    run_id,
    simulation_day,
    water_temperature_c,
    tank_volume_l,
    source_tan_mg_n_l,
    source_nitrite_mg_n_l,
    source_nitrate_mg_n_l,
    created_at
) VALUES
    ('daily-input-golden-d1', 'golden-run-001', 1, 25.0, 100.0, 0.04, 0.02, 0.1, '2026-07-13T08:00:00Z'),
    ('daily-input-golden-d2', 'golden-run-001', 2, 25.0, 100.0, 0.0, 0.0, 0.0, '2026-07-13T08:00:00Z');

-- fish_cohort: 2 row(s)
INSERT INTO fish_cohort (
    fish_cohort_record_id,
    daily_input_record_id,
    species_id,
    fish_count,
    created_at
) VALUES
    ('fish-cohort-golden-d1', 'daily-input-golden-d1', 'golden-species', 2, '2026-07-13T08:00:00Z'),
    ('fish-cohort-golden-d2', 'daily-input-golden-d2', 'golden-species', 2, '2026-07-13T08:00:00Z');

-- feeding_plan: 2 row(s)
INSERT INTO feeding_plan (
    feeding_plan_record_id,
    run_id,
    simulation_day,
    feeding_enabled,
    created_at
) VALUES
    ('feeding-plan-golden-d1', 'golden-run-001', 1, 1, '2026-07-13T08:00:00Z'),
    ('feeding-plan-golden-d2', 'golden-run-001', 2, 0, '2026-07-13T08:00:00Z');

-- water_change_plan: 2 row(s)
INSERT INTO water_change_plan (
    water_change_plan_record_id,
    run_id,
    simulation_day,
    water_change_enabled,
    water_change_fraction,
    created_at
) VALUES
    ('water-change-plan-golden-d1', 'golden-run-001', 1, 1, 0.25, '2026-07-13T08:00:00Z'),
    ('water-change-plan-golden-d2', 'golden-run-001', 2, 0, 0.0, '2026-07-13T08:00:00Z');

-- maintenance_plan: 2 row(s)
INSERT INTO maintenance_plan (
    maintenance_plan_record_id,
    run_id,
    simulation_day,
    maintenance_enabled,
    maintenance_fraction,
    created_at
) VALUES
    ('maintenance-plan-golden-d1', 'golden-run-001', 1, 0, 0.0, '2026-07-13T08:00:00Z'),
    ('maintenance-plan-golden-d2', 'golden-run-001', 2, 1, 0.2, '2026-07-13T08:00:00Z');

-- daily_snapshot: 2 row(s)
INSERT INTO daily_snapshot (
    snapshot_id,
    run_id,
    simulation_day,
    tank_volume_l,
    organic_n_mass_mg,
    tan_mass_mg,
    nitrite_mass_mg,
    nitrate_mass_mg,
    validation_passed,
    created_at
) VALUES
    ('snapshot-golden-d1', 'golden-run-001', 1, 100.0, 10.0, 6.0, 4.5, 12.0, 1, '2026-07-13T08:00:00Z'),
    ('snapshot-golden-d2', 'golden-run-001', 2, 100.0, 6.0, 7.0, 5.5, 14.0, 1, '2026-07-13T08:00:00Z');

-- daily_metric: 28 row(s)
INSERT INTO daily_metric (
    metric_id,
    snapshot_id,
    metric_name,
    metric_value,
    metric_unit,
    created_at
) VALUES
    ('metric-golden-d1-01', 'snapshot-golden-d1', 'water_change_n_removal_mg', 5.5, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-02', 'snapshot-golden-d1', 'source_water_n_input_mg', 4.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-03', 'snapshot-golden-d1', 'water_change_fraction', 0.25, 'fraction', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-04', 'snapshot-golden-d1', 'total_biomass_g', 20.0, 'g', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-05', 'snapshot-golden-d1', 'total_feed_mass_g', 0.2, 'g', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-06', 'snapshot-golden-d1', 'total_feed_nitrogen_mg', 10.000000000000002, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-07', 'snapshot-golden-d1', 'feed_organic_n_input_mg', 10.000000000000002, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-08', 'snapshot-golden-d1', 'organic_n_mineralized_mg', 0.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-09', 'snapshot-golden-d1', 'fish_biomass_g', 20.0, 'g', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-10', 'snapshot-golden-d1', 'fish_oxygen_consumption_mg', 20.0, 'mg-O2', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-11', 'snapshot-golden-d1', 'metabolic_tan_input_mg', 2.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-12', 'snapshot-golden-d1', 'biofilter_tan_capacity_mg_day', 3.0, 'mg-N/day', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-13', 'snapshot-golden-d1', 'biofilter_nitrite_capacity_mg_day', 2.0, 'mg-N/day', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-14', 'snapshot-golden-d1', 'potential_tan_n_oxidized_mg', 4.5, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-15', 'snapshot-golden-d1', 'tan_n_oxidized_mg', 3.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-16', 'snapshot-golden-d1', 'potential_nitrite_n_oxidized_mg', 3.25, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d1-17', 'snapshot-golden-d1', 'nitrite_n_oxidized_mg', 2.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-01', 'snapshot-golden-d2', 'maintenance_n_removal_mg', 2.0000000000000004, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-02', 'snapshot-golden-d2', 'organic_n_mineralized_mg', 2.0000000000000004, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-03', 'snapshot-golden-d2', 'fish_biomass_g', 20.0, 'g', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-04', 'snapshot-golden-d2', 'fish_oxygen_consumption_mg', 20.0, 'mg-O2', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-05', 'snapshot-golden-d2', 'metabolic_tan_input_mg', 2.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-06', 'snapshot-golden-d2', 'biofilter_tan_capacity_mg_day', 3.0, 'mg-N/day', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-07', 'snapshot-golden-d2', 'biofilter_nitrite_capacity_mg_day', 2.0, 'mg-N/day', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-08', 'snapshot-golden-d2', 'potential_tan_n_oxidized_mg', 5.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-09', 'snapshot-golden-d2', 'tan_n_oxidized_mg', 3.0, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-10', 'snapshot-golden-d2', 'potential_nitrite_n_oxidized_mg', 3.75, 'mg-N', '2026-07-13T08:00:00Z'),
    ('metric-golden-d2-11', 'snapshot-golden-d2', 'nitrite_n_oxidized_mg', 2.0, 'mg-N', '2026-07-13T08:00:00Z');

COMMIT;

-- Verification queries (read-only)
PRAGMA foreign_key_check;

SELECT 'tank' AS table_name, COUNT(*) AS row_count FROM tank
UNION ALL SELECT 'parameter_set', COUNT(*) FROM parameter_set
UNION ALL SELECT 'simulation_profile', COUNT(*) FROM simulation_profile
UNION ALL SELECT 'simulation_profile_parameter', COUNT(*) FROM simulation_profile_parameter
UNION ALL SELECT 'species_simulation_mapping', COUNT(*) FROM species_simulation_mapping
UNION ALL SELECT 'simulation_run', COUNT(*) FROM simulation_run
UNION ALL SELECT 'simulation_initial_state', COUNT(*) FROM simulation_initial_state
UNION ALL SELECT 'filter_unit', COUNT(*) FROM filter_unit
UNION ALL SELECT 'filter_media', COUNT(*) FROM filter_media
UNION ALL SELECT 'daily_input', COUNT(*) FROM daily_input
UNION ALL SELECT 'fish_cohort', COUNT(*) FROM fish_cohort
UNION ALL SELECT 'feeding_plan', COUNT(*) FROM feeding_plan
UNION ALL SELECT 'water_change_plan', COUNT(*) FROM water_change_plan
UNION ALL SELECT 'maintenance_plan', COUNT(*) FROM maintenance_plan
UNION ALL SELECT 'daily_snapshot', COUNT(*) FROM daily_snapshot
UNION ALL SELECT 'daily_metric', COUNT(*) FROM daily_metric
;

SELECT s.simulation_day, s.organic_n_mass_mg, s.tan_mass_mg, s.nitrite_mass_mg, s.nitrate_mass_mg, COUNT(m.metric_id) AS metric_count
FROM daily_snapshot AS s
LEFT JOIN daily_metric AS m ON m.snapshot_id = s.snapshot_id
WHERE s.run_id = 'golden-run-001'
GROUP BY s.snapshot_id, s.simulation_day
ORDER BY s.simulation_day;
