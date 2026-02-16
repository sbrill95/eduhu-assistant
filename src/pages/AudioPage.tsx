import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

const API = import.meta.env.VITE_API_URL || '';

interface AudioPageData {
  id: string;
  title: string;
  audio_type: string;
  audio_ids: string[];
  script: any;
}

export default function AudioPage() {
  const { code } = useParams<{ code: string }>();
  const [page, setPage] = useState<AudioPageData | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!code) return;
    fetch(`${API}/api/public/audio/pages/${code}`)
      .then((r) => {
        if (!r.ok) throw new Error('Nicht gefunden');
        return r.json();
      })
      .then(setPage)
      .catch(() => setError('Audio-Seite nicht gefunden. Prüfe den Zugangscode.'))
      .finally(() => setLoading(false));
  }, [code]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-main">
        <div className="animate-pulse text-text-muted">Lade Audio...</div>
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-main">
        <div className="rounded-xl bg-white p-8 shadow-card text-center max-w-md">
          <div className="text-4xl mb-4">🔇</div>
          <h1 className="text-xl font-semibold text-text-strong mb-2">Nicht gefunden</h1>
          <p className="text-text-muted">{error}</p>
        </div>
      </div>
    );
  }

  const typeLabels: Record<string, string> = {
    tts: '🔊 Vorgelesener Text',
    podcast: '🎙️ Podcast',
    gespraechssimulation: '💬 Gesprächssimulation',
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-main p-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-card">
        <div className="text-center mb-6">
          <div className="text-3xl mb-2">🦉</div>
          <h1 className="text-xl font-semibold text-text-strong">{page.title}</h1>
          <p className="text-sm text-text-muted mt-1">
            {typeLabels[page.audio_type] || page.audio_type}
          </p>
        </div>

        <div className="space-y-4">
          {page.audio_ids.map((audioId, i) => (
            <div key={audioId} className="rounded-lg border border-gray-200 p-3">
              {page.audio_ids.length > 1 && (
                <div className="text-xs text-text-muted mb-2">Teil {i + 1}</div>
              )}
              <audio
                src={`${API}/api/audio/${audioId}`}
                controls
                className="w-full"
              />
            </div>
          ))}
        </div>

        {page.script && page.audio_type === 'gespraechssimulation' && (
          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-primary hover:underline">
              📜 Skript anzeigen
            </summary>
            <div className="mt-2 space-y-2 text-sm">
              {Array.isArray(page.script) && page.script.map((entry: any, i: number) => (
                <div key={i} className="rounded bg-bg-subtle p-2">
                  <span className="font-medium">{entry.speaker}:</span> {entry.text}
                </div>
              ))}
            </div>
          </details>
        )}

        <div className="mt-6 text-center text-xs text-text-muted">
          Bereitgestellt von eduhu 🦉
        </div>
      </div>
    </div>
  );
}
