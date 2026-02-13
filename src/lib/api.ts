import type { ChatMessage, Conversation } from './types';

const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

export async function sendMessage(
  message: string,
  conversationId: string | null,
): Promise<{ conversation_id: string; message: ChatMessage }> {
  const res = await fetch(`${BASE}/api/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

  if (!res.ok) {
    throw new Error('Nachricht konnte nicht gesendet werden.');
  }

  return res.json() as Promise<{ conversation_id: string; message: ChatMessage }>;
}

export async function getHistory(conversationId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${BASE}/api/chat/history?conversation_id=${conversationId}`);
  if (!res.ok) throw new Error('Verlauf konnte nicht geladen werden.');
  const data = await res.json() as { messages: ChatMessage[] };
  return data.messages;
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await fetch(`${BASE}/api/chat/conversations`);
  if (!res.ok) return [];
  return res.json() as Promise<Conversation[]>;
}
