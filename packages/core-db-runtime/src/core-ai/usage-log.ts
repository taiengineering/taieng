import { coreAi } from '../client';

export interface InsertUsageLog {
  workspace_id: string;
  engine: string;
  capability: string;
  provider: string;
  model: string;
  prompt_key?: string;
  prompt_tokens: number;
  completion_tokens: number;
  estimated_cost_usd: number;
  latency_ms: number;
  status: string;
  trace_id?: string;
  correlation_id?: string;
}

export async function insertUsageLog(data: InsertUsageLog) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await coreAi().from('ai_usage_log').insert(data).select().single();
  if (error) throw new Error(`insertUsageLog: ${error.message}`);
  return row;
}
