import { createClient, SupabaseClient } from '@supabase/supabase-js';

let sb: SupabaseClient | null = null;

export function supabase(): SupabaseClient {
  if (!sb) {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_KEY;
    if (!url || !key) throw new Error('SUPABASE_URL and SUPABASE_SERVICE_KEY required');
    sb = createClient(url, key, { db: { schema: 'public' } });
  }
  return sb;
}

// Direct schema query helper — Supabase JS v2 uses .schema()
export function mkt() { return supabase().schema('marketing'); }
export function coreAi() { return supabase().schema('core_ai'); }
