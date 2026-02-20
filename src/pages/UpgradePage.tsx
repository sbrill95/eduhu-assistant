import { useState, type FormEvent } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { completeDemoUpgrade } from '../lib/auth';

export default function UpgradePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const token = searchParams.get('token');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) {
      setError('Ungültiger Aktivierungslink.');
      return;
    }
    if (password.length < 8) {
      setError('Passwort muss mindestens 8 Zeichen lang sein.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwörter stimmen nicht überein.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await completeDemoUpgrade(token, password, name.trim());
      void navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Aktivierung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg-page px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mb-3 text-6xl">🎓</div>
          <h1 className="text-2xl font-bold text-text-strong">
            Konto aktivieren
          </h1>
          <p className="mt-2 text-sm text-text-muted">
            Setze deinen Namen und ein Passwort, um dein eduhu-Konto dauerhaft zu nutzen.
          </p>
        </div>
        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="card space-y-4"
        >
          <div>
            <label
              htmlFor="upgrade-name"
              className="mb-1.5 block text-sm font-medium text-text-strong"
            >
              Name <span className="text-text-muted font-normal">(optional)</span>
            </label>
            <input
              id="upgrade-name"
              type="text"
              autoFocus
              className="input"
              placeholder="Dein Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label
              htmlFor="upgrade-password"
              className="mb-1.5 block text-sm font-medium text-text-strong"
            >
              Passwort
            </label>
            <input
              id="upgrade-password"
              type="password"
              className="input"
              placeholder="Mind. 8 Zeichen"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError('');
              }}
              disabled={loading}
            />
          </div>
          <div>
            <label
              htmlFor="upgrade-confirm"
              className="mb-1.5 block text-sm font-medium text-text-strong"
            >
              Passwort bestätigen
            </label>
            <input
              id="upgrade-confirm"
              type="password"
              className="input"
              placeholder="Passwort wiederholen"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                setError('');
              }}
              disabled={loading}
            />
          </div>
          {error && (
            <p className="text-sm text-error" role="alert">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Wird aktiviert...' : 'Konto aktivieren'}
          </button>
        </form>
      </div>
    </div>
  );
}
