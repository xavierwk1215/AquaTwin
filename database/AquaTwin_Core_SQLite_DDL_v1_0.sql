-- AquaTwin - Digital Twin Aquarium Simulator
-- Core SQLite DDL v1.0
-- Source of Truth: AquaTwin Core Data Dictionary v1.0
-- Generated: 2026-07-13
--
-- Scope:
--   16-table transactional Core schema for the official StepContext-based path.
--
-- Important application-layer responsibilities remain:
--   finite-number validation, UTC ISO 8601 formatting, run-day completeness,
--   external Species DB integrity, parameter completeness/name-unit validation,
--   metric catalog validation, lifecycle transitions, immutability, and archival.

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ============================================================
-- 01. tank
-- ============================================================
CREATE TABLE tank (
    tank_id TEXT PRIMARY KEY
        CHECK (length(trim(tank_id)) > 0),

    tank_name TEXT NOT NULL
        CHECK (length(trim(tank_name)) > 0),

    nominal_volume_l REAL NOT NULL
        CHECK (nominal_volume_l > 0),

    tank_type TEXT,

    description TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL
);

-- ============================================================
-- 13. parameter_set
-- Created before simulation_run because it is referenced by it.
-- ============================================================
CREATE TABLE parameter_set (
    parameter_set_id TEXT PRIMARY KEY
        CHECK (length(trim(parameter_set_id)) > 0),

    parameter_set_version TEXT NOT NULL
        CHECK (length(trim(parameter_set_version)) > 0),

    model_version TEXT NOT NULL
        CHECK (length(trim(model_version)) > 0),

    organic_n_mineralization_fraction_per_day REAL NOT NULL
        CHECK (
            organic_n_mineralization_fraction_per_day >= 0
            AND organic_n_mineralization_fraction_per_day <= 1
        ),

    tan_oxidation_fraction_per_day REAL NOT NULL
        CHECK (
            tan_oxidation_fraction_per_day >= 0
            AND tan_oxidation_fraction_per_day <= 1
        ),

    nitrite_oxidation_fraction_per_day REAL NOT NULL
        CHECK (
            nitrite_oxidation_fraction_per_day >= 0
            AND nitrite_oxidation_fraction_per_day <= 1
        ),

    is_official INTEGER NOT NULL DEFAULT 0
        CHECK (is_official IN (0, 1)),

    created_at TEXT NOT NULL,

    description TEXT,

    CONSTRAINT uq_parameter_set_version
        UNIQUE (parameter_set_version),

    CONSTRAINT uq_parameter_set_version_model
        UNIQUE (parameter_set_version, model_version)
);

