-- Run with the database owner. Application logins are provisioned separately.
CREATE SCHEMA IF NOT EXISTS healthcare;
REVOKE ALL ON SCHEMA healthcare FROM PUBLIC;

CREATE TABLE IF NOT EXISTS healthcare.content_revisions (
    kind text NOT NULL,
    id text NOT NULL,
    sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    payload jsonb NOT NULL,
    PRIMARY KEY (kind, id, sha256)
);

CREATE TABLE IF NOT EXISTS healthcare.releases (
    id text PRIMARY KEY,
    manifest_sha256 text NOT NULL UNIQUE CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    git_commit text NOT NULL,
    base_release_id text REFERENCES healthcare.releases(id),
    record_count integer NOT NULL CHECK (record_count > 0),
    baseline_import boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz
);

CREATE TABLE IF NOT EXISTS healthcare.release_items (
    release_id text NOT NULL REFERENCES healthcare.releases(id),
    kind text NOT NULL,
    id text NOT NULL,
    content_sha256 text NOT NULL,
    PRIMARY KEY (release_id, kind, id),
    FOREIGN KEY (kind, id, content_sha256)
        REFERENCES healthcare.content_revisions(kind, id, sha256)
);

CREATE TABLE IF NOT EXISTS healthcare.publication_state (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    active_release_id text REFERENCES healthcare.releases(id)
);
INSERT INTO healthcare.publication_state(singleton, active_release_id)
VALUES (true, NULL) ON CONFLICT DO NOTHING;

CREATE OR REPLACE FUNCTION healthcare.reject_revision_change() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    RAISE EXCEPTION 'Published content is immutable; import a new revision';
END $$;
CREATE OR REPLACE FUNCTION healthcare.reject_published_item() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    PERFORM 1 FROM healthcare.releases WHERE id = NEW.release_id FOR SHARE;
    IF EXISTS (SELECT 1 FROM healthcare.releases WHERE id = NEW.release_id AND published_at IS NOT NULL) THEN
        RAISE EXCEPTION 'Published release manifest is immutable';
    END IF;
    RETURN NEW;
END $$;
CREATE OR REPLACE FUNCTION healthcare.guard_release_change() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    IF TG_OP = 'DELETE' OR OLD.published_at IS NOT NULL
       OR NEW.published_at IS NULL
       OR (to_jsonb(NEW) - 'published_at') <> (to_jsonb(OLD) - 'published_at') THEN
        RAISE EXCEPTION 'Release manifests are immutable; only first publication is allowed';
    END IF;
    RETURN NEW;
END $$;
CREATE OR REPLACE FUNCTION healthcare.guard_publication_pointer() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    IF NEW.active_release_id IS NULL OR NOT EXISTS (
        SELECT 1 FROM healthcare.releases WHERE id = NEW.active_release_id AND published_at IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'Only a published release may become active';
    END IF;
    RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS content_immutable ON healthcare.content_revisions;
CREATE TRIGGER content_immutable BEFORE UPDATE OR DELETE ON healthcare.content_revisions
FOR EACH ROW EXECUTE FUNCTION healthcare.reject_revision_change();
DROP TRIGGER IF EXISTS manifest_immutable ON healthcare.release_items;
CREATE TRIGGER manifest_immutable BEFORE UPDATE OR DELETE ON healthcare.release_items
FOR EACH ROW EXECUTE FUNCTION healthcare.reject_revision_change();
DROP TRIGGER IF EXISTS manifest_published ON healthcare.release_items;
CREATE TRIGGER manifest_published BEFORE INSERT ON healthcare.release_items
FOR EACH ROW EXECUTE FUNCTION healthcare.reject_published_item();
DROP TRIGGER IF EXISTS release_immutable ON healthcare.releases;
CREATE TRIGGER release_immutable BEFORE UPDATE OR DELETE ON healthcare.releases
FOR EACH ROW EXECUTE FUNCTION healthcare.guard_release_change();
DROP TRIGGER IF EXISTS pointer_published ON healthcare.publication_state;
CREATE TRIGGER pointer_published BEFORE UPDATE ON healthcare.publication_state
FOR EACH ROW EXECUTE FUNCTION healthcare.guard_publication_pointer();

DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'healthcare_reader') THEN
        CREATE ROLE healthcare_reader NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'healthcare_importer') THEN
        CREATE ROLE healthcare_importer NOLOGIN;
    END IF;
END $$;
REVOKE ALL ON ALL TABLES IN SCHEMA healthcare FROM PUBLIC;
GRANT USAGE ON SCHEMA healthcare TO healthcare_reader, healthcare_importer;
GRANT SELECT ON ALL TABLES IN SCHEMA healthcare TO healthcare_reader, healthcare_importer;
GRANT INSERT ON healthcare.content_revisions, healthcare.releases, healthcare.release_items TO healthcare_importer;
GRANT UPDATE (published_at) ON healthcare.releases TO healthcare_importer;
GRANT UPDATE (active_release_id) ON healthcare.publication_state TO healthcare_importer;
