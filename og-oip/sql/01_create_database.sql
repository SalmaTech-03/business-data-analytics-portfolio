-- OG-OIP (PetroNexa Energy - FICTIONAL, SYNTHETIC DATA). PostgreSQL 14+.
-- Run as a superuser from psql:  \i 01_create_database.sql
-- (CREATE DATABASE cannot run inside a transaction block.)
CREATE DATABASE og_oip;
\connect og_oip
CREATE SCHEMA IF NOT EXISTS og_oip;
COMMENT ON SCHEMA og_oip IS 'Synthetic PetroNexa Energy analytics schema. All data are simulated for portfolio demonstration.';
