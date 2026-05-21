-- Emaira full schema — auth + Architects module + Emaira.Art platform

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

-- Emaira.Art platform tables

CREATE TABLE IF NOT EXISTS artworks (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_artworks_artwork_id    ON artworks ((_doc->>'artwork_id'));
CREATE INDEX IF NOT EXISTS idx_artworks_met_object_id ON artworks ((_doc->>'met_object_id'));
CREATE INDEX IF NOT EXISTS idx_artworks_featured      ON artworks ((_doc->>'is_featured'));

CREATE TABLE IF NOT EXISTS artwork_scans (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_artwork_scans_scan_id    ON artwork_scans ((_doc->>'scan_id'));
CREATE INDEX IF NOT EXISTS idx_artwork_scans_artwork_id ON artwork_scans ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS stories (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_stories_story_id   ON stories ((_doc->>'story_id'));
CREATE INDEX IF NOT EXISTS idx_stories_artwork_id ON stories ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS reviews (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_reviews_review_id  ON reviews ((_doc->>'review_id'));
CREATE INDEX IF NOT EXISTS idx_reviews_artwork_id ON reviews ((_doc->>'artwork_id'));
CREATE INDEX IF NOT EXISTS idx_reviews_user_id    ON reviews ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS review_helpful (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_review_helpful_review_id ON review_helpful ((_doc->>'review_id'));
CREATE INDEX IF NOT EXISTS idx_review_helpful_user_id   ON review_helpful ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS share_links (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_share_links_share_id  ON share_links ((_doc->>'share_id'));
CREATE INDEX IF NOT EXISTS idx_share_links_artwork_id ON share_links ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS condition_reports (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_condition_reports_report_id  ON condition_reports ((_doc->>'report_id'));
CREATE INDEX IF NOT EXISTS idx_condition_reports_artwork_id ON condition_reports ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS restoration_simulations (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_restoration_sim_sim_id     ON restoration_simulations ((_doc->>'simulation_id'));
CREATE INDEX IF NOT EXISTS idx_restoration_sim_artwork_id ON restoration_simulations ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS forensic_analyses (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_forensic_analysis_id  ON forensic_analyses ((_doc->>'analysis_id'));
CREATE INDEX IF NOT EXISTS idx_forensic_artwork_id   ON forensic_analyses ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS museum_partners (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_museum_partners_partner_id ON museum_partners ((_doc->>'partner_id'));

CREATE TABLE IF NOT EXISTS advisory_sessions (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_advisory_session_id ON advisory_sessions ((_doc->>'session_id'));
CREATE INDEX IF NOT EXISTS idx_advisory_user_id    ON advisory_sessions ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS payment_transactions (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_id ON payment_transactions ((_doc->>'transaction_id'));
CREATE INDEX IF NOT EXISTS idx_payment_user_id        ON payment_transactions ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS email_campaigns (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_campaign_id ON email_campaigns ((_doc->>'campaign_id'));

CREATE TABLE IF NOT EXISTS email_sends (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_email_sends_send_id     ON email_sends ((_doc->>'send_id'));
CREATE INDEX IF NOT EXISTS idx_email_sends_campaign_id ON email_sends ((_doc->>'campaign_id'));
CREATE INDEX IF NOT EXISTS idx_email_sends_user_id     ON email_sends ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS uploaded_images (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_uploaded_images_image_id ON uploaded_images ((_doc->>'image_id'));
CREATE INDEX IF NOT EXISTS idx_uploaded_images_user_id  ON uploaded_images ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS generated_images (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_generated_images_image_id ON generated_images ((_doc->>'image_id'));
CREATE INDEX IF NOT EXISTS idx_generated_images_user_id  ON generated_images ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS restored_images (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_restored_images_image_id ON restored_images ((_doc->>'image_id'));
CREATE INDEX IF NOT EXISTS idx_restored_images_user_id  ON restored_images ((_doc->>'user_id'));

CREATE TABLE IF NOT EXISTS vr_narratives (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_vr_narratives_narrative_id ON vr_narratives ((_doc->>'narrative_id'));
CREATE INDEX IF NOT EXISTS idx_vr_narratives_artwork_id   ON vr_narratives ((_doc->>'artwork_id'));

CREATE TABLE IF NOT EXISTS organizations (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_organizations_org_id ON organizations ((_doc->>'org_id'));

CREATE TABLE IF NOT EXISTS crm_notes (_doc JSONB NOT NULL);
CREATE INDEX IF NOT EXISTS idx_crm_notes_note_id ON crm_notes ((_doc->>'note_id'));
CREATE INDEX IF NOT EXISTS idx_crm_notes_user_id ON crm_notes ((_doc->>'user_id'));
