import { createClient, type SupabaseClient } from '@supabase/supabase-js';

let sb: SupabaseClient | null = null;

export function supabase(): SupabaseClient {
  if (!sb) {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_KEY;
    if (!url || !key) throw new Error('SUPABASE_URL and SUPABASE_SERVICE_KEY required');
    sb = createClient(url, key);
  }
  return sb;
}

let mktClient: any = null;
let aiClient: any = null;

export function mkt(): any {
  if (!mktClient) {
    mktClient = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!,
      { db: { schema: 'marketing' } },
    );
  }
  return mktClient;
}

export function coreAi(): any {
  if (!aiClient) {
    aiClient = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!,
      { db: { schema: 'core_ai' } },
    );
  }
  return aiClient;
}
