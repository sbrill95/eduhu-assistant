import type { ChatMessage, Conversation } from './types';
import { getSession } from './auth';

const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'https://eduhu-assistant.onrender.com';

export async function sendMessage(
  message: string,
  conversationId: string | null,
): Promise<{ conversation_id: string; message: ChatMessage }> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      teacher_id: teacher.teacher_id,
    }),
  });

  if (!res.ok) {
    throw new Error('Nachricht konnte nicht gesendet werden.');
  }

  return res.json() as Promise<{ conversation_id: string; message: ChatMessage }>;
}

export async function getHistory(conversationId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${BASE}/api/chat/history?conversation_id=${conversationId}`);
  if (!res.ok) throw new Error('Verlauf konnte nicht geladen werden.');
  const data = (await res.json()) as { messages: ChatMessage[] };
  return data.messages;
}

export async function getConversations(): Promise<Conversation[]> {
  const teacher = getSession();
  if (!teacher) return [];

  const res = await fetch(`${BASE}/api/chat/conversations?teacher_id=${teacher.teacher_id}`);
  if (!res.ok) return [];
  return res.json() as Promise<Conversation[]>;
}

// ── Curriculum API ──

export interface Curriculum {
  id: string;
  fach: string;
  jahrgang: string;
  bundesland: string;
  status: string;
  filename: string;
  created_at: string;
}

export async function uploadCurriculum(
  file: File,
  fach: string,
  jahrgang: string,
  bundesland: string,
): Promise<{ curriculum_id: string; chunks: number; status: string }> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const form = new FormData();
  form.append('file', file);
  form.append('teacher_id', teacher.teacher_id);
  form.append('fach', fach);
  form.append('jahrgang', jahrgang);
  form.append('bundesland', bundesland);

  const res = await fetch(`${BASE}/api/curriculum/upload`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload fehlgeschlagen' }));
    throw new Error(err.detail || 'Upload fehlgeschlagen');
  }

  return res.json() as Promise<{ curriculum_id: string; chunks: number; status: string }>;
}

export async function listCurricula(): Promise<Curriculum[]> {
  const teacher = getSession();
  if (!teacher) return [];

  const res = await fetch(`${BASE}/api/curriculum/list?teacher_id=${teacher.teacher_id}`);
  if (!res.ok) return [];
  return res.json() as Promise<Curriculum[]>;
}

export async function deleteCurriculum(curriculumId: string): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  await fetch(`${BASE}/api/curriculum/${curriculumId}?teacher_id=${teacher.teacher_id}`, {
    method: 'DELETE',
  });
}

// ── Profile API ──

export interface Profile {
  id: string;
  name: string;
  bundesland?: string;
  schulform?: string;
  faecher?: string[];
  jahrgaenge?: number[];
}

export async function getProfile(): Promise<Profile | null> {
  const teacher = getSession();
  if (!teacher) return null;

  const res = await fetch(`${BASE}/api/profile/${teacher.teacher_id}`);
  if (!res.ok) return null;
  return res.json() as Promise<Profile>;
}

export async function updateProfile(data: Partial<Profile>): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  await fetch(`${BASE}/api/profile/${teacher.teacher_id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

// ── Conversation Management ──

export async function deleteConversation(conversationId: string): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  await fetch(`${BASE}/api/chat/conversations/${conversationId}?teacher_id=${teacher.teacher_id}`, {
    method: 'DELETE',
  });
}
