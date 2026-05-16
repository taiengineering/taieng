import { mkt } from '../client';

export interface InsertContent {
  workspace_id: string;
  channel_id?: string;
  source: string;
  external_id?: string;
  content_type: string;
  title?: string;
  body?: string;
  url?: string;
  raw_payload?: Record<string, unknown>;
  collected_at?: string;
}

export async function insertContent(data: InsertContent) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await mkt().from('contents').insert(data).select().single();
  if (error) throw new Error(`insertContent: ${error.message}`);
  return row;
}

export async function getContentById(id: string) {
  const { data, error } = await mkt().from('contents').select('*').eq('id', id).single();
  if (error) throw new Error(`getContentById: ${error.message}`);
  return data;
}

export async function listContentsByWorkspace(workspaceId: string, limit = 50) {
  const { data, error } = await mkt().from('contents').select('*').eq('workspace_id', workspaceId).order('created_at', { ascending: false }).limit(limit);
  if (error) throw new Error(`listContents: ${error.message}`);
  return data ?? [];
}
