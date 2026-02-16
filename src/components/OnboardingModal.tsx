import { useState } from 'react';

const API = import.meta.env.VITE_API_URL || '';

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

const FAECHER = [
  'Deutsch', 'Mathematik', 'Englisch', 'Physik', 'Chemie', 'Biologie',
  'Geschichte', 'Politik', 'Geographie', 'Informatik', 'Kunst', 'Musik',
  'Sport', 'Religion/Ethik', 'Pflege', 'Wirtschaft', 'Technik',
];

interface Props {
  teacherId: string;
  onComplete: () => void;
}

export function OnboardingModal({ teacherId, onComplete }: Props) {
  const [bundesland, setBundesland] = useState('');
  const [schulform, setSchulform] = useState('');
  const [selectedFaecher, setSelectedFaecher] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  const toggleFach = (fach: string) => {
    setSelectedFaecher(prev =>
      prev.includes(fach) ? prev.filter(f => f !== fach) : [...prev, fach]
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${API}/api/profile/${teacherId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bundesland,
          schulform,
          faecher: selectedFaecher,
        }),
      });
      onComplete();
    } catch {
      onComplete(); // Don't block on error
    }
  };

  const canSave = bundesland && schulform && selectedFaecher.length > 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🦉</div>
          <h2 className="text-xl font-semibold text-text-strong">Willkommen bei eduhu!</h2>
          <p className="text-sm text-text-muted mt-1">
            Damit ich dich optimal unterstützen kann, erzähl mir kurz was über dich.
          </p>
        </div>

        {/* Bundesland */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-text-strong mb-1">Bundesland</label>
          <select
            value={bundesland}
            onChange={e => setBundesland(e.target.value)}
            className="w-full rounded-lg border border-gray-200 p-2 text-sm"
          >
            <option value="">Bitte wählen...</option>
            {BUNDESLAENDER.map(bl => (
              <option key={bl} value={bl}>{bl}</option>
            ))}
          </select>
        </div>

        {/* Schulform */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-text-strong mb-1">Schulform</label>
          <select
            value={schulform}
            onChange={e => setSchulform(e.target.value)}
            className="w-full rounded-lg border border-gray-200 p-2 text-sm"
          >
            <option value="">Bitte wählen...</option>
            {SCHULFORMEN.map(sf => (
              <option key={sf} value={sf}>{sf}</option>
            ))}
          </select>
        </div>

        {/* Fächer */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-text-strong mb-2">
            Deine Fächer <span className="text-text-muted font-normal">(mehrere möglich)</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {FAECHER.map(fach => (
              <button
                key={fach}
                onClick={() => toggleFach(fach)}
                className={`rounded-full px-3 py-1 text-sm transition ${
                  selectedFaecher.includes(fach)
                    ? 'bg-primary text-white'
                    : 'bg-bg-subtle text-text-muted hover:bg-gray-200'
                }`}
              >
                {fach}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onComplete}
            className="flex-1 rounded-lg border border-gray-200 py-2 text-sm text-text-muted hover:bg-gray-50"
          >
            Später
          </button>
          <button
            onClick={handleSave}
            disabled={!canSave || saving}
            className="flex-1 rounded-lg bg-primary py-2 text-sm text-white hover:bg-primary/90 disabled:opacity-50"
          >
            {saving ? 'Speichere...' : 'Los geht\'s! 🚀'}
          </button>
        </div>
      </div>
    </div>
  );
}
