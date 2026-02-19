import { useState, useEffect } from 'react';

interface TypingIndicatorProps {
  /** Optional hint about what was asked — used to pick relevant step messages */
  context?: string;
}

const COLD_START_DELAY = 6000;
const STEP_INTERVAL = 4000;

const DEFAULT_STEPS = [
  'Nachricht wird verarbeitet…',
  'Erinnerungen werden durchsucht…',
  'Antwort wird formuliert…',
];

const MATERIAL_STEPS = [
  'Anforderungen werden analysiert…',
  'Lehrplan wird berücksichtigt…',
  'Material wird zusammengestellt…',
  'Aufgaben werden formuliert…',
  'Erwartungshorizont wird erstellt…',
];

const KLAUSUR_STEPS = [
  'Thema wird analysiert…',
  'AFB-Verteilung wird geplant…',
  'Aufgaben werden erstellt…',
  'Erwartungshorizont wird geschrieben…',
  'Klassenarbeit wird finalisiert…',
];

const H5P_STEPS = [
  'Übungstyp wird ausgewählt…',
  'Fragen werden generiert…',
  'Interaktive Übung wird erstellt…',
  'Übungsseite wird vorbereitet…',
];

function pickSteps(context?: string): string[] {
  if (!context) return DEFAULT_STEPS;
  const c = context.toLowerCase();
  if (c.includes('klausur') || c.includes('klassenarbeit') || c.includes('prüfung')) return KLAUSUR_STEPS;
  if (c.includes('material') || c.includes('arbeitsblatt') || c.includes('differenz')) return MATERIAL_STEPS;
  if (c.includes('übung') || c.includes('h5p') || c.includes('quiz') || c.includes('interaktiv')) return H5P_STEPS;
  return DEFAULT_STEPS;
}

export function TypingIndicator({ context }: TypingIndicatorProps) {
  const [stepIndex, setStepIndex] = useState(-1);
  const steps = pickSteps(context);

  useEffect(() => {
    // Show first step after cold-start delay
    const initial = setTimeout(() => setStepIndex(0), COLD_START_DELAY);
    return () => clearTimeout(initial);
  }, []);

  useEffect(() => {
    if (stepIndex < 0 || stepIndex >= steps.length - 1) return;
    const timer = setTimeout(() => setStepIndex((i) => i + 1), STEP_INTERVAL);
    return () => clearTimeout(timer);
  }, [stepIndex, steps.length]);

  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white border border-border">
        <img src="/Eduhu_Eule_Kopf.svg" alt="" className="h-5 w-5" />
      </div>
      <div className="rounded-[var(--radius-card)] bg-bg-card px-4 py-3 shadow-card">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="inline-block h-2 w-2 rounded-full bg-primary"
                style={{
                  animation: 'pulse-dot 1.2s ease-in-out infinite',
                  animationDelay: `${i * 0.2}s`,
                }}
              />
            ))}
          </div>
          <span
            className="text-sm font-medium text-text-secondary transition-opacity duration-500"
            style={{ opacity: stepIndex >= 0 ? 1 : 0 }}
          >
            {stepIndex >= 0 ? steps[stepIndex] : ''}
          </span>
        </div>
      </div>
    </div>
  );
}
