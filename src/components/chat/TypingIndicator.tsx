import { useState, useEffect } from 'react';

export function TypingIndicator() {
  const [showColdStart, setShowColdStart] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowColdStart(true), 8000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-lg">
        🦉
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
          {showColdStart && (
            <span className="text-xs text-text-muted">
              Server startet gerade… kann bis zu 60s dauern
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
