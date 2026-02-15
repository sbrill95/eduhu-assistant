import { useState, useRef, type KeyboardEvent, type ChangeEvent } from 'react';

export interface FileAttachment {
  name: string;
  type: string;
  base64: string;
  size: number;
}

interface Props {
  onSend: (text: string, file?: FileAttachment) => void;
  disabled?: boolean;
}

const MAX_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState('');
  const [file, setFile] = useState<FileAttachment | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSend() {
    const trimmed = text.trim();
    if ((!trimmed && !file) || disabled) return;
    onSend(trimmed || (file ? `[Datei: ${file.name}]` : ''), file ?? undefined);
    setText('');
    setFile(null);
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

  function handleFileSelect(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!ALLOWED_TYPES.includes(f.type)) {
      alert('Nur Bilder (JPG, PNG, WebP) und PDFs sind erlaubt.');
      return;
    }
    if (f.size > MAX_SIZE) {
      alert('Datei ist zu groß (max. 10 MB).');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Strip data URL prefix to get pure base64
      const base64 = result.includes(',') ? result.split(',')[1] : result;
      setFile({ name: f.name, type: f.type, base64, size: f.size });
    };
    reader.readAsDataURL(f);
    // Reset input so same file can be selected again
    e.target.value = '';
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="border-t border-border bg-bg-card px-4 py-3">
      {/* File Preview */}
      {file && (
        <div className="mb-2 flex items-center gap-3 rounded-lg bg-bg-subtle px-3 py-2">
          <span className="text-xl">{file.type.startsWith('image/') ? '🖼️' : '📄'}</span>
          <div className="flex-1 min-w-0">
            <p className="truncate text-sm font-medium text-text-strong">{file.name}</p>
            <p className="text-xs text-text-muted">{formatSize(file.size)}</p>
          </div>
          <button
            onClick={() => setFile(null)}
            className="text-text-muted hover:text-red-500 transition-colors text-lg"
            title="Entfernen"
          >
            ✕
          </button>
        </div>
      )}

      <div className="flex items-end gap-2">
        {/* File Input (hidden) */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,application/pdf"
          onChange={handleFileSelect}
          className="hidden"
        />

        {/* Attachment button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xl text-text-secondary transition-colors hover:bg-bg-subtle hover:text-primary disabled:opacity-40"
          title="Datei anhängen (Bild oder PDF)"
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
          disabled={(!text.trim() && !file) || disabled}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-lg text-white transition-all hover:bg-primary-hover disabled:opacity-40 disabled:hover:bg-primary"
          title="Senden"
        >
          ⬆
        </button>
      </div>
    </div>
  );
}
