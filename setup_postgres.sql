-- PostgreSQL setup script for dating app with pgvector

-- Create database (run as postgres superuser)
CREATE DATABASE dating_app;

-- Connect to the database
\c dating_app;

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create user (optional, for security)
-- CREATE USER dating_app_user WITH PASSWORD 'your_password';
-- GRANT ALL PRIVILEGES ON DATABASE dating_app TO dating_app_user;

-- Verify pgvector installation
SELECT * FROM pg_extension WHERE extname = 'vector';