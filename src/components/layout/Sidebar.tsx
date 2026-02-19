import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getSession, clearSession } from '@/lib/auth';
import { getConversations } from '@/lib/api';
import type { Conversation } from '@/lib/types';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', label: 'Home', icon: 'fa-solid fa-house' },
  { path: '/workspace', label: 'Arbeitsbereich', icon: 'fa-solid fa-layer-group' },
  { path: '/material', label: 'Material', icon: 'fa-solid fa-pen-fancy' },
  { path: '/library', label: 'Bibliothek', icon: 'fa-solid fa-folder-open' },
];

interface Props {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: Props) {
  const location = useLocation();
  const navigate = useNavigate();
  const teacher = getSession();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    void getConversations().then((c) => setConversations(c.slice(0, 5)));
  }, [location.pathname]);

  function handleLogout() {
    clearSession();
    void navigate('/');
  }

  return (
    <nav
      className="flex flex-col border-r border-border/30 bg-bg-card transition-all duration-300 ease-[cubic-bezier(0.25,0.8,0.25,1)]"
      style={{ width: collapsed ? 'var(--sidebar-collapsed-w)' : 'var(--sidebar-w)', minWidth: collapsed ? 'var(--sidebar-collapsed-w)' : 'var(--sidebar-w)' }}
    >
      <div className="relative flex flex-col h-full px-5 py-7" style={{ padding: collapsed ? '30px 12px' : undefined }}>
        {/* Toggle Button */}
        <button
          type="button"
          onClick={onToggle}
          className="absolute top-7 right-4 flex h-7 w-7 items-center justify-center rounded-full bg-bg-page text-text-secondary transition-colors hover:bg-primary hover:text-white"
          style={collapsed ? { right: '26px', transform: 'rotate(180deg)' } : undefined}
        >
          <i className="fa-solid fa-chevron-left text-xs" />
        </button>

        {/* Logo */}
        <button
          type="button"
          onClick={() => void navigate('/dashboard')}
          className="mb-10 flex items-center gap-3 overflow-hidden bg-transparent border-none cursor-pointer"
          style={collapsed ? { paddingLeft: 0, justifyContent: 'center' } : { paddingLeft: '10px' }}
        >
          {collapsed ? (
            <img src="/Eduhu_Eule_Kopf.svg" alt="eduhu" className="h-8 w-8 shrink-0" />
          ) : (
            <img src="/eduhu_logo_transparent.svg" alt="eduhu" className="h-9" />
          )}
        </button>

        {/* Main Navigation */}
        <div className="flex flex-1 flex-col gap-2 overflow-y-auto" style={{ scrollbarWidth: 'none' }}>
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                type="button"
                onClick={() => void navigate(item.path)}
                className={`flex items-center gap-3.5 rounded-[var(--radius-btn)] px-4 py-3.5 text-[15px] font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-primary text-white shadow-[0_4px_12px_rgba(245,104,61,0.25)]'
                    : 'text-text-secondary hover:bg-bg-page hover:text-text-strong'
                }`}
                style={collapsed ? { justifyContent: 'center', padding: '14px 0' } : undefined}
              >
                <i className={`${item.icon} w-6 text-center text-lg shrink-0`} />
                {!collapsed && <span>{item.label}</span>}
              </button>
            );
          })}

          {/* Recent Conversations Section */}
          {!collapsed && conversations.length > 0 && (
            <>
              <div className="mx-3 mt-6 mb-3 text-[11px] font-bold uppercase tracking-wider text-text-secondary">
                Letzte Gespräche
              </div>
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  type="button"
                  onClick={() => void navigate(`/workspace?c=${conv.id}`)}
                  className="flex items-center gap-3.5 rounded-[var(--radius-btn)] px-4 py-3.5 text-sm font-medium text-text-secondary transition-all hover:bg-bg-page hover:text-text-strong"
                >
                  <i className="fa-regular fa-comment w-6 text-center text-base shrink-0" />
                  <span className="truncate">{conv.title || 'Neues Gespräch'}</span>
                </button>
              ))}
            </>
          )}
        </div>

        {/* Bottom: Logout */}
        {teacher && !collapsed && (
          <button
            type="button"
            onClick={handleLogout}
            className="mt-4 flex items-center gap-3.5 rounded-[var(--radius-btn)] px-4 py-3 text-sm font-medium text-text-secondary transition-colors hover:bg-bg-page hover:text-error"
          >
            <i className="fa-solid fa-right-from-bracket w-6 text-center" />
            <span>Abmelden</span>
          </button>
        )}
        {teacher && collapsed && (
          <button
            type="button"
            onClick={handleLogout}
            className="mt-4 flex items-center justify-center rounded-[var(--radius-btn)] py-3 text-text-secondary transition-colors hover:bg-bg-page hover:text-error"
            title="Abmelden"
          >
            <i className="fa-solid fa-right-from-bracket text-center" />
          </button>
        )}
      </div>
    </nav>
  );
}
