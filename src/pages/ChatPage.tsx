import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { sendMessage, getHistory } from '@/lib/api';
import { AppShell } from '@/components/layout/AppShell';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ChipSelector } from '@/components/chat/ChipSelector';
import { ConversationSidebar } from '@/components/chat/ConversationSidebar';
import type { ChatMessage as MessageType } from '@/lib/types';
import { API_BASE } from '@/lib/api';

export default function ChatPage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcomeChips, setShowWelcomeChips] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  useEffect(() => {
    const teacher = getSession();
    if (!teacher) return;
    fetch(`${API_BASE}/api/suggestions?teacher_id=${teacher.teacher_id}`)
      .then(res => res.json())
      .then(data => setSuggestions(data.suggestions))
      .catch(() => setSuggestions(["Plane eine Unterrichtsstunde", "Erstelle Material", "Hilf mir bei der Vorbereitung"]))
      .finally(() => setLoadingSuggestions(false));
  }, []);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Show welcome chips when no messages exist
  useEffect(() => {
    if (teacher && messages.length === 0 && !conversationId) {
      setShowWelcomeChips(true);
    }
  }, [teacher, messages.length, conversationId]);

  // Load existing conversation
  const loadConversation = useCallback(async (convId: string) => {
    setConversationId(convId);
    setShowWelcomeChips(false);
    try {
      const history = await getHistory(convId);
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

  // New chat
  const handleNewChat = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setShowWelcomeChips(true);
  }, []);

  const handleSend = useCallback(async (text: string) => {
    setShowWelcomeChips(false);

    const userMsg: MessageType = {
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
  }, [conversationId]);

  function handleChipSelect(label: string) {
    void handleSend(label);
  }

  if (!teacher) return null;

  return (
    <AppShell>
      <div className="flex h-full">
        {/* Sidebar */}
        <div className="hidden sm:block">
          <ConversationSidebar
            currentId={conversationId}
            onSelect={(id) => void loadConversation(id)}
            onNewChat={handleNewChat}
            open={true}
            onClose={() => {}}
          />
        </div>

        {/* Mobile sidebar */}
        <ConversationSidebar
          currentId={conversationId}
          onSelect={(id) => void loadConversation(id)}
          onNewChat={handleNewChat}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Chat area */}
        <div className="flex flex-1 flex-col">
          {/* Mobile sidebar toggle */}
          <div className="flex h-10 items-center border-b border-border px-3 sm:hidden">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="text-sm text-text-secondary"
            >
              ☰ Gespräche
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4">
            <div className="mx-auto max-w-3xl space-y-4">
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  onChipSelect={handleChipSelect}
                />
              ))}

              {showWelcomeChips && messages.length === 0 && !conversationId && (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="text-6xl mb-6">🦉</div>
                  <h1 className="text-2xl font-semibold mb-2">
                    Hallo {teacher?.name}! 👋
                  </h1>
                  <p className="text-text-secondary mb-8">
                    Womit kann ich dir heute helfen?
                  </p>
                  {loadingSuggestions ? (
                    <div className="flex space-x-2">
                      <div className="h-8 w-32 animate-pulse rounded-full bg-surface-secondary" />
                      <div className="h-8 w-40 animate-pulse rounded-full bg-surface-secondary" />
                      <div className="h-8 w-36 animate-pulse rounded-full bg-surface-secondary" />
                    </div>
                  ) : (
                    <ChipSelector
                      chips={suggestions.map((s: string, i: number) => ({ id: `s-${i}`, label: s }))}
                      onSelect={(chip) => handleChipSelect(chip.label)}
                    />
                  )}
                </div>
              )}

              {isTyping && <TypingIndicator />}
            </div>
          </div>

          {/* Input */}
          <div className="mx-auto w-full max-w-3xl">
            <ChatInput onSend={(t) => void handleSend(t)} disabled={isTyping} />
          </div>
        </div>
      </div>
    </AppShell>
  );
}
