import { useState } from 'react';

interface Props {
  onComplete: () => void;
}

/**
 * Shorter, focused onboarding for demo users.
 * No profile saving — just gets them started quickly.
 */
export function DemoOnboardingModal({ onComplete }: Props) {
  const [step, setStep] = useState(0);

  const steps = [
    {
      icon: '🦉',
      title: 'Willkommen zum eduhu Demo!',
      text: 'Teste alle Features 7 Tage lang kostenlos. Erstelle Materialien, generiere Übungen und lass dich von deinem KI-Assistenten unterstützen.',
    },
    {
      icon: '📝',
      title: 'Material erstellen',
      text: 'Frag den Assistenten z.B. "Erstelle eine Klausur zum Thema Fotosynthese für Klasse 10" — er erstellt ein fertiges DOCX-Dokument.',
    },
    {
      icon: '🎯',
      title: 'Interaktive Übungen',
      text: 'Generiere H5P-Übungen, die deine Schüler:innen direkt im Browser lösen können — mit QR-Code zum Teilen.',
    },
  ];

  const current = steps[step];
  const isLast = step === steps.length - 1;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">{current?.icon}</div>
          <h2 className="text-xl font-semibold text-text-strong">{current?.title}</h2>
          <p className="text-sm text-text-muted mt-2 leading-relaxed">{current?.text}</p>
        </div>

        {/* Step indicators */}
        <div className="flex justify-center gap-2 mb-6">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-2 rounded-full transition-all ${
                i === step ? 'w-6 bg-primary' : 'w-2 bg-bg-subtle'
              }`}
            />
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={onComplete}
            className="flex-1 rounded-lg border border-gray-200 py-2.5 text-sm text-text-muted hover:bg-gray-50"
          >
            Überspringen
          </button>
          <button
            onClick={() => (isLast ? onComplete() : setStep(step + 1))}
            className="flex-1 rounded-lg bg-primary py-2.5 text-sm text-white hover:bg-primary/90"
          >
            {isLast ? 'Los geht\'s! 🚀' : 'Weiter →'}
          </button>
        </div>

        {/* Demo hint */}
        <p className="text-center text-xs text-text-muted mt-4">
          Demo-Account läuft 7 Tage. Danach kannst du upgraden.
        </p>
      </div>
    </div>
  );
}
