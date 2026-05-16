// 45cm Event Runtime — RFC-001 Event Envelope compliant
// Naming: <engine>.<domain>.<action>
// All events MUST have workspace_id and event_version

import { v4 as uuidv4 } from 'uuid';
import type { PlatformEvent, Priority, Severity, EventStatus } from '@45cm/core-shared-types';

export type { PlatformEvent };

// ─── Event Builder ───

export function createEvent<TPayload = unknown, TContext = unknown>(params: {
  eventType: string;
  eventVersion: number;
  workspaceId: string;
  engine: string;
  source: string;
  capability?: string;
  payload: TPayload;
  context?: TContext;
  priority?: Priority;
  severity?: Severity;
  traceId?: string;
  correlationId?: string;
  causationId?: string;
}): PlatformEvent<TPayload, TContext> {
  if (!params.workspaceId) throw new Error('workspace_id is required for all events');
  if (!params.eventVersion) throw new Error('event_version is required for all events');

  return {
    event_id: uuidv4(),
    event_type: params.eventType,
    event_version: params.eventVersion,
    workspace_id: params.workspaceId,
    engine: params.engine,
    source: params.source,
    capability: params.capability,
    trace_id: params.traceId,
    correlation_id: params.correlationId,
    causation_id: params.causationId,
    priority: params.priority ?? 'P3',
    severity: params.severity,
    status: 'created',
    payload: params.payload,
    context: params.context,
    created_at: new Date().toISOString(),
  };
}

// ─── Marketing Event Types ───

export const MARKETING_EVENTS = {
  KEYWORD_DETECTED: 'marketing.keyword.detected',
  CONTENT_COLLECTED: 'marketing.content.collected',
  INTENT_CLASSIFIED: 'marketing.intent.classified',
  DRAFT_GENERATED: 'marketing.draft.generated',
  DRAFT_HUMANIZED: 'marketing.draft.humanized',
  APPROVAL_REQUESTED: 'marketing.approval.requested',
  APPROVAL_COMPLETED: 'marketing.approval.completed',
  PUBLISH_EXECUTED: 'marketing.publish.executed',
  CTA_CLICKED: 'marketing.cta.clicked',
  LEAD_CREATED: 'marketing.lead.created',
  CONVERSION_RECORDED: 'marketing.conversion.recorded',
} as const;

export const AI_EVENTS = {
  USAGE_RECORDED: 'ai.usage.recorded',
} as const;

// ─── Event Emitter Placeholder ───
// TODO: Persist events to Supabase or event store
// TODO: Pub/sub via Redis or Supabase Realtime

const eventBuffer: PlatformEvent[] = [];

export function emitEvent(event: PlatformEvent): void {
  eventBuffer.push(event);
  // TODO: persist + broadcast
}

export function getEventBuffer(): PlatformEvent[] {
  return [...eventBuffer];
}
