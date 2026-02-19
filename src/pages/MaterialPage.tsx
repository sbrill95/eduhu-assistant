import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '../lib/auth';
import { AppShell } from '@/components/layout/AppShell';

const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

interface ExamTask {
  aufgabe: string;
  beschreibung: string;
  afb_level: string;
  punkte: number;
  erwartung: string[];
}

interface DiffTask {
  aufgabe: string;
  beschreibung: string;
  hilfestellung?: string;
  punkte: number;
}

interface DiffNiveau {
  niveau: string;
  aufgaben: DiffTask[];
  zeitaufwand_minuten: number;
  hinweise: string[];
}

interface MaterialResult {
  id: string;
  type: string;
  content: Record<string, unknown>;
  docx_url: string | null;
  created_at: string;
}

export default function MaterialPage() {
  const navigate = useNavigate();
  const teacher = getSession();

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  const [type, setType] = useState<'klausur' | 'differenzierung'>('klausur');
  const [fach, setFach] = useState('');
  const [klasse, setKlasse] = useState('');
  const [thema, setThema] = useState('');
  const [dauer, setDauer] = useState('');
  const [zusatz, setZusatz] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MaterialResult | null>(null);
  const [error, setError] = useState('');
  const [activeNiveau, setActiveNiveau] = useState(0);

  const handleGenerate = async () => {
    const teacher = getSession();
    if (!teacher) return;
    if (!fach || !klasse || !thema) {
      setError('Bitte Fach, Klasse und Thema ausfüllen.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const body: Record<string, unknown> = {
        type,
        fach,
        klasse,
        thema,
        teacher_id: teacher.teacher_id,
      };
      if (type === 'klausur' && dauer) body.dauer_minuten = parseInt(dauer);
      if (zusatz) body.zusatz_anweisungen = zusatz;

      const res = await fetch(`${BASE}/api/materials/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Fehler' }));
        throw new Error(err.detail || 'Generierung fehlgeschlagen');
      }

      const data = (await res.json()) as MaterialResult;
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unbekannter Fehler');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.docx_url) return;
    window.open(`${BASE}${result.docx_url}`, '_blank');
  };

  if (!teacher) return null;

  return (
    <AppShell>
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-text-strong mb-6">Material erstellen</h1>

      {/* Form */}
      <div className="bg-white rounded-xl shadow-sm border border-[#E8DDD4] p-6 mb-6">
        {/* Type Selection */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-[#2D2018] mb-2">Material-Typ</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="type"
                checked={type === 'klausur'}
                onChange={() => setType('klausur')}
                className="accent-[#C8552D]"
              />
              <span className="text-sm">Klassenarbeit / Klausur</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="type"
                checked={type === 'differenzierung'}
                onChange={() => setType('differenzierung')}
                className="accent-[#C8552D]"
              />
              <span className="text-sm">Differenziertes Material</span>
            </label>
          </div>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-[#2D2018] mb-1">Fach *</label>
            <input
              type="text"
              value={fach}
              onChange={(e) => setFach(e.target.value)}
              placeholder="z.B. Physik"
              className="w-full px-3 py-2 border border-[#E8DDD4] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#C8552D]/30"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2D2018] mb-1">Klasse *</label>
            <input
              type="text"
              value={klasse}
              onChange={(e) => setKlasse(e.target.value)}
              placeholder="z.B. 8"
              className="w-full px-3 py-2 border border-[#E8DDD4] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#C8552D]/30"
            />
          </div>
          {type === 'klausur' && (
            <div>
              <label className="block text-sm font-medium text-[#2D2018] mb-1">Dauer (Min.)</label>
              <input
                type="number"
                value={dauer}
                onChange={(e) => setDauer(e.target.value)}
                placeholder="45"
                className="w-full px-3 py-2 border border-[#E8DDD4] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#C8552D]/30"
              />
            </div>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-[#2D2018] mb-1">Thema *</label>
          <input
            type="text"
            value={thema}
            onChange={(e) => setThema(e.target.value)}
            placeholder="z.B. Optik - Reflexion und Brechung"
            className="w-full px-3 py-2 border border-[#E8DDD4] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#C8552D]/30"
          />
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-[#2D2018] mb-1">Zusätzliche Anweisungen</label>
          <textarea
            value={zusatz}
            onChange={(e) => setZusatz(e.target.value)}
            rows={2}
            placeholder="z.B. Fokus auf Snellius-Brechungsgesetz, einfache Sprache"
            className="w-full px-3 py-2 border border-[#E8DDD4] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#C8552D]/30 resize-none"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-3 bg-[#C8552D] text-white font-medium rounded-lg hover:bg-[#A8461F] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Material wird generiert...
            </span>
          ) : (
            '✨ Material erstellen'
          )}
        </button>

        {error && (
          <p className="mt-3 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-[#E8DDD4] p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-[#2D2018]">
              {result.type === 'klausur' ? '📋 Klassenarbeit' : '📊 Differenziertes Material'}
            </h2>
            {result.docx_url && (
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-[#C8552D] text-white text-sm font-medium rounded-lg hover:bg-[#A8461F] transition-colors"
              >
                📥 DOCX herunterladen
              </button>
            )}
          </div>

          {result.type === 'klausur' && <KlausurPreview content={result.content} />}
          {result.type === 'differenzierung' && (
            <DiffPreview content={result.content} activeNiveau={activeNiveau} setActiveNiveau={setActiveNiveau} />
          )}
        </div>
      )}
    </div>
    </AppShell>
  );
}

function KlausurPreview({ content }: { content: Record<string, unknown> }) {
  const aufgaben = (content.aufgaben || []) as ExamTask[];
  const gesamtpunkte = content.gesamtpunkte as number;
  const hinweise = (content.hinweise || []) as string[];
  const notenschluessel = (content.notenschluessel || {}) as Record<string, string>;

  return (
    <div>
      <p className="text-sm text-[#6B5B4F] mb-4">
        {content.fach as string} · Klasse {content.klasse as string} · {content.dauer_minuten as number} Min. · {gesamtpunkte} Punkte
      </p>

      {hinweise.length > 0 && (
        <div className="mb-4 bg-[#FFF8F0] p-3 rounded-lg">
          <p className="text-xs font-medium text-[#6B5B4F] mb-1">Hinweise:</p>
          {hinweise.map((h, i) => (
            <p key={i} className="text-xs text-[#6B5B4F]">• {h}</p>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {aufgaben.map((task, i) => (
          <div key={i} className="border border-[#E8DDD4] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-bold text-[#2D2018]">Aufgabe {i + 1}</span>
              <span className="text-xs px-2 py-0.5 bg-[#FADDD0] text-[#C8552D] rounded-full font-medium">
                {task.afb_level}
              </span>
              <span className="text-xs text-[#6B5B4F]">{task.punkte} P.</span>
            </div>
            <p className="text-sm text-[#2D2018] whitespace-pre-line">{task.beschreibung}</p>
            {task.erwartung.length > 0 && (
              <details className="mt-3">
                <summary className="text-xs text-[#C8552D] cursor-pointer font-medium">
                  Erwartungshorizont anzeigen
                </summary>
                <ul className="mt-2 space-y-1">
                  {task.erwartung.map((e, j) => (
                    <li key={j} className="text-xs text-[#6B5B4F]">• {e}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        ))}
      </div>

      {Object.keys(notenschluessel).length > 0 && (
        <div className="mt-4 border border-[#E8DDD4] rounded-lg p-4">
          <p className="text-sm font-medium text-[#2D2018] mb-2">Notenschlüssel</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(notenschluessel).map(([note, punkte]) => (
              <div key={note} className="text-xs text-[#6B5B4F]">
                <span className="font-medium">{note}:</span> {punkte}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DiffPreview({
  content,
  activeNiveau,
  setActiveNiveau,
}: {
  content: Record<string, unknown>;
  activeNiveau: number;
  setActiveNiveau: (n: number) => void;
}) {
  const niveaus = (content.niveaus || []) as DiffNiveau[];
  const niveauColors = ['#2E7D32', '#F57C00', '#C62828'];
  const niveauBg = ['#E8F5E9', '#FFF3E0', '#FFEBEE'];
  const active = niveaus[activeNiveau];

  return (
    <div>
      <p className="text-sm text-[#6B5B4F] mb-4">
        {content.fach as string} · Klasse {content.klasse as string}
      </p>

      {/* Niveau Tabs */}
      <div className="flex gap-2 mb-4">
        {niveaus.map((n, i) => (
          <button
            key={i}
            onClick={() => setActiveNiveau(i)}
            className="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
            style={{
              backgroundColor: activeNiveau === i ? niveauBg[i] : 'transparent',
              color: niveauColors[i],
              border: `1px solid ${activeNiveau === i ? niveauColors[i] : '#E8DDD4'}`,
            }}
          >
            {n.niveau} ({n.zeitaufwand_minuten} Min.)
          </button>
        ))}
      </div>

      {active && (
        <div>
          {active.hinweise.length > 0 && (
            <div className="mb-4 p-3 rounded-lg" style={{ backgroundColor: niveauBg[activeNiveau] }}>
              {active.hinweise.map((h, i) => (
                <p key={i} className="text-xs text-[#6B5B4F]">• {h}</p>
              ))}
            </div>
          )}

          <div className="space-y-4">
            {active.aufgaben.map((task, i) => (
              <div key={i} className="border border-[#E8DDD4] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-bold text-[#2D2018]">{task.aufgabe}</span>
                  <span className="text-xs text-[#6B5B4F]">{task.punkte} P.</span>
                </div>
                <p className="text-sm text-[#2D2018] whitespace-pre-line">{task.beschreibung}</p>
                {task.hilfestellung && (
                  <p className="mt-2 text-xs text-[#6B5B4F] italic bg-[#FFF8F0] px-3 py-2 rounded">
                    💡 {task.hilfestellung}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
