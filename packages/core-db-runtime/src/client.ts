import { createClient, type SupabaseClient } from '@supabase/supabase-js';

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

// Schema-scoped query helpers
// Return SupabaseClient to avoid non-portable inferred types
export function mkt(): SupabaseClient {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!,
    { db: { schema: 'marketing' } },
  );
}

export function coreAi(): SupabaseClient {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!,
    { db: { schema: 'core_ai' } },
  );
}
