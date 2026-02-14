import { getSession, clearSession } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export function Header() {
  const teacher = getSession();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    clearSession();
    void navigate('/');
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-bg-card px-4 sm:h-16">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <span className="text-2xl">🦉</span>
        <span className="text-lg font-bold text-text-strong">eduhu</span>
      </div>

      {/* Right side */}
      {teacher && (
        <div className="relative">
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-2 rounded-[var(--radius-btn)] px-3 py-1.5 text-sm text-text-secondary transition-colors hover:bg-bg-subtle"
          >
            {teacher.name}
            <span className="text-lg">☰</span>
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full z-20 mt-1 w-48 rounded-[var(--radius-card)] bg-bg-card py-1 shadow-elevated">
                <button
                  type="button"
                  onClick={() => { setMenuOpen(false); void navigate('/chat'); }}
                  className="w-full px-4 py-2 text-left text-sm text-text-default hover:bg-bg-subtle"
                >
                  💬 Neuer Chat
                </button>
                <button
                  type="button"
                  onClick={() => { setMenuOpen(false); void navigate('/curriculum'); }}
                  className="w-full px-4 py-2 text-left text-sm text-text-default hover:bg-bg-subtle"
                >
                  📚 Lehrpläne
                </button>
                <button
                  type="button"
                  onClick={() => { setMenuOpen(false); handleLogout(); }}
                  className="w-full px-4 py-2 text-left text-sm text-error hover:bg-bg-subtle"
                >
                  🚪 Abmelden
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  );
}
