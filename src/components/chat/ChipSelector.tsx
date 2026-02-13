import type { Chip } from '@/lib/types';

interface Props {
  chips: Chip[];
  onSelect: (chip: Chip) => void;
}

export function ChipSelector({ chips, onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {chips.map((chip) => (
        <button
          key={chip.id}
          type="button"
          onClick={() => onSelect(chip)}
          className="rounded-[var(--radius-btn)] border-[1.5px] border-border bg-bg-card px-4 py-2 text-sm font-medium text-text-strong transition-all hover:border-primary hover:bg-primary-soft"
        >
          {chip.icon && <span className="mr-1.5">{chip.icon}</span>}
          {chip.label}
        </button>
      ))}
    </div>
  );
}
