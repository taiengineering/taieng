// Marketing Worker — BullMQ consumers for draft + humanize pipeline (Steps 5+8)
import { createWorker, MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { aiGenerate } from '@45cm/core-ai-runtime';
import { updateDraft, getDraftById, insertUsageLog, insertApprovalRequest } from '@45cm/core-db-runtime';
import { createEvent, emitEvent, MARKETING_EVENTS } from '@45cm/core-event-runtime';

// ====== Humanize Worker ======
interface HumanizePayload { workspace_id: string; draft_id: string; body: string; trace_id?: string; correlation_id?: string; }

const humanizeWorker = createWorker<HumanizePayload>(MARKETING_QUEUES.HUMANIZE, async (job) => {
  const { workspace_id, draft_id, body, trace_id } = job.data;
  console.log(`[humanize] job=${job.id} draft=${draft_id} trace=${trace_id}`);

  const ai = await aiGenerate({
    workspaceId: workspace_id,
    engine: 'marketing',
    capability: 'marketing.rewrite_humanize',
    input: body,
    context: {
      systemPrompt: 'Rewrite the following Korean marketing reply to sound natural, professional, and human-written. Remove any AI-generated feel. Keep the same meaning and facts. Output only the rewritten text.',
    },
  });

  // Save usage log
  await insertUsageLog({
    workspace_id, engine: 'marketing', capability: 'marketing.rewrite_humanize',
    provider: 'openai', model: ai.model, prompt_tokens: ai.usage.promptTokens,
    completion_tokens: ai.usage.completionTokens, estimated_cost_usd: ai.usage.estimatedCostUsd,
    latency_ms: ai.latencyMs, status: 'success', trace_id,
  });

  // Update draft with humanized body
  await updateDraft(draft_id, { humanized_body: ai.output, status: 'humanized' });

  // Emit event
  emitEvent(createEvent({
    eventType: MARKETING_EVENTS.DRAFT_HUMANIZED, eventVersion: 1,
    workspaceId: workspace_id, engine: 'marketing', source: 'marketing-worker',
    capability: 'humanize', payload: { draft_id, trace_id },
  }));

  console.log(`[humanize] done draft=${draft_id}`);
});

humanizeWorker.on('ready', () => console.log(`[worker] ${MARKETING_QUEUES.HUMANIZE} ready`));

console.log('Marketing Worker started.');
