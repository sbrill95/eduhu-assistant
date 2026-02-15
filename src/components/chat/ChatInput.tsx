import { useState, useRef, type KeyboardEvent, type ChangeEvent } from 'react';
import { transcribeAudio } from '@/lib/api';
import { getSession } from '@/lib/auth';

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
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Bevorzuge Opus im WebM-Container, falle aber auf den Standard zurück
      const mimeType = ['audio/webm;codecs=opus', 'audio/webm'].find(MediaRecorder.isTypeSupported);
      if (!mimeType) {
        alert('Dein Browser unterstützt die Audioaufnahme nicht im benötigten Format.');
        return;
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      });

      mediaRecorder.addEventListener('stop', async () => {
        // Stoppe alle Tracks, um die Mikrofon-Anzeige im Browser zu deaktivieren
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());

        const teacher = getSession();
        if (!teacher) {
          alert('Fehler: Nicht angemeldet.');
          setIsRecording(false);
          return;
        }

        if (audioChunksRef.current.length === 0) {
          setIsRecording(false);
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

        setIsTranscribing(true);
        try {
          const transcribedText = await transcribeAudio(audioBlob, teacher.teacher_id);
          setText((prev) => (prev ? `${prev.trim()} ${transcribedText}` : transcribedText));
          // Manuelles Auslösen des Input-Handlers, um die Textarea-Größe anzupassen
          setTimeout(() => handleInput(), 0);
        } catch (err) {
          console.error('Fehler bei der Transkription:', err);
          alert('Die Transkription ist fehlgeschlagen.');
        } finally {
          setIsTranscribing(false);
        }
      });

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Fehler bei der Audioaufnahme:', err);
      alert('Zugriff auf das Mikrofon wurde verweigert oder es ist kein Mikrofon angeschlossen.');
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }

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
          disabled={disabled || isRecording}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xl text-text-secondary transition-colors hover:bg-bg-subtle hover:text-primary disabled:opacity-40"
          title="Datei anhängen (Bild oder PDF)"
        >
          📎
        </button>

        <button
          type="button"
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isTranscribing}
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xl transition-colors ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse'
              : 'text-text-secondary hover:bg-bg-subtle hover:text-primary'
          } disabled:opacity-40`}
          title={isRecording ? 'Aufnahme stoppen' : 'Spracheingabe'}
        >
          {isRecording ? '⏹' : '🎤'}
        </button>

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Nachricht eingeben..."
          disabled={disabled || isRecording}
          rows={1}
          className="input max-h-[160px] min-h-[40px] flex-1 resize-none py-2.5"
        />

        <button
          type="button"
          onClick={handleSend}
          disabled={(!text.trim() && !file) || disabled || isRecording}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-lg text-white transition-all hover:bg-primary-hover disabled:opacity-40 disabled:hover:bg-primary"
          title="Senden"
        >
          ⬆
        </button>
      </div>
      {isTranscribing && (
        <div className="pt-1 text-center text-xs text-text-muted">Wird transkribiert...</div>
      )}
    </div>
  );
}
