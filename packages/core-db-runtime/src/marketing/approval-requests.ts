import { mkt } from '../client';

export interface InsertApproval {
  workspace_id: string;
  draft_id: string;
  transport?: string;
  requested_by?: string;
  external_message_id?: string;
  expires_at?: string;
}

export async function insertApprovalRequest(data: InsertApproval) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await mkt().from('approval_requests').insert({ ...data, transport: data.transport ?? 'slack', status: 'pending' }).select().single();
  if (error) throw new Error(`insertApproval: ${error.message}`);
  return row;
}

export async function updateApprovalStatus(id: string, status: 'approved' | 'rejected' | 'expired' | 'cancelled', approvedBy?: string, reason?: string) {
  const { data, error } = await mkt().from('approval_requests').update({ status, approved_by: approvedBy, reason, updated_at: new Date().toISOString() }).eq('id', id).select().single();
  if (error) throw new Error(`updateApproval: ${error.message}`);
  return data;
}

export async function getApprovalByDraftId(draftId: string) {
  const { data, error } = await mkt().from('approval_requests').select('*').eq('draft_id', draftId).order('created_at', { ascending: false }).limit(1).single();
  if (error) throw new Error(`getApproval: ${error.message}`);
  return data;
}
