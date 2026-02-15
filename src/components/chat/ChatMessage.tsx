import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { ChipSelector } from './ChipSelector';
import { FilePreview } from './FilePreview';
import { CountdownTimer } from './CountdownTimer';
import { QRCard } from './QRCard';
import { TodoCard } from './TodoCard';

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
            <div className="prose prose-sm max-w-none text-text-default prose-headings:text-text-strong prose-strong:text-text-strong prose-a:text-primary">
              <ReactMarkdown
                components={{
                  pre({ children }: any) {
                    // Unwrap <pre> if it contains a custom card component instead of code
                    const child = Array.isArray(children) ? children[0] : children;
                    if (child?.type && typeof child.type !== 'string') {
                      // It's a React component (TodoCard/QRCard), not a DOM element
                      return <>{children}</>;
                    }
                    return <pre className="overflow-auto rounded-lg bg-[#F5F0EB] p-3">{children}</pre>;
                  },
                  code({ node, inline, className, children, ...props }: any) {
                    const match = /language-([\w-]+)/.exec(className || '');
                    const language = match ? match[1] : '';

                    if (language === 'todo-card') {
                      try {
                        const todos = JSON.parse(String(children));
                        return <TodoCard todos={todos} />;
                      } catch {
                        return <code {...props}>{children}</code>;
                      }
                    }
                    if (language === 'qr-card') {
                      try {
                        const data = JSON.parse(String(children));
                        return <QRCard {...data} />;
                      } catch {
                        return <code {...props}>{children}</code>;
                      }
                    }
                    
                    if (!inline && language) {
                      return (
                        <SyntaxHighlighter
                          style={oneLight}
                          language={language}
                          PreTag="div"
                          className="rounded-lg overflow-auto text-sm"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      );
                    }
                    
                    return (
                      <code
                        className="bg-bg-subtle rounded px-1 py-0.5 text-sm"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content.startsWith('⏳') ? '' : message.content.replace(/\{\{TIMER:\d+:[^}]*\}\}/g, '')}
              </ReactMarkdown>
              {message.content.startsWith('⏳') && (
                <p className="text-sm text-text-muted animate-pulse">{message.content}</p>
              )}
              {(() => {
                const timerMatch = message.content.match(/\{\{TIMER:(\d+):([^}]*)\}\}/);
                if (timerMatch) {
                  return <CountdownTimer seconds={parseInt(timerMatch[1] ?? '0')} label={timerMatch[2] ?? ''} />;
                }
                return null;
              })()}
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
