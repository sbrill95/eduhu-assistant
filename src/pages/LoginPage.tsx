import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register, requestMagicLink, forgotPassword } from '../lib/auth';

const API = import.meta.env.VITE_API_URL || '';

type Tab = 'login' | 'register' | 'forgot';

export default function LoginPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/health`).catch(() => {});
  }, []);

  function clearMessages() {
    setError('');
    setSuccess('');
  }

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Bitte E-Mail und Passwort eingeben.');
      return;
    }
    setLoading(true);
    clearMessages();
    try {
      await login(email, password);
      void navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim() || !name.trim()) {
      setError('Bitte alle Felder ausfüllen.');
      return;
    }
    if (password.length < 8) {
      setError('Passwort muss mindestens 8 Zeichen lang sein.');
      return;
    }
    setLoading(true);
    clearMessages();
    try {
      const msg = await register(email, password, name);
      setSuccess(msg);
      setTab('login');
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Registrierung fehlgeschlagen',
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleMagicLink() {
    if (!email.trim()) {
      setError('Bitte E-Mail eingeben.');
      return;
    }
    setLoading(true);
    clearMessages();
    try {
      const msg = await requestMagicLink(email);
      setSuccess(msg);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Magic Link fehlgeschlagen',
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleForgot(e: FormEvent) {
    e.preventDefault();
    if (!email.trim()) {
      setError('Bitte E-Mail eingeben.');
      return;
    }
    setLoading(true);
    clearMessages();
    try {
      const msg = await forgotPassword(email);
      setSuccess(msg);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Zurücksetzen');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg-page px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <img src="/eduhu_logo_transparent.svg" alt="eduhu" className="h-14 mb-3" />
          <p className="mt-1 text-sm text-text-secondary">
            Dein KI-Assistent im Lehrerzimmer
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-4 flex rounded-lg bg-bg-subtle p-1">
          <button
            type="button"
            onClick={() => {
              setTab('login');
              setPassword('');
              clearMessages();
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              tab === 'login'
                ? 'bg-bg-card text-text-strong shadow-sm'
                : 'text-text-secondary hover:text-text-default'
            }`}
          >
            Anmelden
          </button>
          <button
            type="button"
            onClick={() => {
              setTab('register');
              setPassword('');
              clearMessages();
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              tab === 'register'
                ? 'bg-bg-card text-text-strong shadow-sm'
                : 'text-text-secondary hover:text-text-default'
            }`}
          >
            Registrieren
          </button>
        </div>

        {/* Success message */}
        {success && (
          <div className="mb-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
            {success}
          </div>
        )}

        {/* Login Form */}
        {tab === 'login' && (
          <form
            onSubmit={(e) => void handleLogin(e)}
            className="card space-y-4"
          >
            <div>
              <label
                htmlFor="login-email"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                E-Mail
              </label>
              <input
                id="login-email"
                type="email"
                autoFocus
                className="input"
                placeholder="deine@email.de"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
              />
            </div>
            <div>
              <label
                htmlFor="login-password"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                Passwort
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                className="input"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError('');
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
              {loading ? 'Anmelden...' : 'Anmelden →'}
            </button>
            <div className="flex items-center justify-between text-xs">
              <button
                type="button"
                onClick={() => void handleMagicLink()}
                disabled={loading}
                className="text-primary hover:underline"
              >
                Magic Link senden
              </button>
              <button
                type="button"
                onClick={() => {
                  setTab('forgot');
                  clearMessages();
                }}
                className="text-text-secondary hover:underline"
              >
                Passwort vergessen?
              </button>
            </div>
          </form>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <form
            onSubmit={(e) => void handleRegister(e)}
            className="card space-y-4"
          >
            <div>
              <label
                htmlFor="reg-name"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                Name
              </label>
              <input
                id="reg-name"
                type="text"
                autoFocus
                className="input"
                placeholder="Dein Name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
              />
            </div>
            <div>
              <label
                htmlFor="reg-email"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                E-Mail
              </label>
              <input
                id="reg-email"
                type="email"
                className="input"
                placeholder="deine@email.de"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
              />
            </div>
            <div>
              <label
                htmlFor="reg-password"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                Passwort
              </label>
              <input
                id="reg-password"
                type="password"
                autoComplete="new-password"
                className="input"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError('');
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
              {loading ? 'Registrieren...' : 'Account erstellen →'}
            </button>
          </form>
        )}

        {/* Forgot Password Form */}
        {tab === 'forgot' && (
          <form
            onSubmit={(e) => void handleForgot(e)}
            className="card space-y-4"
          >
            <p className="text-sm text-text-secondary">
              Gib deine E-Mail ein und wir senden dir einen Link zum
              Zurücksetzen.
            </p>
            <div>
              <label
                htmlFor="forgot-email"
                className="mb-1.5 block text-sm font-medium text-text-strong"
              >
                E-Mail
              </label>
              <input
                id="forgot-email"
                type="email"
                autoFocus
                className="input"
                placeholder="deine@email.de"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
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
              {loading ? 'Senden...' : 'Reset-Link senden'}
            </button>
            <button
              type="button"
              onClick={() => {
                setTab('login');
                clearMessages();
              }}
              className="w-full text-center text-xs text-text-secondary hover:underline"
            >
              ← Zurück zum Login
            </button>
          </form>
        )}

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-text-muted">
          © 2026 eduhu GmbH
        </p>
      </div>
    </div>
  );
}
