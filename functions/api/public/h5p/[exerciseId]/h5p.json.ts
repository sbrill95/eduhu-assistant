export const onRequestGet: PagesFunction = async (context) => {
  const exerciseId = context.params.exerciseId as string;
  const apiUrl = context.env.VITE_API_URL || 'https://eduhu-assistant.onrender.com';
  const res = await fetch(`${apiUrl}/api/public/h5p/${exerciseId}/h5p.json`);
  return new Response(res.body, {
    status: res.status,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
  });
};
