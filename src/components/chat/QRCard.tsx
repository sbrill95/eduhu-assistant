interface QRCardProps {
  title: string;
  code: string;
  url: string;
  qr_url: string;
  count: number;
}

export function QRCard({ title, code, url, qr_url, count }: QRCardProps) {
  return (
    <div className="max-w-[300px] rounded-[var(--radius-card)] bg-bg-card p-4 text-sm shadow-card">
      <h3 className="mb-3 text-left font-bold text-text-strong">🎯 {title}</h3>
      <div className="text-center">
        <img src={qr_url} alt="QR Code" className="mx-auto my-4 inline-block" />
        <p className="font-bold text-lg text-text-strong">Code: {code}</p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 mb-4 block break-words text-primary hover:underline"
        >
          {url}
        </a>
        <p className="text-xs text-text-muted">{count} Aufgaben</p>
      </div>
    </div>
  );
}
