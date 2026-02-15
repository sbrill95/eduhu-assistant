import { useState } from 'react';

interface ImageCardProps {
  image: string; // data:mime;base64,... URI
  session_id: string;
}

export function ImageCard({ image, session_id }: ImageCardProps) {
  const [fullscreen, setFullscreen] = useState(false);

  function downloadImage() {
    const link = document.createElement('a');
    link.href = image;
    link.download = `eduhu-bild-${session_id}.png`;
    link.click();
  }

  async function shareImage() {
    try {
      const resp = await fetch(image);
      const blob = await resp.blob();
      const file = new File([blob], `eduhu-bild-${session_id}.png`, { type: blob.type });
      
      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: 'eduhu Bild' });
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.write([
          new ClipboardItem({ [blob.type]: blob }),
        ]);
        alert('Bild in Zwischenablage kopiert!');
      }
    } catch {
      downloadImage(); // Fallback to download
    }
  }

  return (
    <>
      <div className="my-2 max-w-[340px] overflow-hidden rounded-xl border border-[#D9D3CD] bg-white text-sm shadow-sm">
        <div
          className="cursor-pointer"
          onClick={() => setFullscreen(true)}
          title="Vollbild anzeigen"
        >
          <img src={image} alt="Generiertes Bild" className="w-full" />
        </div>
        <div className="flex items-center justify-between border-t border-[#D9D3CD] bg-[#F5F0EB] px-3 py-2">
          <span className="text-xs text-[#6B6360]">🎨 KI-Bild</span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={shareImage}
              className="rounded-full bg-[#C8552D] px-2.5 py-1 text-xs font-medium text-white hover:bg-[#A8461F]"
            >
              📤 Teilen
            </button>
            <button
              type="button"
              onClick={downloadImage}
              className="rounded-full border border-[#D9D3CD] bg-white px-2.5 py-1 text-xs font-medium text-[#3A3530] hover:bg-[#F5F0EB]"
            >
              ⬇ Download
            </button>
          </div>
        </div>
      </div>

      {/* Fullscreen overlay */}
      {fullscreen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setFullscreen(false)}
        >
          <img
            src={image}
            alt="Generiertes Bild (Vollbild)"
            className="max-h-[90vh] max-w-[90vw] rounded-lg shadow-2xl"
          />
          <button
            type="button"
            className="absolute right-4 top-4 rounded-full bg-white/20 px-3 py-1 text-white hover:bg-white/40"
            onClick={() => setFullscreen(false)}
          >
            ✕
          </button>
        </div>
      )}
    </>
  );
}
