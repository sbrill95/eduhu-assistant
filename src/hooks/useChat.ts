import { useState, useCallback, useEffect } from 'react';
import { getSession } from '../lib/auth';
import { sendMessage, getHistory, API_BASE } from '../lib/api';
import type { ChatMessage } from '../lib/types';

export function useChat() {
  const teacher = getSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcomeChips, setShowWelcomeChips] = useState(true);

  // Load suggestions on mount
  useEffect(() => {
    if (!teacher) return;
    
    fetch(`${API_BASE}/api/suggestions?teacher_id=${teacher.teacher_id}`)
      .then(res => res.json())
      .then(data => setSuggestions(data.suggestions))
      .catch(() => setSuggestions(["Plane eine Unterrichtsstunde", "Erstelle Material", "Hilf mir bei der Vorbereitung"]))
      .finally(() => setLoadingSuggestions(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Show welcome chips when no messages exist
  useEffect(() => {
    if (teacher && messages.length === 0 && !conversationId) {
      setShowWelcomeChips(true);
    }
  }, [teacher, messages.length, conversationId]);

  const loadConversation = useCallback(async (convId: string) => {
    setConversationId(convId);
    setShowWelcomeChips(false);
    try {
      const history = await getHistory(convId);
      // Map history to ensure valid timestamp format if needed
      setMessages(history.map((m) => ({
        ...m,
        timestamp: m.timestamp || new Date().toISOString(),
      })));
    } catch {
      setMessages([{
        id: 'error',
        role: 'assistant',
        content: 'Gespräch konnte nicht geladen werden.',
        timestamp: new Date().toISOString(),
      }]);
    }
  }, []);

  const resetChat = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setShowWelcomeChips(true);
  }, []);

  const send = useCallback(async (text: string) => {
    if (!teacher) return;
    
    setShowWelcomeChips(false);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await sendMessage(text, conversationId);
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.message]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Da ist etwas schiefgelaufen. Versuch\'s nochmal. 🦉',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }, [conversationId, teacher]);

  return {
    messages,
    suggestions,
    loadingSuggestions,
    conversationId,
    isTyping,
    showWelcomeChips,
    loadConversation,
    resetChat,
    send,
    teacher,
  };
}
