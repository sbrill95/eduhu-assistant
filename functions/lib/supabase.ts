/**
 * Minimal Supabase REST client — zero dependencies, pure fetch.
 */

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_ROLE_KEY: string;
  ANTHROPIC_API_KEY: string;
}

function headers(key: string, extra?: Record<string, string>): Record<string, string> {
  return {
    'apikey': key,
    'Authorization': `Bearer ${key}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
    ...extra,
  };
}

type Row = Record<string, unknown>;

export interface QueryResult<T = Row> {
  data: T | null;
  error: unknown;
}

export function getSupabase(env: Env) {
  const base = env.SUPABASE_URL.replace(/\/$/, '');
  const key = env.SUPABASE_SERVICE_ROLE_KEY;

  return {
    /** SELECT rows */
    async select<T = Row[]>(
      table: string,
      opts?: {
        columns?: string;
        filters?: Record<string, string>;
        order?: { col: string; asc?: boolean };
        limit?: number;
        single?: boolean;
      },
    ): Promise<QueryResult<T>> {
      const params = new URLSearchParams();
      params.set('select', opts?.columns ?? '*');
      if (opts?.filters) {
        for (const [col, val] of Object.entries(opts.filters)) {
          params.set(col, `eq.${val}`);
        }
      }
      if (opts?.order) {
        params.set('order', `${opts.order.col}.${opts.order.asc === false ? 'desc' : 'asc'}`);
      }
      if (opts?.limit) {
        params.set('limit', String(opts.limit));
      }

      const hdrs = opts?.single
        ? headers(key, { 'Accept': 'application/vnd.pgrst.object+json' })
        : headers(key);

      const res = await fetch(`${base}/rest/v1/${table}?${params}`, { headers: hdrs });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        return { data: null, error: err };
      }
      return { data: (await res.json()) as T, error: null };
    },

    /** INSERT rows */
    async insert<T = Row[]>(table: string, data: unknown): Promise<QueryResult<T>> {
      const res = await fetch(`${base}/rest/v1/${table}`, {
        method: 'POST',
        headers: headers(key),
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        return { data: null, error: err };
      }
      return { data: (await res.json()) as T, error: null };
    },

    /** UPSERT rows */
    async upsert<T = Row[]>(
      table: string,
      data: unknown,
      onConflict?: string,
    ): Promise<QueryResult<T>> {
      let url = `${base}/rest/v1/${table}`;
      if (onConflict) url += `?on_conflict=${onConflict}`;

      const res = await fetch(url, {
        method: 'POST',
        headers: headers(key, { 'Prefer': 'resolution=merge-duplicates,return=representation' }),
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        return { data: null, error: err };
      }
      return { data: (await res.json()) as T, error: null };
    },
  };
}

export type SupabaseDB = ReturnType<typeof getSupabase>;

// JSON response helpers
export function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export function error(message: string, status = 400): Response {
  return json({ error: message }, status);
}
