import { useEffect, useRef } from 'react';

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

interface H5PPlayerProps {
  exerciseId: string;
}

export function H5PPlayer({ exerciseId }: H5PPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    initializedRef.current = true;

    const el = containerRef.current;
    const options = {
      h5pJsonPath: `${API_BASE}/api/public/h5p/${exerciseId}`,
      frameJs: '/h5p-player/frame.bundle.js',
      frameCss: '/h5p-player/styles/h5p.css',
      librariesPath: '/h5p-libs',
      frame: true,
      copyright: false,
      export: false,
      icon: false,
      fullScreen: false,
    };

    import('h5p-standalone').then(({ H5P }) => {
      new H5P(el, options);
    }).catch((err) => {
      console.error('H5P Player error:', err);
      el.innerHTML = '<p style="color:red;padding:20px;">H5P Player konnte nicht geladen werden.</p>';
    });

    return () => {
      initializedRef.current = false;
    };
  }, [exerciseId]);

  return (
    <div
      ref={containerRef}
      style={{ minHeight: '300px', backgroundColor: 'white', borderRadius: '12px', overflow: 'hidden' }}
    />
  );
}
