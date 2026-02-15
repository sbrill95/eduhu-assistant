import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

const PollPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState<string[]>([]);
  const [voted, setVoted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!code) return;
    fetch(`${API_BASE}/api/public/poll/${code}`)
      .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
      .then((data) => {
        setQuestion(data.question);
        setOptions(data.options);
      })
      .catch(() => setError('Abstimmung nicht gefunden.'))
      .finally(() => setLoading(false));
  }, [code]);

  async function vote(option: string) {
    setSubmitting(true);
    try {
      await fetch(`${API_BASE}/api/public/poll/${code}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option }),
      });
      setVoted(true);
    } catch {
      setError('Abstimmung fehlgeschlagen.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-[#F5F0EB] flex items-center justify-center font-[Inter]">
      <div className="text-lg text-gray-600">Lade…</div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#F5F0EB] flex items-center justify-center font-[Inter]">
      <div className="text-lg text-red-600">{error}</div>
    </div>
  );

  if (voted) return (
    <div className="min-h-screen bg-[#F5F0EB] flex items-center justify-center font-[Inter]">
      <div className="text-center">
        <div className="text-6xl mb-4">✅</div>
        <h1 className="text-2xl font-bold text-[#2D2018]">Danke für deine Stimme!</h1>
        <p className="text-[#8B7355] mt-2">Deine Antwort wurde gespeichert.</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F5F0EB] font-[Inter] p-5">
      <header className="text-center mb-8 pt-8">
        <div className="text-5xl mb-3">📊</div>
        <h1 className="text-2xl font-bold text-[#2D2018]">{question}</h1>
        <p className="text-[#8B7355] mt-1 text-sm">Wähle eine Antwort</p>
      </header>
      <div className="max-w-md mx-auto space-y-3">
        {options.map((opt) => (
          <button
            key={opt}
            onClick={() => vote(opt)}
            disabled={submitting}
            className="w-full bg-white rounded-xl shadow-sm p-4 text-left hover:shadow-md hover:bg-[#FAF7F4] transition-all text-[#2D2018] font-medium text-lg disabled:opacity-50 active:scale-[0.98]"
          >
            {opt}
          </button>
        ))}
      </div>
      <footer className="text-center mt-8">
        <p className="text-xs text-[#8B7355]">🦉 eduhu-assistant</p>
      </footer>
    </div>
  );
};

export default PollPage;
