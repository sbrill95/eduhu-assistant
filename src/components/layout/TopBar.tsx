import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getSession, isDemoUser } from '@/lib/auth';
import { ExitSurvey } from '@/components/ExitSurvey';

const TITLES: Record<string, string> = {
  '/dashboard': 'Übersicht',
  '/workspace': 'Arbeitsbereich',
  '/material': 'Material erstellen',
  '/library': 'Bibliothek',
  '/profile': 'Einstellungen',
};

interface Props {
  onMenuToggle?: () => void;
}

export function TopBar({ onMenuToggle }: Props) {
  const location = useLocation();
  const navigate = useNavigate();
  const teacher = getSession();
  const [showExitSurvey, setShowExitSurvey] = useState(false);
  const isDemo = isDemoUser();

  const title = TITLES[location.pathname] || 'eduhu';
  const initial = teacher?.name?.charAt(0)?.toUpperCase() || 'U';

  return (
    <header
      className="flex shrink-0 items-center justify-between px-4 md:px-10 mt-2.5"
      style={{ height: 'var(--header-h)' }}
    >
      <div className="flex items-center gap-3">
        {onMenuToggle && (
          <button
            type="button"
            onClick={onMenuToggle}
            className="flex md:hidden h-10 w-10 items-center justify-center rounded-xl text-text-strong transition-colors hover:bg-bg-subtle"
          >
            <i className="fa-solid fa-bars text-lg" />
          </button>
        )}
        <h1 className="text-lg md:text-[22px] font-bold tracking-tight text-text-strong">
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {isDemo && (
          <button
            type="button"
            onClick={() => setShowExitSurvey(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-100 text-amber-800 hover:bg-amber-200 transition-colors"
          >
            🎯 Demo beenden
          </button>
        )}
        <button
          type="button"
          onClick={() => void navigate('/profile')}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-text-strong text-white font-bold shadow-soft transition-transform hover:scale-105 hover:shadow-elevated"
        >
          {initial}
        </button>
      </div>

      {showExitSurvey && (
        <ExitSurvey
          onClose={() => setShowExitSurvey(false)}
          onUpgrade={(email) => {
            // TODO: call demo-upgrade endpoint
            console.log('Upgrade to:', email);
            setShowExitSurvey(false);
          }}
        />
      )}
    </header>
  );
}
