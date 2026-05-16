// Marketing Collector — Periodic keyword collection (Step 4)
import { collect } from '@45cm/channel-naver-kin';
import { enqueue, MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { insertContent } from '@45cm/core-db-runtime';
import { createEvent, emitEvent, MARKETING_EVENTS } from '@45cm/core-event-runtime';
import { v4 as uuid } from 'uuid';

const DEFAULT_KEYWORDS = [
  '\uc911\ub300\uc7ac\ud574\ucc98\ubc8c\ubc95', '\uc0b0\uc5c5\uc548\uc804\ubcf4\uac74\ubc95', '\uc548\uc804\uad00\ub9ac\uc790 \uc120\uc784',
  '\uacfc\ud0dc\ub8cc \uae30\uc900', '\uc704\ud5d8\uc131\ud3c9\uac00',
];

async function runCollection(workspaceId: string, keywords: string[]) {
  console.log(`[collector] workspace=${workspaceId} keywords=${keywords.length}`);

  for (const keyword of keywords) {
    try {
      const items = await collect({ workspaceId, keyword, maxResults: 5 });
      if (items.length === 0) continue;

      const traceId = uuid();
      emitEvent(createEvent({
        eventType: MARKETING_EVENTS.KEYWORD_DETECTED, eventVersion: 1,
        workspaceId, engine: 'marketing', source: 'channel-naver-kin',
        capability: 'collect', payload: { keyword, count: items.length }, traceId,
      }));

      for (const item of items) {
        const content = await insertContent({
          workspace_id: workspaceId, source: item.source, external_id: item.externalId,
          content_type: 'question', title: item.title, body: item.body, url: item.url,
          raw_payload: item.rawPayload, collected_at: item.collectedAt,
        });

        await enqueue(MARKETING_QUEUES.CLASSIFY, 'classify', {
          workspace_id: workspaceId, content_id: content.id,
          title: item.title, body: item.body, keyword, trace_id: traceId,
        });
      }
      console.log(`[collector] keyword="${keyword}" collected=${items.length}`);
    } catch (err) {
      console.error(`[collector] keyword="${keyword}" error:`, err);
    }
  }
}

// One-shot run (scheduler will call this periodically)
const ws = process.env.DEFAULT_WORKSPACE_ID ?? '00000000-0000-0000-0000-000000000000';
runCollection(ws, DEFAULT_KEYWORDS).then(() => {
  console.log('[collector] done');
  // Keep alive for scheduler or exit
  if (process.env.COLLECTOR_MODE !== 'daemon') process.exit(0);
});

export { runCollection };
