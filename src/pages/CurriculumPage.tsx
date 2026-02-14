import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';
import { uploadCurriculum, listCurricula, deleteCurriculum } from '@/lib/api';
import type { Curriculum } from '@/lib/api';

const BUNDESLAENDER = [
  'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen',
  'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen',
  'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen',
  'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen', 'Bundesweit',
];

export default function CurriculumPage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const [curricula, setCurricula] = useState<Curriculum[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [file, setFile] = useState<File | null>(null);
  const [fach, setFach] = useState('');
  const [jahrgang, setJahrgang] = useState('');
  const [bundesland, setBundesland] = useState('');

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  const loadCurricula = useCallback(async () => {
    const data = await listCurricula();
    setCurricula(data);
    setLoading(false);
  }, []);

  useEffect(() => {
    void loadCurricula();
  }, [loadCurricula]);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !fach) return;

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const result = await uploadCurriculum(file, fach, jahrgang, bundesland);
      setSuccess(`✅ "${fach}" erfolgreich hochgeladen — ${result.chunks} Abschnitte erstellt`);
      setFile(null);
      setFach('');
      setJahrgang('');
      setBundesland('');
      // Reset file input
      const input = document.getElementById('file-input') as HTMLInputElement;
      if (input) input.value = '';
      await loadCurricula();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload fehlgeschlagen');
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string, fach: string) {
    if (!confirm(`"${fach}" wirklich löschen?`)) return;
    await deleteCurriculum(id);
    await loadCurricula();
  }

  if (!teacher) return null;

  return (
    <AppShell>
      <div className="mx-auto max-w-2xl overflow-y-auto px-4 py-6">
        <h1 className="mb-1 text-2xl font-bold text-text-strong">📚 Lehrpläne</h1>
        <p className="mb-6 text-sm text-text-secondary">
          Lade Rahmenlehrpläne als PDF hoch. eduhu kann dann daraus zitieren und Inhalte finden.
        </p>

        {/* Upload Form */}
        <form onSubmit={(e) => void handleUpload(e)} className="mb-8 rounded-[var(--radius-card)] bg-bg-card p-5 shadow-card">
          <h2 className="mb-4 text-lg font-semibold text-text-strong">Neuer Lehrplan</h2>

          <div className="mb-4">
            <label htmlFor="file-input" className="mb-1 block text-sm font-medium text-text-default">
              PDF-Datei
            </label>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-primary file:px-3 file:py-1 file:text-sm file:font-medium file:text-white"
            />
          </div>

          <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label htmlFor="fach" className="mb-1 block text-sm font-medium text-text-default">
                Fach *
              </label>
              <input
                id="fach"
                type="text"
                value={fach}
                onChange={(e) => setFach(e.target.value)}
                placeholder="z.B. Physik"
                required
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="jahrgang" className="mb-1 block text-sm font-medium text-text-default">
                Jahrgang / Stufe
              </label>
              <input
                id="jahrgang"
                type="text"
                value={jahrgang}
                onChange={(e) => setJahrgang(e.target.value)}
                placeholder="z.B. Gymnasium"
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="bundesland" className="mb-1 block text-sm font-medium text-text-default">
                Bundesland
              </label>
              <select
                id="bundesland"
                value={bundesland}
                onChange={(e) => setBundesland(e.target.value)}
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              >
                <option value="">— Bitte wählen —</option>
                {BUNDESLAENDER.map((bl) => (
                  <option key={bl} value={bl}>{bl}</option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
          )}
          {success && (
            <div className="mb-4 rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">{success}</div>
          )}

          <button
            type="submit"
            disabled={!file || !fach || uploading}
            className="rounded-[var(--radius-btn)] bg-primary px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-hover disabled:opacity-50"
          >
            {uploading ? '⏳ Wird verarbeitet...' : '📤 Hochladen'}
          </button>

          {uploading && (
            <p className="mt-2 text-xs text-text-secondary">
              PDF wird gelesen, in Abschnitte geteilt und mit Embeddings versehen. Das kann bis zu 2 Minuten dauern...
            </p>
          )}
        </form>

        {/* Existing Curricula */}
        <h2 className="mb-3 text-lg font-semibold text-text-strong">Deine Lehrpläne</h2>
        {loading ? (
          <p className="text-sm text-text-secondary">Laden...</p>
        ) : curricula.length === 0 ? (
          <p className="text-sm text-text-secondary">
            Noch keine Lehrpläne hochgeladen. Lade oben einen Rahmenlehrplan als PDF hoch!
          </p>
        ) : (
          <div className="space-y-3">
            {curricula.map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between rounded-[var(--radius-card)] bg-bg-card p-4 shadow-card"
              >
                <div>
                  <div className="font-medium text-text-strong">{c.fach}</div>
                  <div className="text-xs text-text-secondary">
                    {[c.jahrgang, c.bundesland].filter(Boolean).join(' · ')}
                    {c.filename && ` · ${c.filename}`}
                  </div>
                  <div className="mt-1 text-xs">
                    {c.status === 'active' ? (
                      <span className="text-green-600">✅ Aktiv</span>
                    ) : (
                      <span className="text-amber-600">⏳ {c.status}</span>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDelete(c.id, c.fach)}
                  className="rounded-lg px-3 py-1.5 text-sm text-red-500 transition-colors hover:bg-red-50"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
