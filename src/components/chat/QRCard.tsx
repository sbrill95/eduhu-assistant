interface QRCardProps {
  title: string;
  code: string;
  url: string;
  qr_url: string;
  count: number;
}

export function QRCard({ title, code, url, qr_url, count }: QRCardProps) {
  return (
    <div className="my-2 max-w-[300px] overflow-hidden rounded-xl border border-[var(--color-sky)]/40 bg-[var(--color-sky-soft)] text-sm shadow-sm">
      <div className="bg-[var(--color-sky)]/30 px-4 py-2.5">
        <h3 className="text-base font-bold text-[var(--color-text-strong)]">🎯 {title}</h3>
      </div>
      <div className="flex flex-col items-center px-4 py-3">
        <img src={qr_url} alt="QR Code" className="h-36 w-36 rounded-lg border border-white shadow-sm" />
        <div className="mt-3 rounded-lg bg-white/60 px-4 py-2 text-center">
          <p className="text-xs text-[var(--color-text-secondary)]">Zugangscode</p>
          <p className="font-mono text-xl font-bold tracking-wider text-[var(--color-primary)]">{code}</p>
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 text-xs text-[var(--color-primary)] hover:underline break-all"
        >
          {url}
        </a>
      </div>
      <div className="border-t border-[var(--color-sky)]/30 bg-[var(--color-sky)]/15 px-4 py-2 text-center">
        <span className="text-xs font-medium text-[var(--color-text-secondary)]">
          {count} Aufgabe{count !== 1 ? 'n' : ''}
        </span>
      </div>
    </div>
  );
}
