import { useState } from 'react';

interface ClarificationCardProps {
  question: string;
  options: string[];
  session_id?: string;
  onSelect: (answer: string) => void;
}

export function ClarificationCard({ question: _question, options, onSelect }: ClarificationCardProps) {
  void _question; // Used for display in markdown above the card
  const [selected, setSelected] = useState<string | null>(null);
  const [customText, setCustomText] = useState('');
  const [showCustom, setShowCustom] = useState(false);

  const handleSelect = (option: string) => {
    // Last option is always the "custom" escape
    const isLastOption = option === options[options.length - 1];
    if (isLastOption && (option.toLowerCase().includes('andere') || option.toLowerCase().includes('eigene'))) {
      setShowCustom(true);
      return;
    }
    setSelected(option);
    onSelect(option);
  };

  const handleCustomSubmit = () => {
    if (customText.trim()) {
      setSelected(customText);
      onSelect(customText);
    }
  };

  if (selected) {
    return (
      <div className="bg-white rounded-xl p-4 border border-[var(--color-primary)]/20 my-2">
        <p className="text-sm text-[var(--color-text-secondary)] mb-1">Deine Auswahl:</p>
        <p className="font-medium text-[var(--color-text)]">✅ {selected}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-4 border border-[var(--color-primary)]/20 my-2 max-w-md">
      <div className="flex flex-col gap-2">
        {options.map((option, i) => (
          <button
            key={i}
            onClick={() => handleSelect(option)}
            className="text-left px-4 py-3 rounded-lg border border-[var(--color-border)] 
                       hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/5
                       transition-all duration-150 text-sm font-medium
                       active:scale-[0.98]"
          >
            {option}
          </button>
        ))}
      </div>

      {showCustom && (
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCustomSubmit()}
            placeholder="Deine Angabe..."
            className="flex-1 px-3 py-2 rounded-lg border border-[var(--color-border)] text-sm
                       focus:outline-none focus:border-[var(--color-primary)]"
            autoFocus
          />
          <button
            onClick={handleCustomSubmit}
            className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg text-sm
                       hover:opacity-90 transition-opacity"
          >
            OK
          </button>
        </div>
      )}
    </div>
  );
}
