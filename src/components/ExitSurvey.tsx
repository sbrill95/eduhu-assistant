import { useState, type FormEvent } from 'react';
import { inviteColleagues } from '@/lib/auth';

interface Props {
  onClose: () => void;
  onEndDemo: () => void;
  onUpgrade: (email: string, survey: Record<string, string>) => Promise<void>;
  error?: string;
}

const SURVEY_QUESTIONS = [
  { id: 'useful', label: 'Wie nützlich fandest du den Assistenten?', options: ['Sehr nützlich', 'Nützlich', 'Etwas nützlich', 'Nicht nützlich'] },
  { id: 'material', label: 'Welche Materialarten waren am hilfreichsten?', options: ['Klausuren', 'Übungen (H5P)', 'Differenzierung', 'Stundenpläne', 'Anderes'] },
  { id: 'recommend', label: 'Würdest du eduhu weiterempfehlen?', options: ['Ja, definitiv', 'Wahrscheinlich', 'Eher nicht', 'Nein'] },
];

export function ExitSurvey({ onClose, onEndDemo, onUpgrade, error: externalError }: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState('');
  const [email, setEmail] = useState('');
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Invite colleagues state
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteList, setInviteList] = useState<string[]>([]);
  const [inviteSending, setInviteSending] = useState(false);
  const [inviteResult, setInviteResult] = useState('');

  const displayError = externalError || error;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setShowUpgrade(true);
  }

  async function handleUpgrade(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || loading) return;
    setError('');
    setLoading(true);
    try {
      await onUpgrade(email.trim(), { ...answers, feedback });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upgrade fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  function addInviteEmail() {
    const trimmed = inviteEmail.trim();
    if (trimmed && trimmed.includes('@') && !inviteList.includes(trimmed)) {
      setInviteList((prev) => [...prev, trimmed]);
      setInviteEmail('');
    }
  }

  async function handleSendInvites() {
    if (inviteList.length === 0 || inviteSending) return;
    setInviteSending(true);
    setInviteResult('');
    try {
      const result = await inviteColleagues(inviteList);
      setInviteResult(
        result.sent === result.total
          ? `${result.sent} Einladung${result.sent > 1 ? 'en' : ''} gesendet!`
          : `${result.sent} von ${result.total} gesendet.`,
      );
      setInviteList([]);
    } catch {
      setInviteResult('Einladungen konnten nicht gesendet werden.');
    } finally {
      setInviteSending(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        {success ? (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">📬</div>
              <h2 className="text-xl font-semibold text-text-strong">E-Mail gesendet!</h2>
              <p className="text-sm text-text-muted mt-2">
                Wir haben dir eine E-Mail an <strong>{email}</strong> geschickt.
                Klicke auf den Link in der E-Mail, um dein Konto dauerhaft zu aktivieren.
              </p>
            </div>

            {/* Invite colleagues section */}
            <div className="border-t border-gray-100 pt-5 mt-2 mb-5">
              <h3 className="text-sm font-semibold text-text-strong mb-2">
                Kollegen einladen
              </h3>
              <p className="text-xs text-text-muted mb-3">
                Teile eduhu mit Kolleginnen und Kollegen.
              </p>

              <div className="flex gap-2 mb-2">
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addInviteEmail();
                    }
                  }}
                  placeholder="kollege@schule.de"
                  className="input flex-1 text-sm"
                />
                <button
                  type="button"
                  onClick={addInviteEmail}
                  disabled={!inviteEmail.trim() || !inviteEmail.includes('@')}
                  className="rounded-lg bg-bg-subtle px-3 py-2 text-xs font-medium text-text-secondary hover:bg-gray-200 disabled:opacity-40"
                >
                  +
                </button>
              </div>

              {inviteList.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {inviteList.map((addr) => (
                    <span
                      key={addr}
                      className="inline-flex items-center gap-1 rounded-full bg-bg-subtle px-2.5 py-1 text-xs text-text-secondary"
                    >
                      {addr}
                      <button
                        type="button"
                        onClick={() => setInviteList((prev) => prev.filter((e) => e !== addr))}
                        className="text-text-muted hover:text-text-strong ml-0.5"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {inviteList.length > 0 && (
                <button
                  type="button"
                  onClick={() => void handleSendInvites()}
                  disabled={inviteSending}
                  className="w-full rounded-lg border border-gray-200 py-2 text-sm font-medium text-text-strong hover:bg-gray-50 disabled:opacity-50"
                >
                  {inviteSending
                    ? 'Wird gesendet…'
                    : `${inviteList.length} Einladung${inviteList.length > 1 ? 'en' : ''} senden`}
                </button>
              )}

              {inviteResult && (
                <p className="text-xs text-green-700 mt-2">{inviteResult}</p>
              )}
            </div>

            <button
              type="button"
              onClick={onClose}
              className="w-full rounded-lg bg-primary py-2.5 text-sm text-white hover:bg-primary/90"
            >
              Verstanden
            </button>
            <p className="text-center text-xs text-text-muted mt-4">
              Deine Demo-Daten bleiben noch 7 Tage erhalten.
            </p>
          </>
        ) : !showUpgrade ? (
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

              {displayError && (
                <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{displayError}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onEndDemo}
                  className="flex-1 rounded-lg border border-gray-200 py-2.5 text-sm text-text-muted hover:bg-gray-50"
                >
                  Nein, Demo beenden
                </button>
                <button
                  type="submit"
                  disabled={!email.trim() || loading}
                  className="flex-1 rounded-lg bg-primary py-2.5 text-sm text-white hover:bg-primary/90 disabled:opacity-50"
                >
                  {loading ? 'Wird gesendet…' : 'Account erstellen →'}
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
