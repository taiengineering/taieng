// 45cm Marketing Worker
// Consumes: 45.marketing.draft, 45.marketing.humanize
// RFC-002 Queue Contract compliant
// Workers MUST be idempotent

import { MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { aiRuntime } from '@45cm/core-ai-runtime';
import { createEvent, emitEvent, MARKETING_EVENTS } from '@45cm/core-event-runtime';

// ─── Draft Consumer Placeholder ───

async function processDraftJob(payload: {
  workspaceId: string;
  contentId?: string;
  channelId?: string;
  input: string;
}) {
  console.log(`[Worker] Processing draft job for workspace: ${payload.workspaceId}`);

  // Call AI Runtime (never call provider directly)
  const result = await aiRuntime.generate({
    workspaceId: payload.workspaceId,
    engine: 'marketing',
    capability: 'marketing.generate_draft',
    input: payload.input,
  });

  console.log(`[Worker] Draft generated: ${result.requestId}`);

  // Emit event per RFC-001
  const event = createEvent({
    eventType: MARKETING_EVENTS.DRAFT_GENERATED,
    eventVersion: 1,
    workspaceId: payload.workspaceId,
    engine: 'marketing',
    source: 'marketing-worker',
    capability: 'draft',
    payload: {
      requestId: result.requestId,
      output: result.output,
      model: result.model,
    },
  });
  emitEvent(event);

  // TODO: Save draft to marketing.drafts via Supabase
  // TODO: Enqueue 45.marketing.humanize

  return result;
}

// ─── Humanize Consumer Placeholder ───

async function processHumanizeJob(payload: {
  workspaceId: string;
  draftId: string;
  body: string;
}) {
  console.log(`[Worker] Processing humanize job for draft: ${payload.draftId}`);

  const result = await aiRuntime.generate({
    workspaceId: payload.workspaceId,
    engine: 'marketing',
    capability: 'marketing.rewrite_humanize',
    input: payload.body,
  });

  console.log(`[Worker] Humanized: ${result.requestId}`);

  const event = createEvent({
    eventType: MARKETING_EVENTS.DRAFT_HUMANIZED,
    eventVersion: 1,
    workspaceId: payload.workspaceId,
    engine: 'marketing',
    source: 'marketing-worker',
    capability: 'humanize',
    payload: {
      draftId: payload.draftId,
      requestId: result.requestId,
      output: result.output,
    },
  });
  emitEvent(event);

  // TODO: Update marketing.drafts status
  // TODO: Enqueue 45.marketing.approval

  return result;
}

// ─── Worker Bootstrap ───

console.log('Marketing Worker starting...');
console.log(`Listening on queues: ${MARKETING_QUEUES.DRAFT}, ${MARKETING_QUEUES.HUMANIZE}`);

// TODO: Connect BullMQ workers to Redis
// TODO: Register processDraftJob for 45.marketing.draft
// TODO: Register processHumanizeJob for 45.marketing.humanize

export { processDraftJob, processHumanizeJob };
