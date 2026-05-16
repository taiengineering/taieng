import { Queue, type QueueOptions } from 'bullmq';
import { getRedisConnection } from './connection';

const queues = new Map<string, Queue>();

export function getQueue<T = unknown>(name: string, opts?: Partial<QueueOptions>): Queue<T> {
  if (queues.has(name)) return queues.get(name)! as Queue<T>;
  const q = new Queue<T>(name, {
    connection: getRedisConnection(),
    defaultJobOptions: {
      attempts: 3,
      backoff: { type: 'exponential', delay: 30_000 },
      removeOnComplete: { count: 1000 },
      removeOnFail: { count: 5000 },
    },
    ...opts,
  });
  queues.set(name, q as unknown as Queue);
  return q;
}

export async function enqueue<T>(queueNameStr: string, jobName: string, data: T & { workspace_id: string; trace_id?: string; correlation_id?: string }): Promise<string> {
  if (!data.workspace_id) throw new Error('workspace_id is required for all queue jobs');
  const q = getQueue<T>(queueNameStr);
  const job = await q.add(jobName, data, { jobId: undefined });
  return job.id ?? '';
}
