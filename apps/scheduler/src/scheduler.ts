// 45cm Scheduler
// Triggers periodic jobs: keyword collection, analytics, etc.
// Does NOT contain business logic — only enqueues jobs

import { createJob, MARKETING_QUEUES } from '@45cm/core-queue-runtime';

// ─── Schedule Definitions ───

interface ScheduleEntry {
  name: string;
  queue: string;
  engine: string;
  capability: string;
  intervalMs: number;
  workspaceId: string;
}

// TODO: Load schedules from DB per workspace
const schedules: ScheduleEntry[] = [];

// ─── Scheduler Loop ───

function tick() {
  const now = new Date();
  console.log(`[Scheduler] Tick at ${now.toISOString()}, ${schedules.length} schedules registered`);

  for (const schedule of schedules) {
    const job = createJob({
      queue: schedule.queue,
      workspaceId: schedule.workspaceId,
      engine: schedule.engine,
      capability: schedule.capability,
      payload: { scheduledAt: now.toISOString() },
    });
    // TODO: Enqueue via BullMQ
    console.log(`[Scheduler] Job enqueued: ${job.job_id} → ${job.queue}`);
  }
}

// ─── Bootstrap ───

console.log('Scheduler starting...');

// TODO: Connect to Redis
// TODO: Load workspace schedules from Supabase
// TODO: Start interval timer (e.g., every 5 minutes for collection)

export { tick, schedules };
