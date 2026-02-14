import type { Teacher } from './types';

const STORAGE_KEY = 'eduhu_teacher';

export function getSession(): Teacher | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Teacher;
  } catch {
    return null;
  }
}

export function setSession(teacher: Teacher): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(teacher));
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export async function login(password: string): Promise<Teacher> {
  const apiUrl = import.meta.env.VITE_API_URL as string | undefined;
  const baseUrl = apiUrl ?? 'https://eduhu-assistant.onrender.com';
  
  const res = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({})) as Record<string, string>;
    throw new Error(data['error'] ?? 'Login fehlgeschlagen');
  }

  const teacher = await res.json() as Teacher;
  setSession(teacher);
  return teacher;
}
