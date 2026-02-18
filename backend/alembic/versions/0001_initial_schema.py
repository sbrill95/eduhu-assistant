"""Initial schema.

Revision ID: 0001
Revises: None
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      password TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    op.execute("""
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
    )
    """)

    op.execute("""
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
    )
    """)

    op.execute("""
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
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES teachers(id),
      title TEXT,
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS messages (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
      role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
      content TEXT NOT NULL,
      metadata JSONB DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS session_logs (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      conversation_id UUID UNIQUE REFERENCES conversations(id),
      user_id UUID NOT NULL REFERENCES teachers(id),
      summary TEXT,
      knowledge_extracts JSONB DEFAULT '[]',
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    op.execute("""
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
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS curriculum_chunks (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      curriculum_id UUID NOT NULL REFERENCES user_curricula(id) ON DELETE CASCADE,
      section_path TEXT,
      chunk_text TEXT NOT NULL,
      embedding vector(1536),
      metadata JSONB DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON curriculum_chunks
      USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10)
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_memories_user ON user_memories(user_id, scope)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, updated_at DESC)")

    op.execute("""
    INSERT INTO teachers (name, password) VALUES ('Demo-Lehrer', 'demo123')
    ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS curriculum_chunks CASCADE")
    op.execute("DROP TABLE IF EXISTS user_curricula CASCADE")
    op.execute("DROP TABLE IF EXISTS session_logs CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS user_memories CASCADE")
    op.execute("DROP TABLE IF EXISTS teacher_entities CASCADE")
    op.execute("DROP TABLE IF EXISTS user_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS teachers CASCADE")
