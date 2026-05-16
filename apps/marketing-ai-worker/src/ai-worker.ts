// 45cm Marketing AI Worker
// Dedicated worker for AI-heavy operations
// Consumes: 45.ai.generate (marketing scope)
// All AI calls go through 45 AI Runtime — NO direct provider calls

import { AI_QUEUES } from '@45cm/core-queue-runtime';
import { aiRuntime } from '@45cm/core-ai-runtime';
import { createEvent, emitEvent, AI_EVENTS } from '@45cm/core-event-runtime';
import type { AiGenerateRequest } from '@45cm/core-shared-types';

async function processAiJob(request: AiGenerateRequest) {
  console.log(`[AI-Worker] Processing AI job: engine=${request.engine}, capability=${request.capability}`);

  const result = await aiRuntime.generate(request);

  // Emit AI usage event
  const event = createEvent({
    eventType: AI_EVENTS.USAGE_RECORDED,
    eventVersion: 1,
    workspaceId: request.workspaceId,
    engine: request.engine,
    source: 'marketing-ai-worker',
    capability: request.capability,
    payload: {
      requestId: result.requestId,
      model: result.model,
      promptTokens: result.usage.promptTokens,
      completionTokens: result.usage.completionTokens,
      estimatedCostUsd: result.usage.estimatedCostUsd,
      latencyMs: result.latencyMs,
    },
  });
  emitEvent(event);

  return result;
}

// ─── AI Worker Bootstrap ───

console.log('Marketing AI Worker starting...');
console.log(`Listening on queue: ${AI_QUEUES.GENERATE}`);

// TODO: Connect BullMQ worker to Redis
// TODO: Register processAiJob for 45.ai.generate
// TODO: Filter by engine='marketing' scope

export { processAiJob };
