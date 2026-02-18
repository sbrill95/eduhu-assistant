import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';
import { getProfile, updateProfile, getTokenUsage, type TokenUsageSummary } from '@/lib/api';
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

  const [usage, setUsage] = useState<TokenUsageSummary | null>(null);
  const [usageDays, setUsageDays] = useState(7);
  const [usageLoading, setUsageLoading] = useState(false);

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

  useEffect(() => {
    setUsageLoading(true);
    void getTokenUsage(usageDays)
      .then((u) => {
        setUsage(u);
        setUsageLoading(false);
      })
      .catch(() => setUsageLoading(false));
  }, [usageDays]);

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

        {/* Token Usage Section */}
        <div className="mt-6 rounded-[var(--radius-card)] bg-bg-card p-5 shadow-card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-text-strong">📊 Token-Verbrauch</h2>
            <select
              value={usageDays}
              onChange={(e) => setUsageDays(Number(e.target.value))}
              className="rounded-[var(--radius-input)] border border-border bg-bg-page px-2 py-1 text-sm"
            >
              <option value={7}>7 Tage</option>
              <option value={30}>30 Tage</option>
              <option value={90}>90 Tage</option>
            </select>
          </div>
          {usageLoading ? (
            <p className="text-sm text-text-secondary">Laden...</p>
          ) : usage && usage.daily.length > 0 ? (
            <>
              {/* Total summary */}
              <div className="mb-4 grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-bg-subtle p-3 text-center">
                  <p className="text-xs text-text-secondary">Anfragen</p>
                  <p className="text-lg font-bold text-text-strong">{usage.total.calls}</p>
                </div>
                <div className="rounded-lg bg-bg-subtle p-3 text-center">
                  <p className="text-xs text-text-secondary">Tokens</p>
                  <p className="text-lg font-bold text-text-strong">
                    {((usage.total.input_tokens + usage.total.output_tokens) / 1000).toFixed(1)}k
                  </p>
                </div>
                <div className="rounded-lg bg-bg-subtle p-3 text-center">
                  <p className="text-xs text-text-secondary">Kosten</p>
                  <p className="text-lg font-bold text-text-strong">
                    ${usage.total.cost_usd.toFixed(2)}
                  </p>
                </div>
              </div>
              {/* Daily breakdown table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs text-text-secondary">
                      <th className="pb-2 pr-3">Datum</th>
                      <th className="pb-2 pr-3">Modell</th>
                      <th className="pb-2 pr-3 text-right">Input</th>
                      <th className="pb-2 pr-3 text-right">Output</th>
                      <th className="pb-2 pr-3 text-right">Calls</th>
                      <th className="pb-2 text-right">Kosten</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usage.daily.map((row, i) => (
                      <tr key={i} className="border-b border-border/50">
                        <td className="py-2 pr-3 text-text-default">{row.date}</td>
                        <td className="py-2 pr-3 text-text-secondary">
                          {row.model.replace('claude-', '').replace('-20250514', '').replace('-20241022', '')}
                        </td>
                        <td className="py-2 pr-3 text-right text-text-default">
                          {(row.input_tokens / 1000).toFixed(1)}k
                        </td>
                        <td className="py-2 pr-3 text-right text-text-default">
                          {(row.output_tokens / 1000).toFixed(1)}k
                        </td>
                        <td className="py-2 pr-3 text-right text-text-default">{row.calls}</td>
                        <td className="py-2 text-right text-text-default">
                          ${row.cost_usd.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="text-sm text-text-secondary">Noch keine Nutzungsdaten vorhanden.</p>
          )}
        </div>
      </div>
    </AppShell>
  );
}
