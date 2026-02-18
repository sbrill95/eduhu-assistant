import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { verifyEmail } from '../lib/auth';

export default function VerifyPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Verifizierung läuft...');
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setMessage('Ungültiger Verifizierungslink.');
      setIsError(true);
      return;
    }
    void verifyEmail(token)
      .then((msg) => {
        setMessage(msg);
        setTimeout(() => void navigate('/'), 3000);
      })
      .catch((err) => {
        setMessage(
          err instanceof Error ? err.message : 'Verifizierung fehlgeschlagen',
        );
        setIsError(true);
      });
  }, [searchParams, navigate]);

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg-page px-4">
      <div className="w-full max-w-sm text-center">
        <div className="mb-4 text-5xl">🦉</div>
        <div className={`card p-6 ${isError ? 'border-error' : ''}`}>
          <p
            className={`text-sm ${
              isError ? 'text-error' : 'text-text-default'
            }`}
          >
            {message}
          </p>
          {!isError && (
            <p className="mt-2 text-xs text-text-secondary">
              Du wirst gleich weitergeleitet...
            </p>
          )}
        </div>
        <button
          onClick={() => void navigate('/')}
          className="mt-4 text-sm text-primary hover:underline"
        >
          Zum Login
        </button>
      </div>
    </div>
  );
}
