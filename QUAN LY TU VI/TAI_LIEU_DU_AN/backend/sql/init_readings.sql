CREATE TABLE IF NOT EXISTS readings (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    normalized_input_json JSONB NOT NULL,
    chart_json JSONB NOT NULL,
    free_teaser TEXT NOT NULL,
    full_reading TEXT,
    is_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS readings_sender_id_created_at_idx
    ON readings (sender_id, created_at DESC);

