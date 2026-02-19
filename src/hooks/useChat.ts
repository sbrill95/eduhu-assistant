import { useState, useCallback, useEffect } from 'react';
import { getSession } from '../lib/auth';
import { sendMessage, getHistory, API_BASE, sendMessageStream } from '../lib/api';
import type { ChatMessage } from '../lib/types';
import { log } from '../lib/logger';

export function useChat() {
  const teacher = getSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [streamingStep, setStreamingStep] = useState<string | null>(null);
  const [showWelcomeChips, setShowWelcomeChips] = useState(true);

  // Load suggestions on mount
  useEffect(() => {
    if (!teacher) return;
    
    fetch(`${API_BASE}/api/suggestions?teacher_id=${teacher.teacher_id}`, {
      headers: { Authorization: `Bearer ${teacher.access_token}` },
    })
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

  const send = useCallback(async (text: string, file?: { name: string; type: string; base64: string }) => {
    if (!teacher) return;
    
    setShowWelcomeChips(false);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: file ? `${text}\n📎 ${file.name}` : text,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    const streamMsgId = `stream-${Date.now()}`;
    log.info('chat', 'send started', { streamMsgId, conversationId, textLength: text.length, hasFile: !!file });
    log.time('chat:roundtrip');

    // Add empty assistant message that will be filled
    setMessages(prev => [...prev, { id: streamMsgId, role: 'assistant', content: '', timestamp: new Date().toISOString() }]);

    try {
      let hasContent = false;
      let deltaCount = 0;
      await sendMessageStream(
        text, conversationId, file,
        // onDelta
        (delta) => {
          deltaCount++;
          if (!hasContent) {
            log.info('chat', 'first content delta received', { deltaCount });
          }
          hasContent = true;
          setMessages(prev => prev.map(m => {
            if (m.id !== streamMsgId) return m;
            // Strip step prefix once real content arrives
            const cleanContent = m.content.startsWith('⏳') ? '' : m.content;
            return { ...m, content: cleanContent + delta };
          }));
        },
        // onMeta
        (meta) => {
          log.info('chat', 'meta received', { conversation_id: meta.conversation_id });
          setConversationId(meta.conversation_id);
        },
        // onDone
        (done) => {
          log.info('chat', 'done received', { message_id: done.message_id, totalDeltas: deltaCount });
          log.timeEnd('chat:roundtrip');
          setStreamingStep(null);
          setMessages(prev => prev.map(m =>
            m.id === streamMsgId ? { ...m, id: done.message_id || streamMsgId } : m
          ));
        },
        // onStep
        (stepText) => {
          log.info('chat', 'step received', { stepText, hasContent });
          setStreamingStep(stepText);
          if (!hasContent) {
            setMessages(prev => prev.map(m =>
              m.id === streamMsgId ? { ...m, content: `⏳ ${stepText}` } : m
            ));
          }
        },
      );
    } catch (err) {
      log.warn('chat', 'stream failed, falling back to non-streaming', { error: err });
      // Fallback to non-streaming
      setMessages(prev => prev.filter(m => m.id !== streamMsgId));
      try {
        log.time('chat:fallback');
        const response = await sendMessage(text, conversationId, file);
        log.timeEnd('chat:fallback');
        log.info('chat', 'fallback succeeded', { conversation_id: response.conversation_id });
        setConversationId(response.conversation_id);
        setMessages((prev) => [...prev, response.message]);
      } catch (fallbackErr) {
        log.error('chat', 'fallback also failed', { error: fallbackErr });
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content: 'Da ist etwas schiefgelaufen. Versuch\'s nochmal. 🦉',
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } finally {
      log.info('chat', 'send complete, re-enabling input');
      setStreamingStep(null);
      setIsTyping(false);
    }
  }, [conversationId, teacher]);

  return {
    messages,
    suggestions,
    loadingSuggestions,
    conversationId,
    isTyping,
    streamingStep,
    showWelcomeChips,
    loadConversation,
    resetChat,
    send,
    teacher,
  };
}
