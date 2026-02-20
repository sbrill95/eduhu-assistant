import type { Teacher } from './types';

const STORAGE_KEY = 'eduhu_teacher';
const API = (import.meta.env.VITE_API_URL as string | undefined) ?? '';

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

export async function login(email: string, password: string): Promise<Teacher> {
  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Login fehlgeschlagen');
  }
  const teacher = (await res.json()) as Teacher;
  setSession(teacher);
  return teacher;
}

export async function register(
  email: string,
  password: string,
  name: string,
): Promise<string> {
  const res = await fetch(`${API}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Registrierung fehlgeschlagen');
  }
  const data = (await res.json()) as { message: string };
  return data.message;
}

export async function requestMagicLink(email: string): Promise<string> {
  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, request_magic_link: true }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Magic Link fehlgeschlagen');
  }
  const data = (await res.json()) as { message: string };
  return data.message;
}

export async function forgotPassword(email: string): Promise<string> {
  const res = await fetch(`${API}/api/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  const data = (await res.json()) as { message: string };
  return data.message;
}

export async function resetPassword(
  token: string,
  newPassword: string,
): Promise<string> {
  const res = await fetch(`${API}/api/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Passwort-Reset fehlgeschlagen');
  }
  const data = (await res.json()) as { message: string };
  return data.message;
}

export async function verifyEmail(token: string): Promise<string> {
  const res = await fetch(`${API}/api/auth/verify/${token}`);
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Verifizierung fehlgeschlagen');
  }
  const data = (await res.json()) as { message: string };
  return data.message;
}

export function isDemoUser(): boolean {
  const session = getSession();
  return session?.role === 'demo';
}

export async function checkDemoEnabled(): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/auth/demo-status`);
    if (!res.ok) return false;
    const data = (await res.json()) as { demo_enabled: boolean };
    return data.demo_enabled;
  } catch {
    return false;
  }
}

export async function startDemo(): Promise<Teacher> {
  const res = await fetch(`${API}/api/auth/demo-start`, { method: 'POST' });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Demo konnte nicht gestartet werden');
  }
  const teacher = (await res.json()) as Teacher;
  setSession(teacher);
  return teacher;
}

export async function requestDemoUpgrade(data: {
  email: string;
  survey_useful?: string;
  survey_material?: string;
  survey_recommend?: string;
  survey_feedback?: string;
}): Promise<string> {
  const session = getSession();
  if (!session) throw new Error('Nicht angemeldet');

  const res = await fetch(`${API}/api/auth/demo-upgrade`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(err['detail'] ?? 'Upgrade fehlgeschlagen');
  }
  const result = (await res.json()) as { message: string };
  return result.message;
}

export async function completeDemoUpgrade(
  token: string,
  password: string,
  name: string,
): Promise<Teacher> {
  const res = await fetch(`${API}/api/auth/demo-upgrade/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, password, name }),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(err['detail'] ?? 'Aktivierung fehlgeschlagen');
  }
  const teacher = (await res.json()) as Teacher;
  setSession(teacher);
  return teacher;
}

export async function inviteColleagues(emails: string[]): Promise<{ sent: number; total: number }> {
  const session = getSession();
  if (!session) throw new Error('Nicht angemeldet');

  const res = await fetch(`${API}/api/auth/invite-colleagues`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(emails),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(err['detail'] ?? 'Einladung fehlgeschlagen');
  }
  return (await res.json()) as { sent: number; total: number };
}

export async function magicLogin(token: string): Promise<Teacher> {
  const res = await fetch(`${API}/api/auth/magic-login?token=${token}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as Record<string, string>;
    throw new Error(data['detail'] ?? 'Magic Login fehlgeschlagen');
  }
  const teacher = (await res.json()) as Teacher;
  setSession(teacher);
  return teacher;
}
