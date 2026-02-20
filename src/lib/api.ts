import { type ChatMessage, type Conversation } from './types';
import { getSession, clearSession } from './auth';
import { log } from './logger';

export const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';
const BASE = API_BASE;

function getAuthHeaders(withContentType = true): Record<string, string> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');
  const headers: Record<string, string> = {
    Authorization: `Bearer ${teacher.access_token}`,
  };
  if (withContentType) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

/** Handle 401 responses by clearing session — caller should redirect to login */
function handle401(res: Response): boolean {
  if (res.status === 401) {
    clearSession();
    window.location.href = '/';
    return true;
  }
  return false;
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
    headers: getAuthHeaders(),
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
  file: { name: string; type: string; base64: string } | undefined,
  onDelta: (text: string) => void,
  onMeta: (data: { conversation_id: string }) => void,
  onDone: (data: { message_id: string; sources?: Array<{ index: number; title: string; url?: string }> }) => void,
  onStep?: (text: string) => void,
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

  log.info('stream', 'fetch start', { conversationId, messageLength: message.length, hasFile: !!file });
  log.time('stream:fetch');

  const res = await fetch(`${BASE}/api/chat/send-stream`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(body),
  });

  log.timeEnd('stream:fetch');

  if (!res.ok) {
    log.error('stream', 'fetch failed', { status: res.status, statusText: res.statusText });
    throw new Error('Stream failed');
  }

  log.info('stream', 'response received, reading stream…', { status: res.status });
  log.time('stream:firstChunk');

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let chunkCount = 0;
  let firstChunkLogged = false;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    chunkCount++;
    if (!firstChunkLogged) {
      log.timeEnd('stream:firstChunk');
      firstChunkLogged = true;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      try {
        const data = JSON.parse(line.slice(6));
        log.debug('stream', `event: ${data.type}`, data.type === 'delta' ? { len: data.text?.length } : data);
        if (data.type === 'delta') onDelta(data.text);
        else if (data.type === 'meta') onMeta(data);
        else if (data.type === 'done') onDone(data);
        else if (data.type === 'step' && onStep) onStep(data.text);
      } catch (e) {
        log.warn('stream', 'failed to parse SSE line', { line, error: e });
      }
    }
  }

  log.info('stream', 'stream complete', { totalChunks: chunkCount });
}

export async function getHistory(conversationId: string): Promise<ChatMessage[]> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/chat/history?conversation_id=${conversationId}`, {
    headers: { Authorization: `Bearer ${teacher.access_token}` }
  });

  if (!res.ok) {
    handle401(res);
    throw new Error('Verlauf konnte nicht geladen werden.');
  }
  const data = (await res.json()) as { messages: ChatMessage[] };
  return data.messages;
}

export async function getConversations(): Promise<Conversation[]> {
  const teacher = getSession();
  if (!teacher) return [];

  const res = await fetch(`${BASE}/api/chat/conversations`, {
    headers: { Authorization: `Bearer ${teacher.access_token}` }
  });

  if (!res.ok) {
    handle401(res);
    return [];
  }
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
    headers: { Authorization: `Bearer ${teacher.access_token}` },
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

  const res = await fetch(`${BASE}/api/curriculum/list`, {
    headers: { Authorization: `Bearer ${teacher.access_token}` }
  });
  if (!res.ok) return [];
  return res.json() as Promise<Curriculum[]>;
}

export async function deleteCurriculum(curriculumId: string): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/curriculum/${curriculumId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${teacher.access_token}`, 'Content-Type': 'application/json' }
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
  onboarding_completed?: boolean;
}

export async function getProfile(): Promise<Profile | null> {
  const teacher = getSession();
  if (!teacher) return null;

  const res = await fetch(`${BASE}/api/profile/${teacher.teacher_id}`, {
    headers: { Authorization: `Bearer ${teacher.access_token}` }
  });

  if (!res.ok) {
    handle401(res);
    return null;
  }
  return res.json() as Promise<Profile>;
}

export async function updateProfile(data: Partial<Profile>): Promise<void> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');

  const res = await fetch(`${BASE}/api/profile/${teacher.teacher_id}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
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
    headers: { Authorization: `Bearer ${teacher.access_token}` }
  });
}

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');
  const form = new FormData();
  form.append('file', audioBlob, 'recording.webm');
  const resp = await fetch(`${API_BASE}/api/transcribe`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${teacher.access_token}` },
    body: form,
  });
  if (!resp.ok) throw new Error('Transcription failed');
  const data = await resp.json();
  return data.text || '';
}

export interface TokenUsageDaily {
  date: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  calls: number;
  cost_usd: number;
}
export interface TokenUsageSummary {
  daily: TokenUsageDaily[];
  total: {
    input_tokens: number;
    output_tokens: number;
    calls: number;
    cost_usd: number;
  };
}
export async function getTokenUsage(days: number = 7): Promise<TokenUsageSummary> {
  const teacher = getSession();
  if (!teacher) throw new Error('Nicht angemeldet');
  const res = await fetch(`${BASE}/api/profile/token-usage?days=${days}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Token-Usage konnte nicht geladen werden.');
  return res.json();
}
