// Marketing Worker — BullMQ consumers for draft + humanize pipeline
// Runs as long-lived process listening on Redis queues
// Error in one job MUST NOT crash the entire worker

import { createWorker, MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { aiGenerate } from '@45cm/core-ai-runtime';
import { updateDraft, insertUsageLog } from '@45cm/core-db-runtime';
import { createEvent, emitEvent, MARKETING_EVENTS } from '@45cm/core-event-runtime';

// ====== Humanize Worker ======

interface HumanizePayload {
  workspace_id: string;
  draft_id: string;
  body: string;
  trace_id?: string;
  correlation_id?: string;
}

const humanizeWorker = createWorker<HumanizePayload>(
  MARKETING_QUEUES.HUMANIZE,
  async (job) => {
    const { workspace_id, draft_id, body, trace_id } = job.data;
    console.log(JSON.stringify({ level: 'info', msg: 'humanize.start', job_id: job.id, draft_id, trace_id, queue: MARKETING_QUEUES.HUMANIZE }));

    try {
      const ai = await aiGenerate({
        workspaceId: workspace_id,
        engine: 'marketing',
        capability: 'marketing.rewrite_humanize',
        input: body,
        context: {
          systemPrompt:
            '다음 한국어 마케팅 답변을 자연스럽고 전문적이며 사람이 직접 쓴 것처럼 다시 작성해주세요. '
            + 'AI가 생성한 느낌을 완전히 제거하세요. 의미와 사실관계는 유지하세요. '
            + '다시 작성된 텍스트만 출력하세요.',
        },
      });

      // Usage log
      await insertUsageLog({
        workspace_id,
        engine: 'marketing',
        capability: 'marketing.rewrite_humanize',
        provider: 'openai',
        model: ai.model,
        prompt_tokens: ai.usage.promptTokens,
        completion_tokens: ai.usage.completionTokens,
        estimated_cost_usd: ai.usage.estimatedCostUsd,
        latency_ms: ai.latencyMs,
        status: 'success',
        trace_id,
      });

      // Update draft
      await updateDraft(draft_id, {
        humanized_body: ai.output,
        status: 'humanized',
      });

      // Emit event
      emitEvent(
        createEvent({
          eventType: MARKETING_EVENTS.DRAFT_HUMANIZED,
          eventVersion: 1,
          workspaceId: workspace_id,
          engine: 'marketing',
          source: 'marketing-worker',
          capability: 'humanize',
          payload: { draft_id, trace_id, model: ai.model, cost_usd: ai.usage.estimatedCostUsd },
        }),
      );

      console.log(JSON.stringify({ level: 'info', msg: 'humanize.done', job_id: job.id, draft_id, model: ai.model }));
    } catch (err) {
      console.error(JSON.stringify({ level: 'error', msg: 'humanize.error', job_id: job.id, draft_id, error: String(err) }));
      throw err; // BullMQ handles retry + DLQ
    }
  },
  { concurrency: 2 },
);

humanizeWorker.on('ready', () => {
  console.log(JSON.stringify({ level: 'info', msg: 'worker.ready', queue: MARKETING_QUEUES.HUMANIZE }));
});

humanizeWorker.on('error', (err) => {
  console.error(JSON.stringify({ level: 'error', msg: 'worker.error', queue: MARKETING_QUEUES.HUMANIZE, error: String(err) }));
});

// ====== Keep process alive ======
// BullMQ worker keeps the event loop open via Redis connection.
// Add a safety interval in case of unexpected disconnect.

const keepAlive = setInterval(() => {}, 60_000);

process.on('SIGTERM', async () => {
  console.log(JSON.stringify({ level: 'info', msg: 'worker.shutdown', signal: 'SIGTERM' }));
  clearInterval(keepAlive);
  await humanizeWorker.close();
  process.exit(0);
});

console.log(JSON.stringify({ level: 'info', msg: 'marketing-worker.started', queues: [MARKETING_QUEUES.HUMANIZE] }));
