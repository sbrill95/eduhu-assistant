interface QRCardProps {
  title: string;
  code: string;
  url: string;
  qr_url: string;
  count: number;
}

export function QRCard({ title, code, url, qr_url, count }: QRCardProps) {
  return (
    <div className="my-2 max-w-[300px] overflow-hidden rounded-xl border border-[#D9D3CD] bg-white text-sm shadow-sm">
      <div className="bg-[#F5F0EB] px-4 py-2.5">
        <h3 className="text-base font-bold text-[#2D2018]">🎯 {title}</h3>
      </div>
      <div className="flex flex-col items-center px-4 py-3">
        <img src={qr_url} alt="QR Code" className="h-36 w-36 rounded-lg border border-white shadow-sm" />
        <div className="mt-3 rounded-lg bg-white px-4 py-2 text-center">
          <p className="text-xs text-[#6B6360]">Zugangscode</p>
          <p className="font-mono text-xl font-bold tracking-wider text-[#C8552D]">{code}</p>
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 text-xs text-[#C8552D] hover:underline break-all"
        >
          {url}
        </a>
      </div>
      <div className="border-t border-[#D9D3CD] bg-[#F5F0EB] px-4 py-2 text-center">
        <span className="text-xs font-medium text-[#6B6360]">
          {count} Aufgabe{count !== 1 ? 'n' : ''}
        </span>
      </div>
    </div>
  );
}
