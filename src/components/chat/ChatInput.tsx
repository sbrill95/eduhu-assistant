import { useState, useRef, type KeyboardEvent } from 'react';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="flex items-end gap-2 border-t border-border bg-bg-card px-4 py-3">
      {/* Attachment button - placeholder for now */}
      <button
        type="button"
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xl text-text-secondary transition-colors hover:bg-bg-subtle hover:text-primary"
        title="Datei anhängen"
      >
        📎
      </button>

      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder="Nachricht eingeben..."
        disabled={disabled}
        rows={1}
        className="input max-h-[160px] min-h-[40px] flex-1 resize-none py-2.5"
      />

      <button
        type="button"
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-lg text-white transition-all hover:bg-primary-hover disabled:opacity-40 disabled:hover:bg-primary"
        title="Senden"
      >
        ⬆
      </button>
    </div>
  );
}
