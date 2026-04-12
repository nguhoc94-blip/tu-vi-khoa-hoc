CREATE TABLE IF NOT EXISTS messenger_sessions (
    sender_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    data_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messenger_sessions_updated_at_idx
    ON messenger_sessions (updated_at);

