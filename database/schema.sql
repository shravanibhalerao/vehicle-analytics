-- ============================================================
-- schema.sql
-- Purpose: Creates the table that stores every confirmed
--          vehicle line-crossing event.
-- ============================================================

CREATE TABLE IF NOT EXISTS vehicle_events (
    id            SERIAL PRIMARY KEY,          -- auto-increasing row number
    vehicle_id    INTEGER      NOT NULL,       -- tracking ID given by the tracker
    vehicle_type  VARCHAR(20)  NOT NULL,       -- car, bus, truck, motorcycle
    vehicle_color VARCHAR(20)  NOT NULL,       -- black, white, red, blue, silver, grey
    direction     VARCHAR(10)  NOT NULL,       -- up/down (or in/out)
    timestamp     TIMESTAMP    NOT NULL DEFAULT NOW()  -- when it crossed the line
);

-- Indexes make dashboard queries faster
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON vehicle_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_type      ON vehicle_events (vehicle_type);
CREATE INDEX IF NOT EXISTS idx_events_color     ON vehicle_events (vehicle_color);