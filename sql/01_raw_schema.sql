CREATE SCHEMA IF NOT EXISTS raw;

-- One row per line per hourly snapshot; full API payload kept as JSON
CREATE TABLE IF NOT EXISTS raw.tfl_line_status (
    line_id        TEXT        NOT NULL,
    snapshot_hour  TIMESTAMPTZ NOT NULL,
    payload        JSONB       NOT NULL,
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (line_id, snapshot_hour)
);

-- One row per hour
CREATE TABLE IF NOT EXISTS raw.weather_hourly (
    observation_time  TIMESTAMPTZ PRIMARY KEY,
    temperature_c     NUMERIC,
    precipitation_mm  NUMERIC,
    wind_speed_kmh    NUMERIC,
    weather_code      INTEGER,
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);