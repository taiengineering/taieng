import { mkt } from '../client';

export interface InsertLead {
  workspace_id: string;
  source: string;
  source_ref_id?: string;
  contact?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export async function insertLead(data: InsertLead) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await mkt().from('leads').insert({ ...data, lead_status: 'new' }).select().single();
  if (error) throw new Error(`insertLead: ${error.message}`);
  return row;
}
