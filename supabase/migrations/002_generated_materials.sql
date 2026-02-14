-- Persistent storage for generated materials (DOCX + metadata)
CREATE TABLE IF NOT EXISTS generated_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID REFERENCES teachers(id),
    type TEXT NOT NULL,
    content_json JSONB NOT NULL,
    docx_base64 TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
