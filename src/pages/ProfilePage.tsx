import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';
import {
  getProfile,
  updateProfile,
  listCurricula,
  uploadCurriculum,
  deleteCurriculum,
  getTokenUsage,
  type Curriculum,
  type TokenUsageSummary,
} from '@/lib/api';

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

// Mock data for Kurzzeitgedächtnis
const INITIAL_MEMORY_ITEMS = [
  { id: '1', icon: 'fa-solid fa-users-rays', iconBg: '#E8F5E9', iconColor: '#34C759', text: 'bevorzugt SOL' },
  { id: '2', icon: 'fa-solid fa-puzzle-piece', iconBg: '#F3E5F5', iconColor: '#9C27B0', text: 'immer Differenzierung für FS Lernen' },
  { id: '3', icon: 'fa-solid fa-bolt', iconBg: '#FFF9E0', iconColor: '#FFC107', text: 'aktivierende Einstiege' },
];

// Mock data for learning groups
const LEARNING_GROUPS = [
  { name: 'Mathe 8a', tag: 'Leistungsgruppen vorhanden' },
  { name: 'Mathe 8b', tag: 'Leistungsgruppen vorhanden' },
  { name: 'Englisch 13 LK', tag: null },
];

export default function ProfilePage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');

  // Token usage
  const [usage, setUsage] = useState<TokenUsageSummary | null>(null);
  const [usageDays, setUsageDays] = useState(7);
  const [usageLoading, setUsageLoading] = useState(false);

  // Form state
  const [bundesland, setBundesland] = useState('');
  const [schulform, setSchulform] = useState('');
  const [faecherText, setFaecherText] = useState('');
  const [jahrgaengeText, setJahrgaengeText] = useState('');

  // Memory items
  const [memoryItems, setMemoryItems] = useState(INITIAL_MEMORY_ITEMS);

  // Curricula
  const [curricula, setCurricula] = useState<Curriculum[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadFach, setUploadFach] = useState('');

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  useEffect(() => {
    void getProfile().then((p) => {
      if (p) {
        setBundesland(p.bundesland || '');
        setSchulform(p.schulform || '');
        setFaecherText((p.faecher || []).join(', '));
        setJahrgaengeText((p.jahrgaenge || []).join(', '));
      }
      setLoading(false);
    });
  }, []);

  const loadCurricula = useCallback(async () => {
    const data = await listCurricula();
    setCurricula(data);
  }, []);

  useEffect(() => {
    void loadCurricula();
  }, [loadCurricula]);

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
    const jahrgaenge = jahrgaengeText.split(',').map((j) => parseInt(j.trim(), 10)).filter((n) => !isNaN(n));
    await updateProfile({ bundesland, schulform, faecher, jahrgaenge });
    setSuccess('Profil gespeichert!');
    setSaving(false);
    setTimeout(() => setSuccess(''), 3000);
  }

  function removeMemoryItem(id: string) {
    setMemoryItems((prev) => prev.filter((item) => item.id !== id));
  }

  async function handleCurriculumUpload(file: File) {
    if (!uploadFach) return;
    setUploading(true);
    try {
      await uploadCurriculum(file, uploadFach, '', bundesland);
      setUploadFach('');
      await loadCurricula();
    } catch {
      // silent fail
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteCurriculum(id: string, fach: string) {
    if (!confirm(`"${fach}" wirklich löschen?`)) return;
    await deleteCurriculum(id);
    await loadCurricula();
  }

  if (!teacher) return null;

  return (
    <AppShell>
      <h1 className="text-2xl font-bold text-text-strong mb-6">Einstellungen & Profil</h1>

      {/* Two-column grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Left: Profile Form */}
        <div className="rounded-[20px] bg-bg-card p-7 shadow-soft">
          {loading ? (
            <p className="text-sm text-text-secondary">Laden...</p>
          ) : (
            <form onSubmit={(e) => void handleSave(e)} className="space-y-4">
              <div>
                <label className="block font-bold text-sm text-text-strong mb-2">Name</label>
                <input
                  type="text"
                  value={teacher.name}
                  disabled
                  className="w-full px-3.5 py-3 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-secondary outline-none"
                />
              </div>
              <div>
                <label className="block font-bold text-sm text-text-strong mb-2">Bundesland</label>
                <select
                  value={bundesland}
                  onChange={(e) => setBundesland(e.target.value)}
                  className="w-full px-3.5 py-3 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-strong outline-none transition-colors focus:bg-bg-card focus:border-border"
                >
                  <option value="">— Bitte wählen —</option>
                  {BUNDESLAENDER.map((bl) => (
                    <option key={bl} value={bl}>{bl}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block font-bold text-sm text-text-strong mb-2">Schulform</label>
                <select
                  value={schulform}
                  onChange={(e) => setSchulform(e.target.value)}
                  className="w-full px-3.5 py-3 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-strong outline-none transition-colors focus:bg-bg-card focus:border-border"
                >
                  <option value="">— Bitte wählen —</option>
                  {SCHULFORMEN.map((sf) => (
                    <option key={sf} value={sf}>{sf}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block font-bold text-sm text-text-strong mb-2">Fächer</label>
                <input
                  type="text"
                  value={faecherText}
                  onChange={(e) => setFaecherText(e.target.value)}
                  placeholder="Mathematik, Englisch, Physik"
                  className="w-full px-3.5 py-3 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-strong outline-none transition-colors focus:bg-bg-card focus:border-border"
                />
                <span className="block text-[11px] text-text-secondary mt-1">Kommagetrennt</span>
              </div>
              <div>
                <label className="block font-bold text-sm text-text-strong mb-2">Jahrgangsstufen</label>
                <input
                  type="text"
                  value={jahrgaengeText}
                  onChange={(e) => setJahrgaengeText(e.target.value)}
                  placeholder="7, 8, 9, 10"
                  className="w-full px-3.5 py-3 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-strong outline-none transition-colors focus:bg-bg-card focus:border-border"
                />
                <span className="block text-[11px] text-text-secondary mt-1">Kommagetrennt</span>
              </div>

              {success && (
                <div className="rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">{success}</div>
              )}

              <button
                type="submit"
                disabled={saving}
                className="bg-[#C0492C] text-white border-none px-6 py-3 rounded-[10px] font-bold cursor-pointer mt-2 transition-colors hover:bg-[#A03D24] disabled:opacity-50"
              >
                {saving ? 'Speichern...' : 'Speichern'}
              </button>
            </form>
          )}
        </div>

        {/* Right: Attributes */}
        <div className="rounded-[20px] bg-bg-card p-7 shadow-soft flex flex-col">
          {/* Kurzzeitgedächtnis */}
          <h3 className="text-[13px] font-bold uppercase text-text-secondary mb-5">
            Kurzzeitgedächtnis
          </h3>
          <div className="mb-2.5">
            {memoryItems.map((item) => (
              <div key={item.id} className="flex items-center justify-between py-2.5 bg-transparent">
                <div className="flex items-center gap-3.5">
                  <div
                    className="flex items-center justify-center w-8 h-8 rounded-lg text-sm"
                    style={{ backgroundColor: item.iconBg, color: item.iconColor }}
                  >
                    <i className={item.icon} />
                  </div>
                  <span className="font-semibold text-sm text-text-strong">{item.text}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeMemoryItem(item.id)}
                  className="text-text-secondary cursor-pointer text-base hover:text-error transition-colors bg-transparent border-none"
                >
                  <i className="fa-regular fa-trash-can" />
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            className="block text-center text-text-secondary font-semibold text-[13px] mb-6 cursor-pointer hover:text-primary hover:underline transition-colors bg-transparent border-none"
          >
            Alles ansehen
          </button>

          {/* Hinterlegte Rahmenlehrpläne */}
          <h3 className="text-[13px] font-bold uppercase text-text-secondary mb-5">
            Hinterlegte Rahmenlehrpläne
          </h3>
          <div className="mb-2.5">
            {curricula.map((c) => (
              <div key={c.id} className="flex items-center justify-between py-2.5 bg-transparent">
                <div className="flex items-center gap-3.5">
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg text-sm bg-primary-soft text-primary">
                    <i className="fa-solid fa-book-bookmark" />
                  </div>
                  <span className="font-semibold text-sm text-text-strong">
                    {c.fach}
                    {c.bundesland ? ` ${c.bundesland}` : ''}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDeleteCurriculum(c.id, c.fach)}
                  className="text-text-secondary cursor-pointer text-base hover:text-error transition-colors bg-transparent border-none"
                >
                  <i className="fa-regular fa-trash-can" />
                </button>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) void handleCurriculumUpload(f);
              e.target.value = '';
            }}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center justify-center gap-2 w-full mt-2.5 px-3 py-3 rounded-[14px] bg-bg-card text-text-secondary border-2 border-dashed border-border font-semibold text-[13px] cursor-pointer transition-colors hover:border-primary hover:text-primary hover:bg-primary-soft disabled:opacity-50"
          >
            <i className="fa-solid fa-cloud-arrow-up" />
            {uploading ? 'Wird hochgeladen...' : 'Rahmenlehrplan hochladen'}
          </button>
        </div>
      </div>

      {/* Learning Groups */}
      <div className="rounded-[20px] bg-bg-card p-7 shadow-soft mb-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-[13px] font-bold uppercase text-text-secondary">
            Lern- und Leistungsgruppen
          </h3>
          <i className="fa-solid fa-pen text-text-secondary cursor-pointer text-xs" />
        </div>
        <div className="flex gap-4 flex-wrap items-start">
          {LEARNING_GROUPS.map((group) => (
            <div
              key={group.name}
              className="flex flex-col justify-start rounded-[16px] bg-bg-card border border-border p-4 min-w-[140px] cursor-pointer shadow-soft transition-all hover:-translate-y-0.5 hover:shadow-elevated"
            >
              <div className="font-bold text-[15px] text-text-strong mb-2">{group.name}</div>
              {group.tag && (
                <span className="text-[10px] font-bold text-primary bg-primary-soft px-2 py-1 rounded-md inline-block">
                  {group.tag}
                </span>
              )}
            </div>
          ))}
          <button
            type="button"
            className="flex items-center justify-center rounded-[16px] border-2 border-dashed border-border min-w-[60px] min-h-[80px] cursor-pointer text-text-secondary transition-colors hover:border-text-secondary hover:text-text-strong bg-transparent"
          >
            <i className="fa-solid fa-plus text-xl" />
          </button>
        </div>
      </div>

      {/* Admin: Demo Mode Toggle */}
      {teacher.role === 'admin' && (
        <div className="rounded-[20px] bg-bg-card p-7 shadow-soft mb-6">
          <h3 className="text-[13px] font-bold uppercase text-text-secondary mb-5">
            Demo-Modus (Didacta)
          </h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-text-strong">Demo-Modus aktivieren</p>
              <p className="text-xs text-text-secondary mt-1">
                Zeigt "Demo starten" auf der Login-Seite. Demo-Accounts laufen nach 7 Tagen ab.
              </p>
            </div>
            <button
              type="button"
              onClick={async () => {
                const current = (document.getElementById('demo-toggle') as HTMLInputElement)?.checked;
                try {
                  const API = import.meta.env.VITE_API_URL || '';
                  await fetch(`${API}/api/auth/demo-toggle?enabled=${!current}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${teacher.access_token}` },
                  });
                  const toggle = document.getElementById('demo-toggle') as HTMLInputElement;
                  if (toggle) toggle.checked = !current;
                } catch { /* silent */ }
              }}
              className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors bg-bg-subtle hover:bg-gray-300"
            >
              <input type="checkbox" id="demo-toggle" className="sr-only peer" />
              <span className="peer-checked:translate-x-5 peer-checked:bg-primary inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform translate-x-0.5" />
            </button>
          </div>
        </div>
      )}

      {/* Token Usage */}
      <div className="rounded-[20px] bg-bg-card p-7 shadow-soft mb-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-[13px] font-bold uppercase text-text-secondary">
            Token-Verbrauch
          </h3>
          <select
            value={usageDays}
            onChange={(e) => setUsageDays(Number(e.target.value))}
            className="px-3 py-1.5 rounded-xl bg-[#F0EDE9] border border-transparent text-sm text-text-strong outline-none"
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
            <div className="grid grid-cols-3 gap-4 mb-5">
              <div className="rounded-2xl bg-[#F0EDE9] p-4 text-center">
                <p className="text-[11px] font-bold uppercase text-text-secondary mb-1">Anfragen</p>
                <p className="text-xl font-bold text-text-strong">{usage.total.calls}</p>
              </div>
              <div className="rounded-2xl bg-[#F0EDE9] p-4 text-center">
                <p className="text-[11px] font-bold uppercase text-text-secondary mb-1">Tokens</p>
                <p className="text-xl font-bold text-text-strong">
                  {((usage.total.input_tokens + usage.total.output_tokens) / 1000).toFixed(1)}k
                </p>
              </div>
              <div className="rounded-2xl bg-[#F0EDE9] p-4 text-center">
                <p className="text-[11px] font-bold uppercase text-text-secondary mb-1">Kosten</p>
                <p className="text-xl font-bold text-text-strong">
                  ${usage.total.cost_usd.toFixed(2)}
                </p>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-[11px] font-bold uppercase text-text-secondary">
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
                      <td className="py-2.5 pr-3 text-text-strong">{row.date}</td>
                      <td className="py-2.5 pr-3 text-text-secondary">
                        {row.model.replace('claude-', '').replace('-20250514', '').replace('-20241022', '')}
                      </td>
                      <td className="py-2.5 pr-3 text-right text-text-strong">
                        {(row.input_tokens / 1000).toFixed(1)}k
                      </td>
                      <td className="py-2.5 pr-3 text-right text-text-strong">
                        {(row.output_tokens / 1000).toFixed(1)}k
                      </td>
                      <td className="py-2.5 pr-3 text-right text-text-strong">{row.calls}</td>
                      <td className="py-2.5 text-right text-text-strong">
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
    </AppShell>
  );
}
