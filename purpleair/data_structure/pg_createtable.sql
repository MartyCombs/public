-- All JSON data is stored in one column
-- The event_time is for Postgres time queries
-- The id makes it easier to index
CREATE TABLE purple_air_1 (
    id                 SERIAL PRIMARY KEY,
    event_time         TIMESTAMP WITH TIME ZONE UNIQUE NOT NULL,
    sensor_response    JSONB
);
