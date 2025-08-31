-- not working need to fix
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'datawave') THEN
      CREATE ROLE datawave LOGIN PASSWORD 'password';
   END IF;
END $$;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'datawave') THEN
      CREATE DATABASE datawave OWNER datawave;
   END IF;
END $$;

ALTER DATABASE datawave OWNER TO datawave;
GRANT ALL PRIVILEGES ON DATABASE datawave TO datawave;