-- ============================================================
-- 14. simulation_profile
-- ============================================================
CREATE TABLE simulation_profile (
    profile_record_id TEXT PRIMARY KEY
        CHECK (length(trim(profile_record_id)) > 0),

    parameter_set_id TEXT NOT NULL,

    profile_id TEXT NOT NULL
        CHECK (length(trim(profile_id)) > 0),

    profile_name TEXT NOT NULL
        CHECK (length(trim(profile_name)) > 0),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_simulation_profile_set_profile
        UNIQUE (parameter_set_id, profile_id),

    CONSTRAINT fk_simulation_profile_parameter_set
        FOREIGN KEY (parameter_set_id)
        REFERENCES parameter_set(parameter_set_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

-- ============================================================
-- 15. simulation_profile_parameter
-- ============================================================
CREATE TABLE simulation_profile_parameter (
    profile_parameter_id TEXT PRIMARY KEY
        CHECK (length(trim(profile_parameter_id)) > 0),

    profile_record_id TEXT NOT NULL,

    parameter_name TEXT NOT NULL
        CHECK (length(trim(parameter_name)) > 0)
        CHECK (
            parameter_name IN (
                'adult_weight',
                'daily_feed_ratio',
                'digestibility',
                'nitrogen_fraction',
                'oxygen_consumption',
                'waste_factor',
                'metabolic_tan_excretion'
            )
        ),

    parameter_value REAL NOT NULL
        CHECK (parameter_value >= 0)
        CHECK (
            parameter_name <> 'nitrogen_fraction'
            OR parameter_value <= 1
        ),

    parameter_unit TEXT NOT NULL
        CHECK (length(trim(parameter_unit)) > 0),

    value_origin TEXT NOT NULL
        CHECK (
            value_origin IN (
                'observed',
                'derived',
                'assumed',
                'user_input'
            )
        ),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_profile_parameter_name
        UNIQUE (profile_record_id, parameter_name),

    CONSTRAINT fk_profile_parameter_profile
        FOREIGN KEY (profile_record_id)
        REFERENCES simulation_profile(profile_record_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE INDEX idx_profile_parameter_name
    ON simulation_profile_parameter(parameter_name);

-- ============================================================
-- 16. species_simulation_mapping
-- ============================================================
CREATE TABLE species_simulation_mapping (
    mapping_id TEXT PRIMARY KEY
        CHECK (length(trim(mapping_id)) > 0),

    parameter_set_id TEXT NOT NULL,

    species_id TEXT NOT NULL
        CHECK (length(trim(species_id)) > 0),

    simulation_profile_id TEXT NOT NULL
        CHECK (length(trim(simulation_profile_id)) > 0),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_species_mapping_set_species
        UNIQUE (parameter_set_id, species_id),

    CONSTRAINT fk_species_mapping_parameter_set
        FOREIGN KEY (parameter_set_id)
        REFERENCES parameter_set(parameter_set_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT fk_species_mapping_profile
        FOREIGN KEY (
            parameter_set_id,
            simulation_profile_id
        )
        REFERENCES simulation_profile (
            parameter_set_id,
            profile_id
        )
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE INDEX idx_species_mapping_species_id
    ON species_simulation_mapping(species_id);

-- ============================================================
-- 02. simulation_run
-- ============================================================
CREATE TABLE simulation_run (
    run_id TEXT PRIMARY KEY
        CHECK (length(trim(run_id)) > 0),

    tank_id TEXT NOT NULL,

    model_version TEXT NOT NULL
        CHECK (length(trim(model_version)) > 0),

    parameter_set_version TEXT NOT NULL
        CHECK (length(trim(parameter_set_version)) > 0),

    total_days INTEGER NOT NULL
        CHECK (total_days >= 1),

    scenario_name TEXT,

    description TEXT,

    run_status TEXT NOT NULL DEFAULT 'created'
        CHECK (
            run_status IN (
                'created',
                'queued',
                'running',
                'completed',
                'failed',
                'cancelled'
            )
        ),

    created_at TEXT NOT NULL,

    started_at TEXT,

    completed_at TEXT,

    updated_at TEXT NOT NULL,

    CONSTRAINT fk_simulation_run_tank
        FOREIGN KEY (tank_id)
        REFERENCES tank(tank_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT fk_simulation_run_parameter_model
        FOREIGN KEY (
            parameter_set_version,
            model_version
        )
        REFERENCES parameter_set (
            parameter_set_version,
            model_version
        )
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE INDEX idx_simulation_run_tank_id
    ON simulation_run(tank_id);

CREATE INDEX idx_simulation_run_parameter_model
    ON simulation_run(parameter_set_version, model_version);

-- ============================================================
-- 03. simulation_initial_state
-- ============================================================
CREATE TABLE simulation_initial_state (
    run_id TEXT PRIMARY KEY
        CHECK (length(trim(run_id)) > 0),

    organic_n_mass_mg REAL NOT NULL
        CHECK (organic_n_mass_mg >= 0),

    tan_mass_mg REAL NOT NULL
        CHECK (tan_mass_mg >= 0),

    nitrite_mass_mg REAL NOT NULL
        CHECK (nitrite_mass_mg >= 0),

    nitrate_mass_mg REAL NOT NULL
        CHECK (nitrate_mass_mg >= 0),

    created_at TEXT NOT NULL,

    CONSTRAINT fk_simulation_initial_state_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 08. filter_unit
-- ============================================================
CREATE TABLE filter_unit (
    filter_unit_record_id TEXT PRIMARY KEY
        CHECK (length(trim(filter_unit_record_id)) > 0),

    run_id TEXT NOT NULL,

    filter_id TEXT NOT NULL
        CHECK (length(trim(filter_id)) > 0),

    filter_type TEXT NOT NULL
        CHECK (length(trim(filter_type)) > 0),

    rated_flow_l_h REAL NOT NULL
        CHECK (rated_flow_l_h >= 0),

    actual_flow_l_h REAL NOT NULL
        CHECK (actual_flow_l_h >= 0),

    maturity_fraction REAL NOT NULL
        CHECK (maturity_fraction >= 0 AND maturity_fraction <= 1),

    fouling_fraction REAL NOT NULL
        CHECK (fouling_fraction >= 0 AND fouling_fraction <= 1),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_filter_unit_run
        UNIQUE (run_id),

    CONSTRAINT fk_filter_unit_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 09. filter_media
-- ============================================================
CREATE TABLE filter_media (
    filter_media_record_id TEXT PRIMARY KEY
        CHECK (length(trim(filter_media_record_id)) > 0),

    filter_unit_record_id TEXT NOT NULL,

    media_type TEXT NOT NULL
        CHECK (length(trim(media_type)) > 0),

    media_volume_l REAL NOT NULL
        CHECK (media_volume_l >= 0),

    tan_capacity_mg_n_l_media_day REAL NOT NULL
        CHECK (tan_capacity_mg_n_l_media_day >= 0),

    nitrite_capacity_mg_n_l_media_day REAL NOT NULL
        CHECK (nitrite_capacity_mg_n_l_media_day >= 0),

    usable_fraction REAL NOT NULL
        CHECK (usable_fraction >= 0 AND usable_fraction <= 1),

    created_at TEXT NOT NULL,

    CONSTRAINT fk_filter_media_filter_unit
        FOREIGN KEY (filter_unit_record_id)
        REFERENCES filter_unit(filter_unit_record_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

CREATE INDEX idx_filter_media_filter_unit
    ON filter_media(filter_unit_record_id);

-- ============================================================
-- 10. daily_input
-- ============================================================
CREATE TABLE daily_input (
    daily_input_record_id TEXT PRIMARY KEY
        CHECK (length(trim(daily_input_record_id)) > 0),

    run_id TEXT NOT NULL,

    simulation_day INTEGER NOT NULL
        CHECK (simulation_day >= 1),

    water_temperature_c REAL NOT NULL,

    tank_volume_l REAL NOT NULL
        CHECK (tank_volume_l > 0),

    source_tan_mg_n_l REAL NOT NULL
        CHECK (source_tan_mg_n_l >= 0),

    source_nitrite_mg_n_l REAL NOT NULL
        CHECK (source_nitrite_mg_n_l >= 0),

    source_nitrate_mg_n_l REAL NOT NULL
        CHECK (source_nitrate_mg_n_l >= 0),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_daily_input_run_day
        UNIQUE (run_id, simulation_day),

    CONSTRAINT fk_daily_input_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 04. fish_cohort
-- ============================================================
CREATE TABLE fish_cohort (
    fish_cohort_record_id TEXT PRIMARY KEY
        CHECK (length(trim(fish_cohort_record_id)) > 0),

    daily_input_record_id TEXT NOT NULL,

    species_id TEXT NOT NULL
        CHECK (length(trim(species_id)) > 0),

    fish_count INTEGER NOT NULL
        CHECK (fish_count >= 0),

    created_at TEXT NOT NULL,

    CONSTRAINT fk_fish_cohort_daily_input
        FOREIGN KEY (daily_input_record_id)
        REFERENCES daily_input(daily_input_record_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

CREATE INDEX idx_fish_cohort_daily_input
    ON fish_cohort(daily_input_record_id);

-- ============================================================
-- 05. feeding_plan
-- ============================================================
CREATE TABLE feeding_plan (
    feeding_plan_record_id TEXT PRIMARY KEY
        CHECK (length(trim(feeding_plan_record_id)) > 0),

    run_id TEXT NOT NULL,

    simulation_day INTEGER NOT NULL
        CHECK (simulation_day >= 1),

    feeding_enabled INTEGER NOT NULL
        CHECK (feeding_enabled IN (0, 1)),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_feeding_plan_run_day
        UNIQUE (run_id, simulation_day),

    CONSTRAINT fk_feeding_plan_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 06. water_change_plan
-- ============================================================
CREATE TABLE water_change_plan (
    water_change_plan_record_id TEXT PRIMARY KEY
        CHECK (length(trim(water_change_plan_record_id)) > 0),

    run_id TEXT NOT NULL,

    simulation_day INTEGER NOT NULL
        CHECK (simulation_day >= 1),

    water_change_enabled INTEGER NOT NULL
        CHECK (water_change_enabled IN (0, 1)),

    water_change_fraction REAL NOT NULL
        CHECK (water_change_fraction >= 0 AND water_change_fraction <= 1),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_water_change_plan_run_day
        UNIQUE (run_id, simulation_day),

    CONSTRAINT fk_water_change_plan_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 07. maintenance_plan
-- ============================================================
CREATE TABLE maintenance_plan (
    maintenance_plan_record_id TEXT PRIMARY KEY
        CHECK (length(trim(maintenance_plan_record_id)) > 0),

    run_id TEXT NOT NULL,

    simulation_day INTEGER NOT NULL
        CHECK (simulation_day >= 1),

    maintenance_enabled INTEGER NOT NULL
        CHECK (maintenance_enabled IN (0, 1)),

    maintenance_fraction REAL NOT NULL
        CHECK (maintenance_fraction >= 0 AND maintenance_fraction <= 1),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_maintenance_plan_run_day
        UNIQUE (run_id, simulation_day),

    CONSTRAINT fk_maintenance_plan_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 11. daily_snapshot
-- ============================================================
CREATE TABLE daily_snapshot (
    snapshot_id TEXT PRIMARY KEY
        CHECK (length(trim(snapshot_id)) > 0),

    run_id TEXT NOT NULL,

    simulation_day INTEGER NOT NULL
        CHECK (simulation_day >= 1),

    tank_volume_l REAL NOT NULL
        CHECK (tank_volume_l > 0),

    organic_n_mass_mg REAL NOT NULL
        CHECK (organic_n_mass_mg >= 0),

    tan_mass_mg REAL NOT NULL
        CHECK (tan_mass_mg >= 0),

    nitrite_mass_mg REAL NOT NULL
        CHECK (nitrite_mass_mg >= 0),

    nitrate_mass_mg REAL NOT NULL
        CHECK (nitrate_mass_mg >= 0),

    validation_passed INTEGER NOT NULL
        CHECK (validation_passed IN (0, 1)),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_daily_snapshot_run_day
        UNIQUE (run_id, simulation_day),

    CONSTRAINT fk_daily_snapshot_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_run(run_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

-- ============================================================
-- 12. daily_metric
-- ============================================================
CREATE TABLE daily_metric (
    metric_id TEXT PRIMARY KEY
        CHECK (length(trim(metric_id)) > 0),

    snapshot_id TEXT NOT NULL,

    metric_name TEXT NOT NULL
        CHECK (length(trim(metric_name)) > 0),

    metric_value REAL NOT NULL,

    metric_unit TEXT NOT NULL
        CHECK (length(trim(metric_unit)) > 0),

    created_at TEXT NOT NULL,

    CONSTRAINT uq_daily_metric_snapshot_name
        UNIQUE (snapshot_id, metric_name),

    CONSTRAINT fk_daily_metric_snapshot
        FOREIGN KEY (snapshot_id)
        REFERENCES daily_snapshot(snapshot_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

CREATE INDEX idx_daily_metric_name_snapshot
    ON daily_metric(metric_name, snapshot_id);

COMMIT;
