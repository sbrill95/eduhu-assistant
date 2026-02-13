import type { Attachment } from '@/lib/types';

interface Props {
  attachment: Attachment;
}

const FILE_ICONS: Record<string, string> = {
  'application/pdf': '📄',
  'image/': '🖼',
  'application/vnd': '📊',
  'text/': '📝',
};

function getIcon(mimeType: string): string {
  for (const [prefix, icon] of Object.entries(FILE_ICONS)) {
    if (mimeType.startsWith(prefix)) return icon;
  }
  return '📁';
}

function formatSize(bytes?: number): string {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FilePreview({ attachment }: Props) {
  if (attachment.type === 'image') {
    return (
      <div className="mt-3">
        <img
          src={attachment.url}
          alt={attachment.name}
          className="max-h-[300px] rounded-[var(--radius-badge)] object-contain"
        />
      </div>
    );
  }

  return (
    <div className="mt-3 flex items-center gap-3 rounded-[var(--radius-badge)] bg-bg-subtle p-3">
      <span className="text-2xl">{getIcon(attachment.mimeType)}</span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-text-strong">{attachment.name}</p>
        <p className="text-xs text-text-muted">
          {formatSize(attachment.size)}
          {attachment.mimeType.split('/')[1]?.toUpperCase()}
        </p>
      </div>
      <a
        href={attachment.url}
        download={attachment.name}
        className="btn-ghost rounded-[var(--radius-badge)] px-3 py-1.5 text-xs"
      >
        ⬇️ Download
      </a>
    </div>
  );
}
