import type { Artifact } from '@/lib/types';
import { ArtifactContent } from './ArtifactContent';

interface Props {
  artifacts: Artifact[];
  activeIndex: number;
  onSetActive: (index: number) => void;
  onClose: (index: number) => void;
  onCloseAll: () => void;
}

export function ArtifactPanel({
  artifacts,
  activeIndex,
  onSetActive,
  onClose,
  onCloseAll,
}: Props) {
  if (artifacts.length === 0) return null;
  const active = artifacts[activeIndex] ?? artifacts[0];
  if (!active) return null;
  return (
    <div className="flex flex-col h-full rounded-[var(--radius-card)] bg-bg-card shadow-soft overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-bg-page shrink-0">
        <span className="font-semibold text-text-strong text-sm truncate">
          {active.title}
        </span>
        <div className="flex items-center gap-2">
          {active.type === 'docx' && (
            <a
              href={active.url}
              download
              className="text-xs font-semibold text-primary hover:underline"
            >
              {' '}
              📥 DOCX{' '}
            </a>
          )}
          {artifacts.length > 1 && (
            <button onClick={onCloseAll} className="text-xs text-text-muted hover:text-text-strong">
              Alle schließen
            </button>
          )}
          <button
            onClick={() => onClose(activeIndex)}
            className="text-text-muted hover:text-text-strong text-lg leading-none"
          >
            &times;
          </button>
        </div>
      </div>

      {/* Tabs (if multiple) */}
      {artifacts.length > 1 && (
        <div
          className="flex gap-1 px-3 py-2 overflow-x-auto border-b border-bg-page shrink-0"
          style={{ scrollbarWidth: 'none' }}
        >
          {artifacts.map((art, i) => (
            <button
              key={art.id}
              onClick={() => onSetActive(i)}
              className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                i === activeIndex
                  ? 'bg-primary text-white'
                  : 'bg-bg-subtle text-text-secondary hover:bg-bg-page'
              }`}
            >
              {art.type === 'docx'
                ? '📄'
                : art.type === 'h5p'
                ? '🎯'
                : art.type === 'audio'
                ? '🔊'
                : '🖼️'}{' '}
              {art.title.slice(0, 25)}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-[#f0eded]">
        <ArtifactContent artifact={active} />
      </div>
    </div>
  );
}
