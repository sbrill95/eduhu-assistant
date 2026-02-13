-- eduhu-assistant: Initial Schema
-- Based on architecture doc (12.02.2026)

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ═══════════════════════════════════════
-- Teachers (simple auth for prototype)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS teachers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- User Profiles (Zone 1 context)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY REFERENCES teachers(id),
  name TEXT NOT NULL,
  bundesland TEXT,
  schulform TEXT,
  faecher TEXT[],
  jahrgaenge INT[],
  schule TEXT,
  class_summary JSONB DEFAULT '{}',
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- Teacher Entities (classes, students)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS teacher_entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES teachers(id),
  entity_type TEXT NOT NULL CHECK (entity_type IN ('class', 'student')),
  label TEXT NOT NULL,
  parent_id UUID REFERENCES teacher_entities(id),
  schuljahr TEXT,
  metadata JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- User Memories (Memory Agent writes here)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES teachers(id),
  scope TEXT NOT NULL CHECK (scope IN ('self', 'school', 'class', 'student')),
  entity_id UUID REFERENCES teacher_entities(id),
  category TEXT NOT NULL,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  importance FLOAT DEFAULT 0.5,
  source TEXT DEFAULT 'inferred' CHECK (source IN ('explicit', 'inferred')),
  decay_days INT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, scope, category, key)
);

-- ═══════════════════════════════════════
-- Conversations
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES teachers(id),
  title TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- Messages
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- Session Logs (Memory Agent writes summaries)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS session_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID UNIQUE REFERENCES conversations(id),
  user_id UUID NOT NULL REFERENCES teachers(id),
  summary TEXT,
  knowledge_extracts JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- User Curricula (Phase 1 prep, empty for now)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_curricula (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES teachers(id),
  bundesland TEXT,
  schulform TEXT,
  fach TEXT,
  jahrgang TEXT,
  content_md TEXT,
  structure JSONB,
  wissenskarte JSONB,
  annotations JSONB DEFAULT '{}',
  progress JSONB DEFAULT '{}',
  source_type TEXT,
  schuljahr TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ═══════════════════════════════════════
-- Curriculum Chunks (RAG, Phase 1 prep)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS curriculum_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  curriculum_id UUID NOT NULL REFERENCES user_curricula(id) ON DELETE CASCADE,
  section_path TEXT,
  chunk_text TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON curriculum_chunks 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- Index for fast message loading
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_memories_user ON user_memories(user_id, scope);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, updated_at DESC);

-- ═══════════════════════════════════════
-- Seed: Demo teacher
-- ═══════════════════════════════════════
INSERT INTO teachers (name, password) VALUES ('Demo-Lehrer', 'demo123')
ON CONFLICT DO NOTHING;
