-- eduhu-assistant: Complete schema for self-hosted PostgreSQL (Coolify migration)
-- Creates tables that were previously created directly in Supabase UI,
-- adds the match_curriculum_chunks function, and patches missing columns.

-- ═══════════════════════════════════════
-- Todos
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS todos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID NOT NULL REFERENCES teachers(id),
  text TEXT NOT NULL,
  done BOOLEAN DEFAULT false,
  due_date DATE,
  priority TEXT DEFAULT 'normal',
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_todos_teacher ON todos(teacher_id, done);

-- ═══════════════════════════════════════
-- Exercise Pages (H5P sharing)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS exercise_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID NOT NULL REFERENCES teachers(id),
  title TEXT,
  access_code TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- Exercises (H5P content)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS exercises (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id UUID NOT NULL REFERENCES exercise_pages(id) ON DELETE CASCADE,
  teacher_id UUID REFERENCES teachers(id),
  title TEXT,
  h5p_type TEXT,
  h5p_content JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exercises_page ON exercises(page_id);

-- ═══════════════════════════════════════
-- Polls (Quick Polls with QR codes)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS polls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID NOT NULL REFERENCES teachers(id),
  question TEXT NOT NULL,
  options JSONB NOT NULL DEFAULT '[]',
  votes JSONB DEFAULT '{}',
  access_code TEXT UNIQUE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_polls_code ON polls(access_code);

-- ═══════════════════════════════════════
-- Agent Sessions (multi-turn material editing)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS agent_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID REFERENCES teachers(id),
  conversation_id UUID,
  agent_type TEXT,
  material_structure JSONB DEFAULT '{}',
  message_history JSONB DEFAULT '[]',
  state JSONB DEFAULT '{}',
  status TEXT DEFAULT 'active',
  fach TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_sessions_teacher ON agent_sessions(teacher_id, status);

-- ═══════════════════════════════════════
-- Agent Knowledge (preferences, good practices, generic profiles)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS agent_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID,
  agent_type TEXT,
  fach TEXT,
  knowledge_type TEXT,
  source TEXT,
  description TEXT,
  content JSONB,
  quality_score FLOAT DEFAULT 0.5,
  times_used INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_knowledge_teacher ON agent_knowledge(teacher_id, agent_type, knowledge_type);

-- ═══════════════════════════════════════
-- Audio Pages (shareable audio collections)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS audio_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID REFERENCES teachers(id),
  title TEXT,
  access_code TEXT UNIQUE,
  audio_type TEXT,
  script JSONB,
  audio_ids JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audio_pages_code ON audio_pages(access_code);

-- ═══════════════════════════════════════
-- Patch: Add filename column to user_curricula
-- ═══════════════════════════════════════
ALTER TABLE user_curricula ADD COLUMN IF NOT EXISTS filename TEXT;

-- ═══════════════════════════════════════
-- pgvector similarity search function
-- (replaces Supabase RPC match_curriculum_chunks)
-- ═══════════════════════════════════════
CREATE OR REPLACE FUNCTION match_curriculum_chunks(
  query_embedding vector(1536),
  match_curriculum_ids text[],
  match_threshold float,
  match_count int
) RETURNS TABLE(
  id uuid,
  curriculum_id uuid,
  chunk_text text,
  section_path text,
  similarity float
) AS $$
  SELECT
    cc.id,
    cc.curriculum_id,
    cc.chunk_text,
    cc.section_path,
    (1 - (cc.embedding <=> query_embedding))::float as similarity
  FROM curriculum_chunks cc
  WHERE cc.curriculum_id::text = ANY(match_curriculum_ids)
    AND 1 - (cc.embedding <=> query_embedding) > match_threshold
  ORDER BY cc.embedding <=> query_embedding
  LIMIT match_count;
$$ LANGUAGE sql;
