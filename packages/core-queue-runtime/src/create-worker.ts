import { Worker, Job, type WorkerOptions } from 'bullmq';
import { getRedisConnection } from './connection';
import { dlqName } from './constants';
import { getQueue } from './create-queue';

export type JobProcessor<T = Record<string, unknown>> = (job: Job<T>) => Promise<void>;

export function createWorker<T = Record<string, unknown>>(
  queueNameStr: string,
  processor: JobProcessor<T>,
  opts?: Partial<WorkerOptions>,
): Worker {
  const parts = queueNameStr.replace('45.', '').split('.');
  const engine = parts[0] ?? 'unknown';
  const capability = parts[1] ?? 'unknown';

  const worker = new Worker(
    queueNameStr,
    async (job: Job) => {
      try {
        await processor(job as unknown as Job<T>);
      } catch (err) {
        if (job.attemptsMade >= (job.opts?.attempts ?? 3)) {
          try {
            const dlq = getQueue(dlqName(engine, capability));
            await dlq.add('dlq', {
              originalJob: job.data,
              error: String(err),
              failedAt: new Date().toISOString(),
            });
          } catch (_) { /* DLQ enqueue failure is non-fatal */ }
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
    console.error(JSON.stringify({ level: 'error', msg: 'job.failed', queue: queueNameStr, job_id: job?.id, error: err.message }));
  });
  return worker;
}
