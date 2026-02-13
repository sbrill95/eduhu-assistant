import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { sendMessage } from '@/lib/api';
import { AppShell } from '@/components/layout/AppShell';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ChipSelector } from '@/components/chat/ChipSelector';
import type { ChatMessage as MessageType, Chip } from '@/lib/types';

const WELCOME_CHIPS: Chip[] = [
  { id: '1', label: 'Quiz erstellen', icon: '📝' },
  { id: '2', label: 'Dokumentation', icon: '📋' },
  { id: '3', label: 'Stunde zusammenfassen', icon: '📖' },
  { id: '4', label: 'Ideen für Unterricht', icon: '💡' },
];

export default function ChatPage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcomeChips, setShowWelcomeChips] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Welcome message
  useEffect(() => {
    if (teacher && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: `Hallo ${teacher.name}! 👋\n\nWas kann ich heute für dich tun?`,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [teacher]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSend = useCallback(async (text: string) => {
    setShowWelcomeChips(false);

    // Add user message
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
      <div className="flex h-full flex-col">
        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-4 py-4"
        >
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                onChipSelect={handleChipSelect}
              />
            ))}

            {/* Welcome chips */}
            {showWelcomeChips && messages.length > 0 && (
              <div className="ml-11">
                <ChipSelector
                  chips={WELCOME_CHIPS}
                  onSelect={(chip) => handleChipSelect(chip.label)}
                />
              </div>
            )}

            {/* Typing indicator */}
            {isTyping && <TypingIndicator />}
          </div>
        </div>

        {/* Input */}
        <div className="mx-auto w-full max-w-3xl">
          <ChatInput onSend={(t) => void handleSend(t)} disabled={isTyping} />
        </div>
      </div>
    </AppShell>
  );
}
