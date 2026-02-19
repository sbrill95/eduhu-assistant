/**
 * Debug logger – aktivierbar per VITE_DEBUG=true in .env
 *
 * Usage:
 *   import { log } from '@/lib/logger';
 *   log.info('chat', 'message sent', { conversationId });
 *   log.time('stream');
 *   log.timeEnd('stream');
 */

const ENABLED = import.meta.env.VITE_DEBUG === 'true';

const PREFIX = '[eduhu]';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const COLORS: Record<LogLevel, string> = {
  debug: 'color:#8B8B8B',
  info:  'color:#2563EB',
  warn:  'color:#D97706',
  error: 'color:#DC2626',
};

function fmt(level: LogLevel, tag: string, msg: string, ...args: unknown[]) {
  if (!ENABLED) return;
  const fn = level === 'error' ? console.error : level === 'warn' ? console.warn : console.log;
  fn(`%c${PREFIX} %c[${level.toUpperCase()}]%c [${tag}] ${msg}`, 'color:#6D28D9;font-weight:bold', COLORS[level], 'color:inherit', ...args);
}

export const log = {
  debug: (tag: string, msg: string, ...args: unknown[]) => fmt('debug', tag, msg, ...args),
  info:  (tag: string, msg: string, ...args: unknown[]) => fmt('info',  tag, msg, ...args),
  warn:  (tag: string, msg: string, ...args: unknown[]) => fmt('warn',  tag, msg, ...args),
  error: (tag: string, msg: string, ...args: unknown[]) => fmt('error', tag, msg, ...args),
  time:  (label: string) => { if (ENABLED) console.time(`${PREFIX} ${label}`); },
  timeEnd: (label: string) => { if (ENABLED) console.timeEnd(`${PREFIX} ${label}`); },
};
