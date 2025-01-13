INSERT INTO purple_air_1 (event_time, sensor_response) VALUES (TO_TIMESTAMP(1234567890) AT TIME ZONE 'UTC', '{"test": "HelloWorld"}') RETURNING id;
