import { useState, useEffect, useRef } from 'react';

interface Props {
  seconds: number;
  label: string;
}

export function CountdownTimer({ seconds, label }: Props) {
  const [remaining, setRemaining] = useState(seconds);
  const [running, setRunning] = useState(true);
  const intervalRef = useRef<ReturnType<typeof setInterval>>(undefined);

  useEffect(() => {
    if (!running) return;
    intervalRef.current = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          clearInterval(intervalRef.current);
          setRunning(false);
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, [running]);

  const mins = Math.floor(remaining / 60);
  const secs = remaining % 60;
  const pct = ((seconds - remaining) / seconds) * 100;
  const done = remaining === 0;

  return (
    <div className={`my-3 rounded-xl p-4 text-center ${done ? 'bg-green-50 border-2 border-green-400' : 'bg-[#FADDD0]/50 border border-[#C8552D]/20'}`}>
      <p className="text-xs font-medium text-text-muted mb-2">⏱️ {label}</p>
      <p className={`text-4xl font-mono font-bold ${done ? 'text-green-600' : 'text-[#C8552D]'}`}>
        {done ? '✅ Fertig!' : `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`}
      </p>
      {!done && (
        <div className="mt-3 h-2 rounded-full bg-gray-200 overflow-hidden">
          <div
            className="h-full bg-[#C8552D] transition-all duration-1000 ease-linear rounded-full"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      {done && (
        <p className="text-sm text-green-600 mt-1 animate-bounce">🔔 Zeit ist um!</p>
      )}
    </div>
  );
}
