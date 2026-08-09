-- Durcissement PostgreSQL — journal d'audit inaltérable (§16).
--
-- À exécuter APRÈS `alembic upgrade head`, connecté en propriétaire de la
-- base (le rôle des migrations). Crée un rôle applicatif SANS droit de
-- suppression ni de modification sur audit_logs ; faire ensuite pointer
-- AUDIT_DATABASE_URL de l'API sur ce rôle, et réserver le rôle propriétaire
-- aux migrations.
--
--   psql -U daat_audit -d daat_audit \
--        -v app_password="'un-mot-de-passe-fort'" \
--        -f deploy/postgres-harden.sql

CREATE ROLE daat_audit_app LOGIN PASSWORD :app_password;

GRANT CONNECT ON DATABASE daat_audit TO daat_audit_app;
GRANT USAGE ON SCHEMA public TO daat_audit_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO daat_audit_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO daat_audit_app;

-- Le journal d'audit : insertion et lecture uniquement.
REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM daat_audit_app;

-- Les futures tables créées par les migrations n'héritent d'aucun droit
-- automatique : re-exécuter ce script après chaque `alembic upgrade`.
