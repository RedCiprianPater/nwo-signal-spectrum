-- ============================================================================
-- NWO Signal Spectrum — PostgreSQL schema (Supabase)
-- ----------------------------------------------------------------------------
-- Run once in the Supabase SQL editor (or psql against the direct URL on :5432).
-- Idempotent — safe to re-run; uses CREATE ... IF NOT EXISTS and DO blocks.
-- ============================================================================

-- ---------- Extensions ----------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------- Reusable "updated_at" trigger ----------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------- Enums (replace MySQL ENUM columns) ----------
DO $$ BEGIN
  CREATE TYPE apocalypse_severity AS ENUM ('low','medium','high','critical','extreme');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE owner_category AS ENUM ('private','corporate','government','military','unknown');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE solar_activity_type AS ENUM ('flare','cme','geomagnetic_storm','proton_event');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ============================================================================
-- Core: signals (the RF spectrum table the v1 /signals routes use)
-- ============================================================================
CREATE TABLE IF NOT EXISTS signals (
  id                 BIGSERIAL PRIMARY KEY,
  frequency_hz       BIGINT NOT NULL,
  bandwidth_hz       BIGINT NOT NULL,
  modulation         VARCHAR(32),
  signal_strength_dbm DOUBLE PRECISION,
  classification     VARCHAR(64) NOT NULL DEFAULT 'unknown',
  latitude           DOUBLE PRECISION,
  longitude          DOUBLE PRECISION,
  submitter_wallet   VARCHAR(64),
  metadata           JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_signals_freq        ON signals (frequency_hz);
CREATE INDEX IF NOT EXISTS idx_signals_class       ON signals (classification);
CREATE INDEX IF NOT EXISTS idx_signals_created     ON signals (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_submitter   ON signals (submitter_wallet);

CREATE TABLE IF NOT EXISTS signal_shares (
  id            BIGSERIAL PRIMARY KEY,
  signal_id     BIGINT NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
  share_token   VARCHAR(64) NOT NULL UNIQUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================================
-- Agents + network
-- ============================================================================
CREATE TABLE IF NOT EXISTS agents (
  id            BIGSERIAL PRIMARY KEY,
  wallet        VARCHAR(64) NOT NULL UNIQUE,
  capabilities  TEXT[]      NOT NULL DEFAULT '{}',
  region        VARCHAR(64),
  last_seen     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agents_last_seen ON agents (last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_agents_region    ON agents (region);

CREATE TABLE IF NOT EXISTS network_members (
  wallet       VARCHAR(64) PRIMARY KEY,
  joined_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_active  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================================
-- Consensus
-- ============================================================================
CREATE TABLE IF NOT EXISTS consensus_tasks (
  id                BIGSERIAL PRIMARY KEY,
  type              VARCHAR(64) NOT NULL,
  signal_id         BIGINT REFERENCES signals(id) ON DELETE SET NULL,
  proposed_class    VARCHAR(64),
  evidence          JSONB,
  payload           JSONB,
  submitter_wallet  VARCHAR(64) NOT NULL,
  consensus_result  JSONB,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at       TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_consensus_open ON consensus_tasks (resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_consensus_signal ON consensus_tasks (signal_id);

CREATE TABLE IF NOT EXISTS consensus_votes (
  id              BIGSERIAL PRIMARY KEY,
  task_id         BIGINT NOT NULL REFERENCES consensus_tasks(id) ON DELETE CASCADE,
  voter_wallet    VARCHAR(64) NOT NULL,
  classification  VARCHAR(64) NOT NULL,
  confidence      DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  notes           TEXT,
  cast_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (task_id, voter_wallet)
);
CREATE INDEX IF NOT EXISTS idx_votes_task ON consensus_votes (task_id);


-- ============================================================================
-- Apocalypse — converted 1:1 from schema-apocalypse.sql
-- ============================================================================
CREATE TABLE IF NOT EXISTS apocalypse_signals (
  id          BIGSERIAL PRIMARY KEY,
  type        VARCHAR(50) NOT NULL,
  severity    apocalypse_severity NOT NULL,
  description TEXT NOT NULL,
  metadata    JSONB,
  region      VARCHAR(50),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_apoc_type     ON apocalypse_signals (type);
CREATE INDEX IF NOT EXISTS idx_apoc_severity ON apocalypse_signals (severity);
CREATE INDEX IF NOT EXISTS idx_apoc_created  ON apocalypse_signals (created_at DESC);

CREATE TABLE IF NOT EXISTS signal_baselines (
  id           BIGSERIAL PRIMARY KEY,
  type         VARCHAR(50) NOT NULL,
  region       VARCHAR(50) NOT NULL,
  value        NUMERIC(20, 8) NOT NULL,
  sample_count INT NOT NULL DEFAULT 1,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (type, region)
);
DROP TRIGGER IF EXISTS signal_baselines_set_updated ON signal_baselines;
CREATE TRIGGER signal_baselines_set_updated
  BEFORE UPDATE ON signal_baselines
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS apocalypse_level_history (
  id              BIGSERIAL PRIMARY KEY,
  level           SMALLINT NOT NULL CHECK (level BETWEEN 1 AND 5),
  description     VARCHAR(255),
  active_signals  INT NOT NULL DEFAULT 0,
  recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_apoc_hist ON apocalypse_level_history (recorded_at DESC);

CREATE TABLE IF NOT EXISTS aircraft_sightings (
  id              BIGSERIAL PRIMARY KEY,
  icao_hex        VARCHAR(6) NOT NULL,
  callsign        VARCHAR(10),
  aircraft_type   VARCHAR(20),
  latitude        DOUBLE PRECISION,
  longitude       DOUBLE PRECISION,
  altitude        INT,
  speed           INT,
  heading         INT,
  is_business_jet BOOLEAN NOT NULL DEFAULT FALSE,
  owner_category  owner_category NOT NULL DEFAULT 'unknown',
  detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_aircraft_icao     ON aircraft_sightings (icao_hex);
CREATE INDEX IF NOT EXISTS idx_aircraft_detected ON aircraft_sightings (detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_aircraft_bizjet   ON aircraft_sightings (is_business_jet, detected_at DESC);

CREATE TABLE IF NOT EXISTS seismic_events (
  id              BIGSERIAL PRIMARY KEY,
  usgs_id         VARCHAR(50) UNIQUE,
  magnitude       NUMERIC(3, 1) NOT NULL,
  place           VARCHAR(255),
  latitude        DOUBLE PRECISION,
  longitude       DOUBLE PRECISION,
  depth           NUMERIC(8, 3),
  tsunami_warning BOOLEAN NOT NULL DEFAULT FALSE,
  felt_reports    INT,
  event_time      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_seismic_mag      ON seismic_events (magnitude);
CREATE INDEX IF NOT EXISTS idx_seismic_event_at ON seismic_events (event_time DESC);
CREATE INDEX IF NOT EXISTS idx_seismic_loc      ON seismic_events (latitude, longitude);

CREATE TABLE IF NOT EXISTS solar_activity (
  id            BIGSERIAL PRIMARY KEY,
  activity_type solar_activity_type NOT NULL,
  flare_class   VARCHAR(2),
  kp_index      SMALLINT,
  speed_kms     INT,
  direction     VARCHAR(20),
  arrival_time  TIMESTAMPTZ,
  event_time    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_solar_type     ON solar_activity (activity_type);
CREATE INDEX IF NOT EXISTS idx_solar_event_at ON solar_activity (event_time DESC);

CREATE TABLE IF NOT EXISTS radiation_readings (
  id                 BIGSERIAL PRIMARY KEY,
  sensor_id          VARCHAR(50),
  location_name      VARCHAR(100),
  latitude           DOUBLE PRECISION,
  longitude          DOUBLE PRECISION,
  value_usvh         NUMERIC(10, 6),
  baseline_usvh      NUMERIC(10, 6),
  deviation_percent  NUMERIC(8, 2),
  measured_at        TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rad_sensor   ON radiation_readings (sensor_id);
CREATE INDEX IF NOT EXISTS idx_rad_measured ON radiation_readings (measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_rad_loc      ON radiation_readings (latitude, longitude);

CREATE TABLE IF NOT EXISTS neo_objects (
  id                    BIGSERIAL PRIMARY KEY,
  nasa_id               VARCHAR(50) UNIQUE,
  name                  VARCHAR(100),
  diameter_min_m        NUMERIC(10, 3),
  diameter_max_m        NUMERIC(10, 3),
  is_hazardous          BOOLEAN NOT NULL DEFAULT FALSE,
  approach_date         DATE,
  miss_distance_km      NUMERIC(15, 3),
  miss_distance_ld      NUMERIC(10, 6),
  relative_velocity_kmh NUMERIC(12, 3),
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_neo_approach  ON neo_objects (approach_date);
CREATE INDEX IF NOT EXISTS idx_neo_hazardous ON neo_objects (is_hazardous);
CREATE INDEX IF NOT EXISTS idx_neo_distance  ON neo_objects (miss_distance_ld);


-- ============================================================================
-- Dashboard view (read by /apocalypse default endpoint)
-- ============================================================================
CREATE OR REPLACE VIEW apocalypse_dashboard AS
SELECT
  (SELECT COUNT(*) FROM apocalypse_signals
    WHERE created_at > NOW() - INTERVAL '24 hours'
      AND severity IN ('critical','extreme'))                AS critical_count,
  (SELECT COUNT(*) FROM apocalypse_signals
    WHERE created_at > NOW() - INTERVAL '24 hours')          AS total_signals_24h,
  (SELECT MAX(magnitude) FROM seismic_events
    WHERE event_time > NOW() - INTERVAL '24 hours')          AS max_quake_magnitude,
  (SELECT COUNT(*) FROM aircraft_sightings
    WHERE is_business_jet
      AND detected_at > NOW() - INTERVAL '1 hour')           AS business_jets_last_hour,
  (SELECT MAX(level) FROM apocalypse_level_history
    WHERE recorded_at > NOW() - INTERVAL '24 hours')         AS max_level_24h,
  NOW()                                                       AS last_updated;


-- ============================================================================
-- Seed baselines (matches the MySQL schema's INSERT ... ON DUPLICATE KEY UPDATE)
-- ============================================================================
INSERT INTO signal_baselines (type, region, value) VALUES
  ('aviation',  'global',  150.0),
  ('aviation',  'davos',    25.0),
  ('aviation',  'maui',     15.0),
  ('aviation',  'monaco',   30.0),
  ('radiation', 'global',    0.1),
  ('seismic',   'global',    2.5)
ON CONFLICT (type, region) DO UPDATE SET value = EXCLUDED.value;


-- ============================================================================
-- Row-Level Security (recommended for Supabase)
-- ----------------------------------------------------------------------------
-- The FastAPI service uses the service_role key (bypasses RLS) for its asyncpg
-- connection, so all the policies below only matter if you ALSO expose these
-- tables via Supabase's PostgREST. Safe defaults: deny anon, allow auth-read
-- on signals + apocalypse_signals, deny anon writes.
-- ============================================================================
ALTER TABLE signals             ENABLE ROW LEVEL SECURITY;
ALTER TABLE apocalypse_signals  ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents              ENABLE ROW LEVEL SECURITY;
ALTER TABLE consensus_tasks     ENABLE ROW LEVEL SECURITY;
ALTER TABLE consensus_votes     ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "signals readable by authenticated" ON signals;
CREATE POLICY "signals readable by authenticated"
  ON signals FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "apoc readable by authenticated" ON apocalypse_signals;
CREATE POLICY "apoc readable by authenticated"
  ON apocalypse_signals FOR SELECT TO authenticated USING (true);
