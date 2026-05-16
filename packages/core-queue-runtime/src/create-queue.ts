import { Queue, type QueueOptions } from 'bullmq';
import { getRedisConnection } from './connection';

const queues = new Map<string, Queue>();

export function getQueue(name: string, opts?: Partial<QueueOptions>): Queue {
  if (queues.has(name)) return queues.get(name)!;
  const q = new Queue(name, {
    connection: getRedisConnection(),
    defaultJobOptions: {
      attempts: 3,
      backoff: { type: 'exponential', delay: 30_000 },
      removeOnComplete: { count: 1000 },
      removeOnFail: { count: 5000 },
    },
    ...opts,
  });
  queues.set(name, q);
  return q;
}

export async function enqueue(
  queueNameStr: string,
  jobName: string,
  data: Record<string, unknown> & { workspace_id: string; trace_id?: string; correlation_id?: string },
): Promise<string> {
  if (!data.workspace_id) throw new Error('workspace_id is required for all queue jobs');
  const q = getQueue(queueNameStr);
  const job = await q.add(jobName, data);
  return job.id ?? '';
}
