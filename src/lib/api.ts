import { type ChatMessage, type Conversation } from './types';
import { getSession } from './auth';

export const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';
const BASE = API_BASE;

function getAuthHeaders(teacherId: string) {
  return {
    'Content-Type': 'application/json',
    'X-Teacher-ID': teacherId, // Inject header for security middleware
  };
}

export async function sendMessage(
  message: string,
  conversationId: string | null,
  file?: { name: string; type: string; base64: string },
): Promise<{ conversation_id: string; message: ChatMessage }> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const body: Record<string, unknown> = {
    message,
    conversation_id: conversationId,
    teacher_id: teacher.teacher_id,
  };

  if (file) {
    body.attachment_base64 = file.base64;
    body.attachment_name = file.name;
    body.attachment_type = file.type;
  }

  const res = await fetch(`${BASE}/api/chat/send`, {
    method: 'POST',
    headers: getAuthHeaders(teacher.teacher_id),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error('Nachricht konnte nicht gesendet werden.');
  }

  return res.json() as Promise<{ conversation_id: string; message: ChatMessage }>;
}

export async function sendMessageStream(
  message: string,
  conversationId: string | null,
  file?: { name: string; type: string; base64: string },
  onDelta: (text: string) => void,
  onMeta: (data: { conversation_id: string }) => void,
  onDone: (data: { message_id: string }) => void,
): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const body: Record<string, unknown> = {
    message,
    conversation_id: conversationId,
    teacher_id: teacher.teacher_id,
  };
  if (file) {
    body.attachment_base64 = file.base64;
    body.attachment_name = file.name;
    body.attachment_type = file.type;
  }

  const res = await fetch(`${BASE}/api/chat/send-stream`, {
    method: 'POST',
    headers: getAuthHeaders(teacher.teacher_id),
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error('Stream failed');
  
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = JSON.parse(line.slice(6));
      if (data.type === 'delta') onDelta(data.text);
      else if (data.type === 'meta') onMeta(data);
      else if (data.type === 'done') onDone(data);
    }
  }
}

export async function getHistory(conversationId: string): Promise<ChatMessage[]> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/chat/history?conversation_id=${conversationId}`, {
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });

  if (!res.ok) throw new Error('Verlauf konnte nicht geladen werden.');
  const data = (await res.json()) as { messages: ChatMessage[] };
  return data.messages;
}

export async function getConversations(): Promise<Conversation[]> {
  const teacher = getSession();
  if (!teacher) return [];

  const res = await fetch(`${BASE}/api/chat/conversations`, {
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });

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
    headers: { 'X-Teacher-ID': teacher.teacher_id },
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

  const res = await fetch(`${BASE}/api/curriculum/list?teacher_id=${teacher.teacher_id}`, {
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });
  if (!res.ok) return [];
  return res.json() as Promise<Curriculum[]>;
}

export async function deleteCurriculum(curriculumId: string): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/curriculum/${curriculumId}?teacher_id=${teacher.teacher_id}`, {
    method: 'DELETE',
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });
  if (!res.ok) throw new Error('Lehrplan konnte nicht gelöscht werden.');
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

  const res = await fetch(`${BASE}/api/profile/${teacher.teacher_id}`, {
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });

  if (!res.ok) return null;
  return res.json() as Promise<Profile>;
}

export async function updateProfile(data: Partial<Profile>): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/profile/${teacher.teacher_id}`, {
    method: 'PATCH',
    headers: getAuthHeaders(teacher.teacher_id),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Profil konnte nicht gespeichert werden.');
}

// ── Conversation Management ──
export async function deleteConversation(conversationId: string): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  await fetch(`${BASE}/api/chat/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: { 'X-Teacher-ID': teacher.teacher_id }
  });
}
