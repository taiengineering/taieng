import { Worker, Job, type WorkerOptions } from 'bullmq';
import { getRedisConnection } from './connection';
import { dlqName } from './constants';
import { getQueue } from './create-queue';

export type JobProcessor<T> = (job: Job<T>) => Promise<void>;

export function createWorker<T>(
  queueNameStr: string,
  processor: JobProcessor<T>,
  opts?: Partial<WorkerOptions>,
): Worker<T> {
  const worker = new Worker<T>(
    queueNameStr,
    async (job) => {
      try {
        await processor(job);
      } catch (err) {
        if (job.attemptsMade >= (job.opts.attempts ?? 3)) {
          const dlq = getQueue(dlqName(queueNameStr.split('.')[1] ?? 'unknown', queueNameStr.split('.')[2] ?? 'unknown'));
          await dlq.add('dlq', { originalJob: job.data, error: String(err), failedAt: new Date().toISOString() } as any);
        }
        throw err;
      }
    },
    {
      connection: getRedisConnection(),
      concurrency: 3,
      ...opts,
    },
  );
  worker.on('failed', (job, err) => {
    console.error(`[Worker:${queueNameStr}] Job ${job?.id} failed: ${err.message}`);
  });
  return worker;
}
