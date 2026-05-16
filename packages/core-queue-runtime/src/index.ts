// 45cm Queue Runtime — RFC-002 Queue Contract compliant
// Queue naming: 45.<engine>.<capability>
// Redis namespace separation via prefix

import { v4 as uuidv4 } from 'uuid';
import type { QueueJob, Priority } from '@45cm/core-shared-types';

export type { QueueJob };

// ─── Queue Name Helper ───

export function queueName(engine: string, capability: string): string {
  return `45.${engine}.${capability}`;
}

export function dlqName(engine: string, capability: string): string {
  return `45.${engine}.${capability}.dlq`;
}

// ─── Marketing Queue Names ───

export const MARKETING_QUEUES = {
  COLLECT: queueName('marketing', 'collect'),
  CLASSIFY: queueName('marketing', 'classify'),
  DRAFT: queueName('marketing', 'draft'),
  HUMANIZE: queueName('marketing', 'humanize'),
  APPROVAL: queueName('marketing', 'approval'),
  PUBLISH: queueName('marketing', 'publish'),
  CTA_TRACK: queueName('marketing', 'cta_track'),
  ANALYTICS: queueName('marketing', 'analytics'),
} as const;

export const AI_QUEUES = {
  GENERATE: queueName('ai', 'generate'),
} as const;

// ─── Default Retry Policy ───

export const DEFAULT_RETRY_POLICY = {
  maxRetry: 3,
  backoffMs: [30_000, 120_000, 600_000], // 30s, 2m, 10m
} as const;

// ─── Job Builder ───

export function createJob<TPayload = unknown>(params: {
  queue: string;
  workspaceId: string;
  engine: string;
  capability: string;
  payload: TPayload;
  priority?: Priority;
  traceId?: string;
  correlationId?: string;
}): QueueJob<TPayload> {
  return {
    job_id: uuidv4(),
    queue: params.queue,
    workspace_id: params.workspaceId,
    engine: params.engine,
    capability: params.capability,
    priority: params.priority ?? 'P3',
    retry_count: 0,
    max_retry: DEFAULT_RETRY_POLICY.maxRetry,
    trace_id: params.traceId,
    correlation_id: params.correlationId,
    payload: params.payload,
    created_at: new Date().toISOString(),
  };
}

// ─── BullMQ Connection Placeholder ───
// TODO: Connect to shared Redis with namespace prefix
// Redis URL from env: REDIS_URL
// All marketing queues use prefix "45:marketing:"

export function getRedisConfig() {
  return {
    url: process.env.REDIS_URL ?? 'redis://localhost:6379',
    prefix: '45:',
  };
}
