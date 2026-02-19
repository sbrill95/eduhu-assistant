import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';

const TEMPLATE_CARDS = [
  {
    icon: 'fa-solid fa-paintbrush',
    iconColor: '#ff9f8a',
    title: 'Bild generieren mit Nano Banana Pro',
    desc: 'Mit dieser Vorlage kannst du Bilder mit Nano Banana Pro, dem fortschrittlichsten Modell von Google, erstellen und bearbeiten.',
    badges: [{ label: 'Beta-Funktion', beta: true }],
  },
  {
    icon: 'fa-solid fa-circle-info',
    iconColor: '#ffbfae',
    title: 'Hilfekarte erstellen',
    desc: 'Eine Vorlage zur Erstellung kompakter Hilfekarten mit Tipps, Checklisten oder Formulierungshilfen.',
    badges: [{ label: 'alle Schulformen' }, { label: 'alle Fächer' }],
  },
  {
    icon: 'fa-regular fa-circle-play',
    iconColor: '#f5683d',
    title: 'Quiz zu YouTube-Video erstellen',
    desc: 'Eine Vorlage zur Erstellung eines klassischen Quiz auf Basis eines YouTube-Videos.',
    badges: [{ label: 'alle Schulformen' }, { label: 'alle Fächer' }],
  },
  {
    icon: 'fa-solid fa-dumbbell',
    iconColor: '#ffc9ba',
    title: 'Übungsaufgaben erstellen',
    desc: 'Ein strukturiertes Arbeitsblatt zur gezielten Übung und Vertiefung fachlicher Inhalte.',
    badges: [{ label: 'Beta-Funktion', beta: true }, { label: 'Sprachen + NaWi + Mathe' }],
  },
];

const UPCOMING = [
  { time: '08:30', title: 'Mathe 8a', room: 'Raum 204' },
  { time: '10:15', title: 'Englisch 10c', room: 'Raum 102' },
];

