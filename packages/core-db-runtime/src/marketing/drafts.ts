import { mkt } from '../client';

export interface InsertDraft {
  workspace_id: string;
  source_content_id?: string;
  channel_id?: string;
  draft_type: string;
  body: string;
  humanized_body?: string;
  status?: string;
  ai_usage_log_id?: string;
  metadata?: Record<string, unknown>;
}

export async function insertDraft(data: InsertDraft) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await mkt().from('drafts').insert({ ...data, status: data.status ?? 'draft' }).select().single();
  if (error) throw new Error(`insertDraft: ${error.message}`);
  return row;
}

export async function updateDraft(id: string, updates: Partial<InsertDraft> & { status?: string }) {
  const { data, error } = await mkt().from('drafts').update({ ...updates, updated_at: new Date().toISOString() }).eq('id', id).select().single();
  if (error) throw new Error(`updateDraft: ${error.message}`);
  return data;
}

export async function getDraftById(id: string) {
  const { data, error } = await mkt().from('drafts').select('*').eq('id', id).single();
  if (error) throw new Error(`getDraftById: ${error.message}`);
  return data;
}
