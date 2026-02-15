import { useEffect, useRef, useState } from 'react';

interface H5PPlayerProps {
  exerciseId: string;
}

export function H5PPlayer({ exerciseId }: H5PPlayerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(400);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'h5p-resize' && event.data.height) {
        setHeight(Math.max(event.data.height + 20, 300));
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Use the dedicated player.html page — same origin, no about:blank issues
  const playerUrl = `/h5p-player/player.html?id=${exerciseId}`;

  return (
    <iframe
      ref={iframeRef}
      src={playerUrl}
      style={{
        width: '100%',
        height: `${height}px`,
        border: 'none',
        borderRadius: '12px',
        backgroundColor: 'white',
      }}
      title="H5P Exercise"
    />
  );
}
