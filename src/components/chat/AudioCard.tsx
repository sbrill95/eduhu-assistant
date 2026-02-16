import { useState, useRef } from 'react';

interface Props {
  url: string;
  title?: string;
}

export function AudioCard({ url, title }: Props) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleEnded = () => setIsPlaying(false);

  const apiBase = import.meta.env.VITE_API_URL || '';
  const fullUrl = url.startsWith('http') ? url : `${apiBase}${url}`;

  return (
    <div className="my-2 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      {title && (
        <div className="mb-2 text-sm font-medium text-gray-700">🎙️ {title}</div>
      )}
      <div className="flex items-center gap-3">
        <button
          onClick={togglePlay}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:bg-primary/90 transition"
        >
          {isPlaying ? '⏸' : '▶️'}
        </button>
        <audio
          ref={audioRef}
          src={fullUrl}
          onEnded={handleEnded}
          onPause={() => setIsPlaying(false)}
          onPlay={() => setIsPlaying(true)}
          className="w-full"
          controls
        />
      </div>
      <div className="mt-2 flex gap-2">
        <a
          href={fullUrl}
          download
          className="text-xs text-gray-500 hover:text-primary transition"
        >
          📥 Download
        </a>
      </div>
    </div>
  );
}
