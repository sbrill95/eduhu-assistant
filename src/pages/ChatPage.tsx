import { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ChipSelector } from '@/components/chat/ChipSelector';
import { useChat } from '@/hooks/useChat';
import { OnboardingModal } from '@/components/OnboardingModal';
import { ArtifactPanel } from '@/components/artifacts/ArtifactPanel';
import { ArtifactModal } from '@/components/artifacts/ArtifactModal';
import type { Artifact } from '@/lib/types';

export default function ChatPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const {
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
    artifacts,
    activeArtifactIndex,
    setActiveArtifactIndex,
    closeArtifact,
    closeAllArtifacts,
  } = useChat();

  const [showOnboarding, setShowOnboarding] = useState(false);
  // TODO: Auto-open on mobile when artifact detected (needs screen width check)
  const [mobileArtifact, setMobileArtifact] = useState<Artifact | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  // Load conversation from URL param
  useEffect(() => {
    const convId = searchParams.get('c');
    if (convId) {
      void loadConversation(convId);
    }
  }, [searchParams, loadConversation]);

  // Handle pre-filled message from dashboard
  useEffect(() => {
    const msg = searchParams.get('msg');
    if (msg && teacher) {
      void send(msg);
      // Clear the URL param
      void navigate('/workspace', { replace: true });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Check if onboarding needed
  useEffect(() => {
    if (!teacher) return;
    const onboarded = localStorage.getItem(`eduhu_onboarded_${teacher.teacher_id}`);
    if (!onboarded) {
      setShowOnboarding(true);
    }
  }, [teacher]);

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

  const hasArtifacts = artifacts.length > 0;

  return (
    <AppShell>
      {showOnboarding && (
        <OnboardingModal
          teacherId={teacher.teacher_id}
          onComplete={() => {
            setShowOnboarding(false);
            localStorage.setItem(`eduhu_onboarded_${teacher.teacher_id}`, '1');
          }}
        />
      )}
      <div className="flex gap-5 h-full transition-all duration-300">
        {/* Chat Widget */}
        <div
          className={`flex flex-col rounded-[var(--radius-card)] bg-bg-card shadow-soft overflow-hidden transition-all duration-400 ${
            hasArtifacts
              ? 'lg:w-[calc(100%-500px)] w-full'
              : 'w-full max-w-[1000px] mx-auto shadow-modal'
          }`}
          style={!hasArtifacts ? { height: '90%' } : { height: '100%' }}
        >
          {/* Chat Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-bg-page">
            <div className="font-bold text-text-strong">
              <i className="fa-solid fa-sparkles text-primary mr-1" /> Assistent
            </div>
            {conversationId && (
              <button
                type="button"
                onClick={resetChat}
                className="text-xs font-semibold text-text-secondary hover:text-primary transition-colors"
              >
                + Neuer Chat
              </button>
            )}
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4">
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  onChipSelect={handleChipSelect}
                  isStreaming={isTyping && idx === messages.length - 1 && msg.id.startsWith('stream-')}
                />
              ))}

              {showWelcomeChips && (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="mb-6">
                    <img src="/Eduhu_Eule_Kopf.svg" alt="eduhu" className="h-12 w-12" />
                  </div>
                  <h2 className="text-2xl font-semibold mb-2">
                    Womit kann ich dir helfen?
                  </h2>
                  <p className="text-text-secondary mb-8">
                    Frag mich etwas oder wähle einen Vorschlag.
                  </p>
                  {loadingSuggestions ? (
                    <div className="flex space-x-2">
                      <div className="h-8 w-32 animate-pulse rounded-full bg-bg-subtle" />
                      <div className="h-8 w-40 animate-pulse rounded-full bg-bg-subtle" />
                      <div className="h-8 w-36 animate-pulse rounded-full bg-bg-subtle" />
                    </div>
                  ) : (
                    <ChipSelector
                      chips={suggestions.map((s: string, i: number) => ({ id: `s-${i}`, label: s }))}
                      onSelect={(chip) => handleChipSelect(chip.label)}
                    />
                  )}
                </div>
              )}

              {isTyping && !messages.some(m => m.id.startsWith('stream-')) && (
                <TypingIndicator context={messages.filter(m => m.role === 'user').slice(-1)[0]?.content} />
              )}

              {isTyping && streamingStep && messages.some(m => m.id.startsWith('stream-') && m.content && !m.content.startsWith('⏳')) && (
                <div className="flex items-center gap-2 pl-11 py-1 text-sm text-text-secondary">
                  <span
                    className="inline-block h-2 w-2 rounded-full bg-primary"
                    style={{ animation: 'pulse-dot 1.2s ease-in-out infinite' }}
                  />
                  <span>{streamingStep}</span>
                </div>
              )}
            </div>
          </div>

          {/* Suggestion Chips */}
          {!showWelcomeChips && suggestions.length > 0 && messages.length > 0 && (
            <div className="flex gap-2.5 px-5 pb-2.5 overflow-x-auto shrink-0" style={{ scrollbarWidth: 'none' }}>
              {suggestions.slice(0, 3).map((sug, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleChipSelect(sug)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all hover:-translate-y-0.5 ${
                    i === 0
                      ? 'bg-primary-soft text-primary'
                      : 'bg-blue-bg text-blue-accent'
                  }`}
                >
                  {sug}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <ChatInput onSend={(t, f) => void send(t, f)} disabled={isTyping} />
        </div>

        {/* Artifact Panel — Desktop only */}
        {hasArtifacts && (
          <div className="hidden lg:flex w-[480px] shrink-0">
            <ArtifactPanel
              artifacts={artifacts}
              activeIndex={activeArtifactIndex}
              onSetActive={setActiveArtifactIndex}
              onClose={closeArtifact}
              onCloseAll={closeAllArtifacts}
            />
          </div>
        )}
      </div>

      {/* Artifact Modal — Mobile only */}
      {mobileArtifact && (
        <div className="lg:hidden">
          <ArtifactModal artifact={mobileArtifact} onClose={() => setMobileArtifact(null)} />
        </div>
      )}
    </AppShell>
  );
}
