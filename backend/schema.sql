-- Emaira Architects — minimal Neon schema
-- Only tables required for auth + Launch Studio + Start an Inspection.

CREATE TABLE IF NOT EXISTS users (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_user_id    ON users ((_doc->>'user_id'));
CREATE INDEX IF NOT EXISTS idx_users_email       ON users ((_doc->>'email'));
CREATE INDEX IF NOT EXISTS idx_users_clerk_id    ON users ((_doc->>'clerk_user_id'));

CREATE TABLE IF NOT EXISTS user_sessions (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token   ON user_sessions ((_doc->>'session_token'));
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS user_activities (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS notifications (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS architects_projects (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_arch_projects_project_id ON architects_projects ((_doc->>'project_id'));
CREATE INDEX IF NOT EXISTS idx_arch_projects_user_id    ON architects_projects ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS architects_inspections (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_arch_insp_inspection_id ON architects_inspections ((_doc->>'inspection_id'));
CREATE INDEX IF NOT EXISTS idx_arch_insp_user_id        ON architects_inspections ((_doc->>'user_id'));
CREATE INDEX IF NOT EXISTS idx_arch_insp_project_id     ON architects_inspections ((_doc->>'project_id'));
CREATE INDEX IF NOT EXISTS idx_arch_insp_status         ON architects_inspections ((_doc->>'status'));

CREATE TABLE IF NOT EXISTS architects_findings (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_arch_findings_inspection_id ON architects_findings ((_doc->>'inspection_id'));
CREATE INDEX IF NOT EXISTS idx_arch_findings_user_id       ON architects_findings ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS architects_share_links (
    _doc JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_arch_share_share_id      ON architects_share_links ((_doc->>'share_id'));
CREATE INDEX IF NOT EXISTS idx_arch_share_inspection_id ON architects_share_links ((_doc->>'inspection_id'));
