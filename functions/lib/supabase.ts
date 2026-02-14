/**
 * Lightweight Supabase client using fetch (no npm dependency).
 * Works natively in Cloudflare Workers without nodejs_compat.
 */

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_ROLE_KEY: string;
  ANTHROPIC_API_KEY: string;
}

export class SupabaseClient {
  private url: string;
  private key: string;

  constructor(url: string, key: string) {
    this.url = url.replace(/\/$/, '');
    this.key = key;
  }

  private headers(): Record<string, string> {
    return {
      'apikey': this.key,
      'Authorization': `Bearer ${this.key}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    };
  }

  async from(table: string) {
    return new QueryBuilder(this.url, this.key, table);
  }
}

class QueryBuilder {
  private url: string;
  private key: string;
  private table: string;
  private filters: string[] = [];
  private selectCols = '*';
  private orderCol = '';
  private orderAsc = true;
  private limitN = 0;
  private isSingle = false;

  constructor(url: string, key: string, table: string) {
    this.url = url.replace(/\/$/, '');
    this.key = key;
    this.table = table;
  }

  private headers(extra?: Record<string, string>): Record<string, string> {
    return {
      'apikey': this.key,
      'Authorization': `Bearer ${this.key}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
      ...extra,
    };
  }

  select(cols = '*') {
    this.selectCols = cols;
    return this;
  }

  eq(col: string, val: string) {
    this.filters.push(`${col}=eq.${val}`);
    return this;
  }

  order(col: string, opts?: { ascending?: boolean }) {
    this.orderCol = col;
    this.orderAsc = opts?.ascending ?? true;
    return this;
  }

  limit(n: number) {
    this.limitN = n;
    return this;
  }

  single() {
    this.isSingle = true;
    return this;
  }

  private buildUrl(): string {
    const params = [`select=${this.selectCols}`, ...this.filters];
    if (this.orderCol) {
      params.push(`order=${this.orderCol}.${this.orderAsc ? 'asc' : 'desc'}`);
    }
    if (this.limitN) {
      params.push(`limit=${this.limitN}`);
    }
    return `${this.url}/rest/v1/${this.table}?${params.join('&')}`;
  }

  async then(resolve: (r: { data: unknown; error: unknown }) => void) {
    try {
      const res = await fetch(this.buildUrl(), {
        headers: this.headers(this.isSingle ? { 'Accept': 'application/vnd.pgrst.object+json' } : {}),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        resolve({ data: null, error: err });
        return;
      }
      const data = await res.json();
      resolve({ data, error: null });
    } catch (e) {
      resolve({ data: null, error: e });
    }
  }

  async insert(rows: unknown | unknown[]) {
    const body = Array.isArray(rows) ? rows : [rows];
    const res = await fetch(`${this.url}/rest/v1/${this.table}`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(body.length === 1 ? body[0] : body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      return { data: null, error: err, select: () => ({ single: async () => ({ data: null, error: err }) }) };
    }
    const data = await res.json();
    const singleData = Array.isArray(data) ? data[0] : data;
    return {
      data,
      error: null,
      select: (_cols?: string) => ({
        single: async () => ({ data: singleData, error: null }),
      }),
    };
  }

  async upsert(rows: unknown | unknown[], opts?: { onConflict?: string }) {
    const body = Array.isArray(rows) ? rows : [rows];
    const headers = this.headers({
      'Prefer': 'resolution=merge-duplicates,return=representation',
    });
    let url = `${this.url}/rest/v1/${this.table}`;
    if (opts?.onConflict) {
      url += `?on_conflict=${opts.onConflict}`;
    }
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body.length === 1 ? body[0] : body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: res.statusText }));
      return { data: null, error: err };
    }
    const data = await res.json();
    return { data, error: null };
  }
}

// Factory
export function getSupabase(env: Env) {
  return {
    from(table: string) {
      return new QueryBuilder(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, table);
    },
  };
}

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
