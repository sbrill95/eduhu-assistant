import { useEffect, useRef } from 'react';

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
      h5pJsonPath: `/api/public/h5p/${exerciseId}`,
      frameJs: '/h5p-player/frame.bundle.js',
      frameCss: '/h5p-player/styles/h5p.css',
      librariesPath: '/h5p-libs',
      frame: false,
      copyright: false,
      export: false,
      icon: false,
      fullScreen: false,
    };

    import('h5p-standalone').then(({ H5P }) => {
      new H5P(el, options).then(() => {
        // Auto-resize iframe to fit content
        const resizeIframe = () => {
          const iframe = el.querySelector('iframe.h5p-iframe') as HTMLIFrameElement;
          if (iframe?.contentDocument?.body) {
            const height = iframe.contentDocument.body.scrollHeight;
            if (height > 100) {
              iframe.style.height = `${height + 50}px`;
            }
          }
        };

        // Resize after initial load + periodically for dynamic content
        setTimeout(resizeIframe, 500);
        setTimeout(resizeIframe, 1500);
        setTimeout(resizeIframe, 3000);

        // Listen for H5P resize messages
        window.addEventListener('message', (event) => {
          if (event.data?.context === 'h5p' || event.data?.type === 'h5p') {
            setTimeout(resizeIframe, 100);
          }
        });
      });
    }).catch((err) => {
      console.error('H5P Player error:', err);
      el.innerHTML = `<p style="color:red;padding:20px;">H5P Player Fehler: ${err.message}</p>`;
    });

    return () => {
      initializedRef.current = false;
    };
  }, [exerciseId]);

  return (
    <div
      ref={containerRef}
      style={{ minHeight: '400px', backgroundColor: 'white', borderRadius: '12px', overflow: 'hidden' }}
    />
  );
}
