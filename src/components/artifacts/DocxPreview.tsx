import { useState, useEffect } from 'react';
import mammoth from 'mammoth';
import { getSession } from '@/lib/auth';
import { API_BASE } from '@/lib/api';

interface Props {
  url: string;
}

export function DocxPreview({ url }: Props) {
  const [html, setHtml] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const teacher = getSession();
    const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
    fetch(fullUrl, {
      headers: teacher ? { Authorization: `Bearer ${teacher.access_token}` } : {},
    })
      .then(res => {
        if (!res.ok) throw new Error('Download fehlgeschlagen');
        return res.arrayBuffer();
      })
      .then(buf => mammoth.convertToHtml({ arrayBuffer: buf }))
      .then(result => {
        setHtml(result.value);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [url]);

  if (loading)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  if (error)
    return (
      <div className="p-6 text-center text-red-500">
        Vorschau nicht verfügbar: {error}
      </div>
    );

  return (
    <div className="bg-white p-8 shadow-lg max-w-[600px] mx-auto min-h-[400px]">
      <div
        className="prose prose-sm max-w-none"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}
