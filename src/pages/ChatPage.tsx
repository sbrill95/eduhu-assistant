import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ChipSelector } from '@/components/chat/ChipSelector';
import { ConversationSidebar } from '@/components/chat/ConversationSidebar';
import { useChat } from '@/hooks/useChat';

export default function ChatPage() {
  const navigate = useNavigate();
  const {
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
  } = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  function handleChipSelect(label: string) {
    void send(label);
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
            onNewChat={resetChat}
            open={true}
            onClose={() => { }}
          />
        </div>

        {/* Mobile sidebar */}
        {sidebarOpen && (
          <div className="fixed inset-0 z-50 sm:hidden">
            <div className="absolute inset-0 bg-black/30" onClick={() => setSidebarOpen(false)} />
            <div className="relative h-full w-72">
              <ConversationSidebar
                currentId={conversationId}
                onSelect={(id) => { void loadConversation(id); setSidebarOpen(false); }}
                onNewChat={() => { resetChat(); setSidebarOpen(false); }}
                open={true}
                onClose={() => setSidebarOpen(false)}
              />
            </div>
          </div>
        )}

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

              {showWelcomeChips && (
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

              {isTyping && !messages.some(m => m.id.startsWith('stream-')) && <TypingIndicator context={messages.filter(m => m.role === 'user').slice(-1)[0]?.content} />}
            </div>
          </div>

          {/* Input */}
          <div className="mx-auto w-full max-w-3xl">
            <ChatInput onSend={(t, f) => void send(t, f)} disabled={isTyping} />
          </div>
        </div>
      </div>
    </AppShell>
  );
}
