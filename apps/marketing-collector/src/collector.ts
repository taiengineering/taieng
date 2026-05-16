// 45cm Marketing Collector
// Collects external content via Channel Adapters
// RFC-006: Adapter MUST NOT call AI directly

import { naverKinAdapter } from '@45cm/channel-naver-kin';
import { createJob, MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { createEvent, emitEvent, MARKETING_EVENTS } from '@45cm/core-event-runtime';

async function collectFromNaverKin(workspaceId: string, keywords: string[]) {
  console.log(`[Collector] Starting Naver Kin collection for workspace: ${workspaceId}`);

  for (const keyword of keywords) {
    const contents = await naverKinAdapter.collect({
      workspaceId,
      keyword,
      maxResults: 10,
    });

    if (contents.length > 0) {
      // Emit keyword detected event
      const event = createEvent({
        eventType: MARKETING_EVENTS.KEYWORD_DETECTED,
        eventVersion: 1,
        workspaceId,
        engine: 'marketing',
        source: 'channel-naver-kin',
        capability: 'collect',
        payload: { keyword, count: contents.length },
      });
      emitEvent(event);

      // Enqueue classify job for each content
      for (const content of contents) {
        const job = createJob({
          queue: MARKETING_QUEUES.CLASSIFY,
          workspaceId,
          engine: 'marketing',
          capability: 'classify',
          payload: {
            externalId: content.externalId,
            title: content.title,
            body: content.body,
            url: content.url,
            keyword,
          },
        });
        // TODO: Enqueue via BullMQ
        console.log(`[Collector] Classify job created: ${job.job_id}`);
      }
    }

    // TODO: Save to marketing.contents via Supabase
  }
}

// ─── Collector Bootstrap ───

console.log('Marketing Collector starting...');

// TODO: Load keywords from workspace config + domain pack
// TODO: Schedule periodic collection via scheduler app
// TODO: Connect to BullMQ for job enqueueing

export { collectFromNaverKin };
