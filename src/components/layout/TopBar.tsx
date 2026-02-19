import { useLocation, useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';

const TITLES: Record<string, string> = {
  '/dashboard': 'Übersicht',
  '/workspace': 'Arbeitsbereich',
  '/material': 'Material erstellen',
  '/library': 'Bibliothek',
  '/profile': 'Einstellungen',
};

export function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const teacher = getSession();

  const title = TITLES[location.pathname] || 'eduhu';
  const initial = teacher?.name?.charAt(0)?.toUpperCase() || 'U';

  return (
    <header
      className="flex shrink-0 items-center justify-between px-10 mt-2.5"
      style={{ height: 'var(--header-h)' }}
    >
      <h1 className="text-[22px] font-bold tracking-tight text-text-strong">
        {title}
      </h1>

      <div className="flex items-center gap-5">
        <button
          type="button"
          onClick={() => void navigate('/profile')}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-text-strong text-white font-bold shadow-soft transition-transform hover:scale-105 hover:shadow-elevated"
        >
          {initial}
        </button>
      </div>
    </header>
  );
}
