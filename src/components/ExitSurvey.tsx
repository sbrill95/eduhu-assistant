import { useState, type FormEvent } from 'react';

interface Props {
  onClose: () => void;
  onUpgrade: (email: string) => void;
}

const SURVEY_QUESTIONS = [
  { id: 'useful', label: 'Wie nützlich fandest du den Assistenten?', options: ['Sehr nützlich', 'Nützlich', 'Etwas nützlich', 'Nicht nützlich'] },
  { id: 'material', label: 'Welche Materialarten waren am hilfreichsten?', options: ['Klausuren', 'Übungen (H5P)', 'Differenzierung', 'Stundenpläne', 'Anderes'] },
  { id: 'recommend', label: 'Würdest du eduhu weiterempfehlen?', options: ['Ja, definitiv', 'Wahrscheinlich', 'Eher nicht', 'Nein'] },
];

export function ExitSurvey({ onClose, onUpgrade }: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState('');
  const [email, setEmail] = useState('');
  const [showUpgrade, setShowUpgrade] = useState(false);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // TODO: Send survey data to backend
    console.log('Survey:', { answers, feedback });
    setShowUpgrade(true);
  }

  function handleUpgrade(e: FormEvent) {
    e.preventDefault();
    if (email.trim()) {
      onUpgrade(email);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        {!showUpgrade ? (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">📋</div>
              <h2 className="text-xl font-semibold text-text-strong">Demo beenden</h2>
              <p className="text-sm text-text-muted mt-1">
                Kurzes Feedback — hilft uns, eduhu besser zu machen.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {SURVEY_QUESTIONS.map((q) => (
                <div key={q.id}>
                  <label className="block text-sm font-medium text-text-strong mb-2">{q.label}</label>
                  <div className="flex flex-wrap gap-2">
                    {q.options.map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                        className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
                          answers[q.id] === opt
                            ? 'bg-primary text-white'
                            : 'bg-bg-subtle text-text-secondary hover:bg-gray-200'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-text-strong mb-2">
                  Sonstiges Feedback <span className="text-text-muted font-normal">(optional)</span>
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  rows={3}
                  placeholder="Was hat dir gefallen? Was können wir verbessern?"
                  className="w-full rounded-lg border border-gray-200 p-3 text-sm resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 rounded-lg border border-gray-200 py-2.5 text-sm text-text-muted hover:bg-gray-50"
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="flex-1 rounded-lg bg-primary py-2.5 text-sm text-white hover:bg-primary/90"
                >
                  Weiter →
                </button>
              </div>
            </form>
          </>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">🎓</div>
              <h2 className="text-xl font-semibold text-text-strong">Account behalten?</h2>
              <p className="text-sm text-text-muted mt-1">
                Registriere dich mit E-Mail, um deine Daten zu behalten und eduhu weiter zu nutzen.
              </p>
            </div>

            <form onSubmit={handleUpgrade} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-strong mb-1.5">E-Mail</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="deine@email.de"
                  className="input w-full"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 rounded-lg border border-gray-200 py-2.5 text-sm text-text-muted hover:bg-gray-50"
                >
                  Nein, Demo beenden
                </button>
                <button
                  type="submit"
                  disabled={!email.trim()}
                  className="flex-1 rounded-lg bg-primary py-2.5 text-sm text-white hover:bg-primary/90 disabled:opacity-50"
                >
                  Account erstellen →
                </button>
              </div>
            </form>

            <p className="text-center text-xs text-text-muted mt-4">
              Deine Demo-Daten bleiben noch 7 Tage erhalten.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
