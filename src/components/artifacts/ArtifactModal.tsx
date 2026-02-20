import { useEffect } from 'react';
import type { Artifact } from '@/lib/types';
import { ArtifactContent } from './ArtifactContent';

interface Props {
  artifact: Artifact;
  onClose: () => void;
}

export function ArtifactModal({ artifact, onClose }: Props) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-end sm:items-center justify-center" onClick={onClose}>
      <div className="bg-bg-card w-full h-[90vh] sm:h-[85vh] sm:max-w-lg sm:rounded-t-2xl rounded-t-2xl flex flex-col overflow-hidden animate-[slideUp_0.3s_ease]" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-bg-page shrink-0">
          <span className="font-semibold text-text-strong text-sm truncate">
            {artifact.title}
          </span>
          <div className="flex items-center gap-3">
            {artifact.type === 'docx' && (
              <a
                href={artifact.url}
                download
                className="text-xs font-semibold text-primary"
              >
                📥 DOCX
              </a>
            )}
            <button
              onClick={onClose}
              className="text-text-muted hover:text-text-strong text-xl leading-none"
            >
              &times;
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 bg-[#f0eded]">
          <ArtifactContent artifact={artifact} />
        </div>
      </div>
    </div>
  );
}
