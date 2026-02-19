import type { Artifact } from '@/lib/types';
import { DocxPreview } from './DocxPreview';
import { H5PPlayer } from '@/components/exercises/H5PPlayer';

interface Props {
  artifact: Artifact;
  onClose: () => void;
}

export function ArtifactModal({ artifact, onClose }: Props) {
  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-end sm:items-center justify-center">
      <div className="bg-bg-card w-full h-[90vh] sm:h-[85vh] sm:max-w-lg sm:rounded-t-2xl rounded-t-2xl flex flex-col overflow-hidden animate-[slideUp_0.3s_ease]">
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
          {artifact.type === 'docx' && <DocxPreview url={artifact.url} />}
          {artifact.type === 'h5p' && <H5PPlayer exerciseId={artifact.id} />}
          {artifact.type === 'audio' && (
            <div className="flex items-center justify-center h-full">
              <audio controls src={artifact.url} className="w-full max-w-md" />
            </div>
          )}
          {artifact.type === 'image' && (
            <div className="flex items-center justify-center">
              <img
                src={artifact.url}
                alt={artifact.title}
                className="max-w-full rounded-lg"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
