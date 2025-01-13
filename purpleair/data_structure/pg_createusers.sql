-- Create the user for polling the sensor and inserting new rows
CREATE ROLE pa_write WITH
	LOGIN
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1
	PASSWORD '**REDACTED**';

GRANT USAGE ON SCHEMA public TO pa_write;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO pa_write;

-- Grant ability to add rows to the table or select from table
-- but nothing else.
GRANT SELECT, INSERT ON TABLE public.purple_air_1 TO pa_write;
GRANT USAGE, SELECT ON SEQUENCE public.purple_air_1_id_seq TO pa_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO pa_write;



-- ==============================================================
-- Create the user for reading data
CREATE USER pa_read WITH 
	LOGIN
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1
    PASSWORD '**REDACTED**';

GRANT SELECT ON TABLE public.purple_air_1 TO pa_read;
GRANT USAGE ON SCHEMA public TO pa_read;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pa_read;

-- Grant ability to read data only.
GRANT SELECT ON TABLE public.purple_air_1 TO pa_read;
GRANT USAGE, SELECT ON SEQUENCE public.purple_air_1_id_seq TO pa_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO pa_read;



