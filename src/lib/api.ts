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
