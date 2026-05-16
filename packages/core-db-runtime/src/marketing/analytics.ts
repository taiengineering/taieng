import { mkt } from '../client';

export interface InsertAnalyticsEvent {
  workspace_id: string;
  event_type: string;
  subject_type?: string;
  subject_id?: string;
  metadata?: Record<string, unknown>;
}

export async function insertAnalyticsEvent(data: InsertAnalyticsEvent) {
  if (!data.workspace_id) throw new Error('workspace_id required');
  const { data: row, error } = await mkt().from('analytics_events').insert(data).select().single();
  if (error) throw new Error(`insertAnalytics: ${error.message}`);
  return row;
}