export default function DashboardPage() {
  const navigate = useNavigate();
  const teacher = getSession();
  const chatInputRef = useRef<HTMLInputElement>(null);
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    if (!teacher) void navigate('/');
  }, [teacher, navigate]);

  function handleChatSend() {
    const val = chatInput.trim();
    if (!val) return;
    // Navigate to workspace with the message pre-filled
    void navigate(`/workspace?msg=${encodeURIComponent(val)}`);
  }

  function handleChatKeyPress(e: React.KeyboardEvent) {
    if (e.key === 'Enter') handleChatSend();
  }

  if (!teacher) return null;

  const firstName = teacher.name?.split(' ')[0] || teacher.name;

  return (
    <AppShell>
      {/* Hero Section */}
      <div className="flex items-center justify-between rounded-[var(--radius-card)] bg-bg-card p-6 shadow-soft mb-6">
        <div>
          <h1 className="text-[28px] font-bold text-text-heading mb-1">
            Hallo {firstName}!
          </h1>
          <p className="text-[15px] font-medium text-text-secondary">
            Dein Fokus heute.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">
            Deine heutigen Stunden
          </span>
          <div className="flex gap-3">
            {UPCOMING.map((evt) => (
              <div
                key={evt.time}
                className="flex items-center gap-2.5 rounded-xl bg-bg-page px-4 py-2 border border-transparent transition-all cursor-pointer hover:bg-bg-card hover:border-border hover:shadow-subtle"
              >
                <span className="text-sm font-bold text-primary bg-primary-soft px-2 py-1 rounded-md">
                  {evt.time}
                </span>
                <span className="text-sm font-semibold text-text-strong">
                  {evt.title}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dashboard Split: Templates + Chat */}
      <div className="grid grid-cols-2 gap-6 mb-8" style={{ height: '450px', minHeight: '450px' }}>
        {/* Left: Templates Grid */}
        <div className="overflow-y-auto pr-1" style={{ scrollbarWidth: 'none' }}>
          <div className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-4 pb-2">
            {TEMPLATE_CARDS.map((card) => (
              <div
                key={card.title}
                className="flex flex-col rounded-[16px] bg-bg-card p-4 shadow-soft border border-[#f5f5f5] transition-all cursor-pointer hover:-translate-y-1 hover:shadow-elevated"
                style={{ minHeight: '200px' }}
                onClick={() => void navigate('/material')}
              >
                <div className="flex justify-between items-start mb-2.5">
                  <i className={`${card.icon} text-2xl`} style={{ color: card.iconColor }} />
                  <div className="flex flex-col items-end gap-1">
                    {card.badges.map((b) => (
                      <span
                        key={b.label}
                        className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border ${
                          b.beta
                            ? 'border-primary-soft text-primary bg-primary-soft'
                            : 'border-border text-text-secondary bg-bg-card'
                        }`}
                      >
                        {b.label}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-[15px] font-bold text-text-strong mb-2 leading-snug">
                  {card.title}
                </div>
                <div className="text-xs text-text-secondary leading-relaxed mb-4 flex-1">
                  {card.desc}
                </div>
                <button className="bg-[#EBF7F6] text-[#2D6A64] border-none px-2 py-2 rounded-lg font-semibold text-xs text-center transition-colors hover:bg-[#d0efec]">
                  Material erstellen
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Chat Widget */}
        <div className="flex flex-col rounded-[var(--radius-card)] bg-bg-card shadow-soft overflow-hidden h-full">
          {/* Chat Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-bg-page">
            <div className="font-extrabold text-base italic text-text-strong">
              <i className="fa-solid fa-sparkles text-primary mr-1.5" /> Assistent
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col gap-4 p-5 overflow-y-auto">
            <div className="flex gap-3 items-end">
              <div className="flex shrink-0 items-center justify-center w-8 h-8 rounded-full bg-white border border-border">
                <img src="/Eduhu_Eule_Kopf.svg" alt="" className="h-5 w-5" />
              </div>
              <div className="max-w-[90%] px-6 py-4 rounded-[22px] text-sm leading-relaxed bg-bg-card text-text-strong border border-border" style={{ borderBottomLeftRadius: '4px' }}>
                Womit kann ich dir behilflich sein?
              </div>
            </div>
          </div>

          {/* Chat Input */}
          <div className="px-5 py-4 bg-bg-card border-t border-bg-page shrink-0">
            <div className="flex items-center bg-bg-page rounded-full px-1.5 h-12 gap-1">
              <button className="flex items-center justify-center w-9 h-9 rounded-full text-text-secondary hover:bg-white/60 transition-colors">
                <i className="fa-solid fa-plus" />
              </button>
              <input
                ref={chatInputRef}
                type="text"
                placeholder="Frage mich etwas..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={handleChatKeyPress}
                className="flex-1 bg-transparent border-none outline-none text-sm h-full pl-2"
              />
              <button className="flex items-center justify-center w-9 h-9 rounded-full text-text-secondary hover:bg-white/60 transition-colors">
                <i className="fa-solid fa-microphone" />
              </button>
              <button
                onClick={handleChatSend}
                className="flex items-center justify-center w-9 h-9 rounded-full bg-text-strong text-white transition-transform hover:scale-110 relative overflow-hidden"
                style={{ background: 'linear-gradient(135deg, #f5683d 0%, #ff8e53 100%)' }}
              >
                <i className="fa-solid fa-arrow-up text-sm" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing / Promo Section */}
      <div className="rounded-[var(--radius-card)] bg-bg-card p-10 shadow-soft text-center">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-text-heading mb-2">
            Starte jetzt mit eduhu Beta 2.0
          </h2>
          <p className="text-sm text-text-secondary max-w-xl mx-auto">
            Registriere dich jetzt und sichere dir den vollen Zugriff auf die nächste Generation des KI-gestützten Unterrichts.
          </p>
        </div>

        <div className="flex gap-6 justify-center flex-wrap">
          {/* Free Tier */}
          <div className="flex-1 max-w-[320px] border border-border rounded-[20px] p-8 text-center transition-all hover:-translate-y-1 hover:shadow-elevated">
            <div className="text-[13px] font-bold uppercase tracking-wider opacity-60 mb-4">Free</div>
            <div className="text-4xl font-extrabold text-text-heading mb-6">
              0 € <span className="text-sm font-medium text-text-secondary">/ dauerhaft</span>
            </div>
            <div className="flex flex-col gap-3 mb-8 w-full">
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-green-accent w-4 text-center" /> 3 Generierungen
              </div>
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-green-accent w-4 text-center" /> Basis-Vorlagen
              </div>
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-green-accent w-4 text-center" /> Standard Support
              </div>
            </div>
            <button className="w-full py-3.5 rounded-xl font-semibold text-sm bg-bg-subtle text-text-secondary border-none cursor-default">
              Aktueller Plan
            </button>
          </div>

          {/* Premium Tier */}
          <div className="relative flex-1 max-w-[320px] rounded-[20px] p-8 text-center text-white transition-all hover:scale-[1.03]"
            style={{ background: 'linear-gradient(145deg, #1C1C1E 0%, #2C2C2E 100%)' }}
          >
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-[11px] font-bold px-3 py-1 rounded-full">
              Empfohlen
            </span>
            <div className="text-[13px] font-bold uppercase tracking-wider opacity-60 mb-4">Premium</div>
            <div className="text-4xl font-extrabold mb-6">
              30 € <span className="text-sm font-medium text-white/60">/ Monat</span>
            </div>
            <div className="flex flex-col gap-3 mb-8 w-full">
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-[#4cd964] w-4 text-center" /> <b>Unbegrenzte</b>&nbsp;Generierungen
              </div>
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-[#4cd964] w-4 text-center" /> Alle Premium-Vorlagen
              </div>
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-[#4cd964] w-4 text-center" /> Zugriff auf Beta-Features
              </div>
              <div className="flex items-center gap-2.5 text-sm text-left">
                <i className="fa-solid fa-check text-[#4cd964] w-4 text-center" /> Priorisierter Support
              </div>
            </div>
            <button className="w-full py-3.5 rounded-xl font-semibold text-sm bg-primary text-white border-none cursor-pointer shadow-[0_4px_15px_rgba(245,104,61,0.3)] transition-all hover:bg-primary-hover hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(245,104,61,0.4)]">
              Jetzt upgraden
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
