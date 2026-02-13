import ReactMarkdown from 'react-markdown';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { ChipSelector } from './ChipSelector';
import { FilePreview } from './FilePreview';

interface Props {
  message: ChatMessageType;
  onChipSelect?: (label: string) => void;
}

export function ChatMessage({ message, onChipSelect }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-lg">
          🦉
        </div>
      )}

      {/* Bubble */}
      <div className={`max-w-[80%] sm:max-w-[70%] ${isUser ? 'ml-auto' : ''}`}>
        <div
          className={`rounded-[var(--radius-card)] px-4 py-3 ${
            isUser
              ? 'bg-primary text-white'
              : 'bg-bg-card shadow-card'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none text-text-default">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}

          {/* Attachments */}
          {message.attachments?.map((att, i) => (
            <FilePreview key={i} attachment={att} />
          ))}
        </div>

        {/* Chips */}
        {message.chips && message.chips.length > 0 && onChipSelect && (
          <div className="mt-2">
            <ChipSelector chips={message.chips} onSelect={(c) => onChipSelect(c.label)} />
          </div>
        )}

        {/* Timestamp */}
        <p className={`mt-1 text-xs text-text-muted ${isUser ? 'text-right' : ''}`}>
          {new Date(message.timestamp).toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}
