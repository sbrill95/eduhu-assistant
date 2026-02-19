import { useState } from 'react';

export type Source = {
  index: number;
  title: string;
  url?: string;
  type: 'web' | 'curriculum' | 'youtube';
};

const ICON_MAP: Record<Source['type'], string> = {
  web: '🔍',
  curriculum: '📚',
  youtube: '🎥',
};

function detectType(title: string, url?: string): Source['type'] {
  if (url && (url.includes('youtube.com') || url.includes('youtu.be'))) return 'youtube';
  if (/lehrplan|rahmenlehrplan|bildungsstandard|curriculum/i.test(title)) return 'curriculum';
  return 'web';
}

// Pattern A: [1] [Title](URL)  or  [1] **Title**: snippet ... [Title](URL)
const NUMBERED_SOURCE_RE = /^\[(\d+)\]\s+\[([^\]]+)\]\(([^)]+)\)\s*$/;
const NUMBERED_BOLD_RE = /^\[(\d+)\]\s+\*\*([^*]+)\*\*.*\[([^\]]+)\]\(([^)]+)\)\s*$/;
// Pattern B: 📖 **Quelle: Title** or 📖 Quelle: Title
const CURRICULUM_RE = /^📖\s+\*{0,2}Quelle:\s*\*{0,2}\s*(.+)$/;

export function extractSources(content: string): { cleanContent: string; sources: Source[] } {
  const lines = content.split('\n');
  const sources: Source[] = [];
  const cleanLines: string[] = [];
  let inSourceBlock = false;

  // Scan from end to find source block
  const reversedSourceLines: number[] = [];
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i]!.trim();
    if (!line) {
      if (inSourceBlock) reversedSourceLines.push(i);
      continue;
    }

    let match = line.match(NUMBERED_SOURCE_RE);
    if (match) {
      const [, idx, title, url] = match;
      sources.push({ index: parseInt(idx!), title: title!, url: url!, type: detectType(title!, url!) });
      reversedSourceLines.push(i);
      inSourceBlock = true;
      continue;
    }

    match = line.match(NUMBERED_BOLD_RE);
    if (match) {
      const [, idx, , title, url] = match;
      sources.push({ index: parseInt(idx!), title: title!, url: url!, type: detectType(title!, url!) });
      reversedSourceLines.push(i);
      inSourceBlock = true;
      continue;
    }

    const currMatch = line.match(CURRICULUM_RE);
    if (currMatch) {
      sources.push({ index: sources.length + 1, title: currMatch[1]!.trim(), type: 'curriculum' });
      reversedSourceLines.push(i);
      inSourceBlock = true;
      continue;
    }

    // Non-source line: stop scanning
    break;
  }

  if (sources.length === 0) {
    return { cleanContent: content, sources: [] };
  }

  sources.sort((a, b) => a.index - b.index);

  const sourceLineSet = new Set(reversedSourceLines);
  for (let i = 0; i < lines.length; i++) {
    if (!sourceLineSet.has(i)) {
      cleanLines.push(lines[i]!);
    }
  }

  // Trim trailing empty lines
  while (cleanLines.length > 0 && cleanLines[cleanLines.length - 1]!.trim() === '') {
    cleanLines.pop();
  }

  return { cleanContent: cleanLines.join('\n'), sources };
}

export function SourcesFooter({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState(false);

  if (!sources.length) return null;

  return (
    <div className="mt-1.5">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-default transition-colors px-1 py-0.5 rounded"
      >
        <svg
          className={`w-3 h-3 transition-transform duration-200 ${open ? 'rotate-90' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        {sources.length} {sources.length === 1 ? 'Quelle' : 'Quellen'}
      </button>

      <div
        className={`grid transition-all duration-200 ease-in-out ${
          open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <ul className="mt-1 space-y-1 px-1">
            {sources.map((s) => (
              <li key={s.index} className="flex items-start gap-1.5 text-xs text-text-muted">
                <span className="shrink-0">{ICON_MAP[s.type]}</span>
                {s.url ? (
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline truncate"
                  >
                    {s.title}
                  </a>
                ) : (
                  <span>{s.title}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
