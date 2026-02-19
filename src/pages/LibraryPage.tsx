import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';

const FOLDERS = [
  { name: 'Mathe 8a', files: 12, iconBg: '#FFF9E0', iconColor: '#FFC107', icon: 'fa-regular fa-folder' },
  { name: 'Mathe 8b', files: 8, iconBg: '#FFF9E0', iconColor: '#FFC107', icon: 'fa-regular fa-folder' },
  { name: 'Englisch 13 LK', files: 24, iconBg: '#FFF0EB', iconColor: '#f5683d', icon: 'fa-regular fa-folder-open' },
  { name: 'Admin & Vorlagen', files: null, sub: 'System', iconBg: '#FFF0EB', iconColor: '#f5683d', icon: 'fa-regular fa-folder-open' },
];

const FILTER_TAGS = ['Organisation', 'Schüler:innensessions', 'Reflexion', 'Inspiration'];

const RECENT_FILES = [
  { title: 'Reflexion: Mathe 8a (Unruhe)', date: 'Heute • 08:45 Uhr', iconBg: '#E8F5E9', iconColor: '#34C759' },
  { title: 'Ideenfindung: Sommerfest Rede', date: 'Gestern • 14:20 Uhr', iconBg: '#EBF4FF', iconColor: '#4A90E2' },
  { title: 'Analyse: Notenschnitt 10c', date: 'Mo. 06. Okt • 16:00 Uhr', iconBg: '#FFF5F2', iconColor: '#f5683d' },
];

export default function LibraryPage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const [search, setSearch] = useState('');
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  function toggleFilter(tag: string) {
    setActiveFilters((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  }

  if (!teacher) return null;

  return (
    <AppShell>
      {/* Header with search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <h1 className="text-2xl font-bold text-text-strong">Bibliothek</h1>
        <div className="flex items-center gap-2.5 bg-bg-card rounded-full px-5 py-2.5 shadow-soft w-full sm:w-80">
          <i className="fa-solid fa-magnifying-glass text-text-secondary" />
          <input
            type="text"
            placeholder="Suche..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-sm font-medium text-text-strong"
          />
          <span className="text-text-secondary opacity-50 text-xs hidden sm:inline">Ctrl+K</span>
        </div>
      </div>

      {/* Folders */}
      <h3 className="text-[13px] font-bold uppercase text-text-secondary tracking-wider mb-3">
        Ordner
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3 sm:gap-4 mb-8">
        {FOLDERS.map((folder) => (
          <div
            key={folder.name}
            className="flex flex-col items-center justify-center gap-2.5 rounded-[var(--radius-card)] bg-bg-card p-5 shadow-soft cursor-pointer text-center transition-all hover:-translate-y-1 hover:shadow-elevated"
          >
            <div
              className="flex items-center justify-center w-12 h-12 rounded-[var(--radius-btn)] text-xl mb-1"
              style={{ backgroundColor: folder.iconBg, color: folder.iconColor }}
            >
              <i className={folder.icon} />
            </div>
            <div className="font-bold text-[13px] text-text-strong">{folder.name}</div>
            <div className="text-[11px] text-text-secondary">
              {folder.sub || `${folder.files} Dateien`}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Materials */}
      <h3 className="text-[13px] font-bold uppercase text-text-secondary tracking-wider mb-3">
        Letzte Materialien
      </h3>

      {/* Filter Tags */}
      <div className="flex gap-2.5 mb-5 overflow-x-auto pb-1" style={{ scrollbarWidth: 'none' }}>
        {FILTER_TAGS.map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={() => toggleFilter(tag)}
            className={`px-4 py-2 rounded-full text-[13px] font-semibold whitespace-nowrap border transition-all ${
              activeFilters.has(tag)
                ? 'bg-text-strong text-white border-text-strong'
                : 'bg-bg-card text-text-secondary border-border hover:bg-bg-page hover:text-text-strong hover:border-text-secondary'
            }`}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* File List */}
      <div className="flex flex-col gap-2.5">
        {RECENT_FILES.map((file) => (
          <div
            key={file.title}
            className="flex items-center justify-between bg-bg-card rounded-[var(--radius-btn)] px-5 py-3.5 shadow-soft cursor-pointer transition-all hover:translate-x-1 hover:bg-[#fdfdfd]"
          >
            <div className="flex items-center gap-3.5">
              <div
                className="flex items-center justify-center w-9 h-9 rounded-lg"
                style={{ backgroundColor: file.iconBg, color: file.iconColor }}
              >
                <i className="fa-regular fa-comments" />
              </div>
              <div>
                <div className="text-sm font-semibold text-text-strong">{file.title}</div>
                <div className="text-xs text-text-secondary">{file.date}</div>
              </div>
            </div>
            <i className="fa-solid fa-chevron-right text-text-secondary text-xs" />
          </div>
        ))}
      </div>
    </AppShell>
  );
}
