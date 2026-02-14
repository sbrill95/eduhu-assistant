import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';
import { getProfile, updateProfile } from '@/lib/api';
import type { Profile } from '@/lib/api';

const BUNDESLAENDER = [
  'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen',
  'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen',
  'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen',
  'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen',
];

const SCHULFORMEN = [
  'Grundschule', 'Hauptschule', 'Realschule', 'Gymnasium',
  'Gesamtschule', 'Berufsschule', 'Förderschule', 'Sonstige',
];

export default function ProfilePage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');

  // Form state
  const [bundesland, setBundesland] = useState('');
  const [schulform, setSchulform] = useState('');
  const [faecherText, setFaecherText] = useState('');
  const [jahrgaengeText, setJahrgaengeText] = useState('');

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  useEffect(() => {
    void getProfile().then((p) => {
      if (p) {
        setProfile(p);
        setBundesland(p.bundesland || '');
        setSchulform(p.schulform || '');
        setFaecherText((p.faecher || []).join(', '));
        setJahrgaengeText((p.jahrgaenge || []).join(', '));
      }
      setLoading(false);
    });
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSuccess('');

    const faecher = faecherText.split(',').map((f) => f.trim()).filter(Boolean);
    const jahrgaenge = jahrgaengeText
      .split(',')
      .map((j) => parseInt(j.trim(), 10))
      .filter((n) => !isNaN(n));

    await updateProfile({ bundesland, schulform, faecher, jahrgaenge });
    setSuccess('✅ Profil gespeichert');
    setSaving(false);
  }

  if (!teacher) return null;

  return (
    <AppShell>
      <div className="mx-auto max-w-xl overflow-y-auto px-4 py-6">
        <h1 className="mb-1 text-2xl font-bold text-text-strong">⚙️ Profil</h1>
        <p className="mb-6 text-sm text-text-secondary">
          Diese Infos helfen eduhu, dir bessere Antworten zu geben.
        </p>

        {loading ? (
          <p className="text-sm text-text-secondary">Laden...</p>
        ) : (
          <form onSubmit={(e) => void handleSave(e)} className="space-y-5 rounded-[var(--radius-card)] bg-bg-card p-5 shadow-card">
            {/* Name (read-only) */}
            <div>
              <label className="mb-1 block text-sm font-medium text-text-default">Name</label>
              <div className="rounded-[var(--radius-input)] border border-border bg-bg-subtle px-3 py-2 text-sm text-text-secondary">
                {profile?.name || teacher.name}
              </div>
            </div>

            {/* Bundesland */}
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

            {/* Schulform */}
            <div>
              <label htmlFor="schulform" className="mb-1 block text-sm font-medium text-text-default">
                Schulform
              </label>
              <select
                id="schulform"
                value={schulform}
                onChange={(e) => setSchulform(e.target.value)}
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              >
                <option value="">— Bitte wählen —</option>
                {SCHULFORMEN.map((sf) => (
                  <option key={sf} value={sf}>{sf}</option>
                ))}
              </select>
            </div>

            {/* Fächer */}
            <div>
              <label htmlFor="faecher" className="mb-1 block text-sm font-medium text-text-default">
                Fächer
              </label>
              <input
                id="faecher"
                type="text"
                value={faecherText}
                onChange={(e) => setFaecherText(e.target.value)}
                placeholder="z.B. Physik, Mathematik, Informatik"
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              />
              <p className="mt-1 text-xs text-text-secondary">Kommagetrennt</p>
            </div>

            {/* Jahrgänge */}
            <div>
              <label htmlFor="jahrgaenge" className="mb-1 block text-sm font-medium text-text-default">
                Jahrgangsstufen
              </label>
              <input
                id="jahrgaenge"
                type="text"
                value={jahrgaengeText}
                onChange={(e) => setJahrgaengeText(e.target.value)}
                placeholder="z.B. 7, 8, 9, 10"
                className="w-full rounded-[var(--radius-input)] border border-border bg-bg-page px-3 py-2 text-sm"
              />
              <p className="mt-1 text-xs text-text-secondary">Kommagetrennt</p>
            </div>

            {success && (
              <div className="rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">{success}</div>
            )}

            <button
              type="submit"
              disabled={saving}
              className="rounded-[var(--radius-btn)] bg-primary px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-hover disabled:opacity-50"
            >
              {saving ? 'Speichern...' : 'Speichern'}
            </button>
          </form>
        )}
      </div>
    </AppShell>
  );
}
