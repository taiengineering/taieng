// AI Worker — consumes 45.ai.generate for marketing scope
import { createWorker, AI_QUEUES } from '@45cm/core-queue-runtime';
import { aiGenerate } from '@45cm/core-ai-runtime';
import { insertUsageLog } from '@45cm/core-db-runtime';
import { createEvent, emitEvent, AI_EVENTS } from '@45cm/core-event-runtime';

interface AiJobPayload {
  workspace_id: string;
  engine: string;
  capability: string;
  input: string;
  context?: Record<string, unknown>;
  trace_id?: string;
  correlation_id?: string;
  callback_queue?: string;
  callback_data?: Record<string, unknown>;
}

const worker = createWorker<AiJobPayload>(AI_QUEUES.GENERATE, async (job) => {
  const d = job.data;
  console.log(`[ai-worker] job=${job.id} cap=${d.capability} trace=${d.trace_id}`);

  const res = await aiGenerate({
    workspaceId: d.workspace_id, engine: d.engine, capability: d.capability,
    input: d.input, context: d.context,
  });

  await insertUsageLog({
    workspace_id: d.workspace_id, engine: d.engine, capability: d.capability,
    provider: 'openai', model: res.model, prompt_tokens: res.usage.promptTokens,
    completion_tokens: res.usage.completionTokens, estimated_cost_usd: res.usage.estimatedCostUsd,
    latency_ms: res.latencyMs, status: 'success', trace_id: d.trace_id,
  });

  emitEvent(createEvent({
    eventType: AI_EVENTS.USAGE_RECORDED, eventVersion: 1,
    workspaceId: d.workspace_id, engine: d.engine, source: 'marketing-ai-worker',
    capability: d.capability, payload: { model: res.model, cost: res.usage.estimatedCostUsd },
  }));

  console.log(`[ai-worker] done job=${job.id} model=${res.model} cost=$${res.usage.estimatedCostUsd}`);
});

worker.on('ready', () => console.log(`[ai-worker] ${AI_QUEUES.GENERATE} ready`));
console.log('AI Worker started.');
