import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '@/lib/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!password.trim()) {
      setError('Bitte gib dein Passwort ein.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(password);
      void navigate('/chat');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg-page px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="mb-3 text-6xl">🦉</div>
          <h1 className="text-2xl font-bold text-text-strong">eduhu</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Dein KI-Assistent im Lehrerzimmer
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={(e) => void handleSubmit(e)} className="card space-y-4">
          <div>
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-text-strong">
              Passwort
            </label>
            <input
              id="password"
              type="password"
              autoFocus
              className="input"
              placeholder="Dein Passwort"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) setError('');
              }}
              disabled={loading}
            />
            {error && (
              <p className="mt-2 text-sm text-error" role="alert">
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Anmelden...' : 'Anmelden →'}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-text-muted">
          © 2026 eduhu GmbH
        </p>
      </div>
    </div>
  );
}
