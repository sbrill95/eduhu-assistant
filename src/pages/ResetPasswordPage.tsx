import { useState, type FormEvent } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { resetPassword } from '../lib/auth';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const token = searchParams.get('token');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) {
      setError('Ungültiger Reset-Link.');
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
      const msg = await resetPassword(token, password);
      setSuccess(msg);
      setTimeout(() => void navigate('/'), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg-page px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mb-3 text-6xl">🦉</div>
          <h1 className="text-2xl font-bold text-text-strong">
            Neues Passwort
          </h1>
        </div>
        {success ? (
          <div className="card p-6 text-center">
            <p className="text-sm text-green-700">{success}</p>
            <p className="mt-2 text-xs text-text-secondary">
              Du wirst gleich weitergeleitet...
            </p>
          </div>
        ) : (
          <form
            onSubmit={(e) => void handleSubmit(e)}
            className="card space-y-4"
          >
            <div>
              <label
                htmlFor="new-password"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                Neues Passwort
              </label>
              <input
                id="new-password"
                type="password"
                autoFocus
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
                htmlFor="confirm-password"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                Passwort bestätigen
              </label>
              <input
                id="confirm-password"
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
              {loading ? 'Speichern...' : 'Passwort ändern'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
