// 45cm Platform — Core Shared Types
// RFC-001 Event Envelope + RFC-002 Queue Contract + RFC-003 Engine Interface

// ─── Priority & Severity ───

export type Priority = 'P1' | 'P2' | 'P3' | 'P4';
export type Severity = 'INFO' | 'WARNING' | 'CRITICAL';
export type EventStatus = 'created' | 'queued' | 'processing' | 'completed' | 'failed' | 'ignored';

// ─── RFC-001: Platform Event Envelope ───

export interface PlatformEvent<TPayload = unknown, TContext = unknown> {
  event_id: string;
  event_type: string;
  event_version: number;

  workspace_id: string;
  tenant_id?: string;

  engine: string;
  source: string;
  capability?: string;

  trace_id?: string;
  correlation_id?: string;
  causation_id?: string;

  priority: Priority;
  severity?: Severity;
  status: EventStatus;

  payload: TPayload;
  context?: TContext;

  created_at: string;
  updated_at?: string;
}

// ─── RFC-002: Queue Job Contract ───

export interface QueueJob<TPayload = unknown> {
  job_id: string;
  queue: string;

  workspace_id: string;
  engine: string;
  capability: string;

  priority: Priority;

  retry_count: number;
  max_retry: number;

  trace_id?: string;
  correlation_id?: string;

  payload: TPayload;
  created_at: string;
}

// ─── RFC-003: Engine Manifest ───

export interface EngineManifest {
  engine: string;
  version: string;
  capabilities: string[];
  queues: string[];
  emits: string[];
  consumes: string[];
}

export type HealthStatus = 'healthy' | 'degraded' | 'maintenance' | 'failed';

// ─── RFC-004: AI Metering ───

export interface AiGenerateRequest {
  workspaceId: string;
  engine: string;
  capability: string;
  input: string;
  context?: Record<string, unknown>;
  priority?: Priority;
}

export interface AiGenerateResult {
  requestId: string;
  output: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    estimatedCostUsd: number;
  };
  latencyMs: number;
}

export interface AiUsageLog {
  id: string;
  workspace_id: string;
  engine: string;
  capability: string;
  provider: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  estimated_cost_usd: number;
  latency_ms: number;
  status: 'success' | 'error' | 'timeout';
  created_at: string;
}
