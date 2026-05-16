// 45cm Marketing API — Fastify-based minimal API server
// Sprint 001: GET /health + POST /draft/generate

import Fastify from 'fastify';
import { createJob, MARKETING_QUEUES } from '@45cm/core-queue-runtime';

const app = Fastify({ logger: true });

// ─── GET /health ───

app.get('/health', async () => {
  return {
    status: 'healthy',
    engine: 'marketing-engine',
    version: '0.0.1',
    timestamp: new Date().toISOString(),
  };
});

// ─── POST /draft/generate ───
// Sprint 001: Enqueue draft generation job (mock)

interface DraftGenerateBody {
  workspaceId: string;
  contentId?: string;
  channelId?: string;
  input: string;
}

app.post<{ Body: DraftGenerateBody }>('/draft/generate', async (request, reply) => {
  const { workspaceId, contentId, channelId, input } = request.body;

  if (!workspaceId || !input) {
    return reply.status(400).send({ error: 'workspaceId and input are required' });
  }

  // Create queue job per RFC-002
  const job = createJob({
    queue: MARKETING_QUEUES.DRAFT,
    workspaceId,
    engine: 'marketing',
    capability: 'draft',
    payload: { contentId, channelId, input },
  });

  // TODO: Enqueue via BullMQ
  // For now, return job as confirmation
  return reply.status(202).send({
    message: 'Draft generation job queued',
    job_id: job.job_id,
    queue: job.queue,
    created_at: job.created_at,
  });
});

// ─── Start Server ───

const start = async () => {
  try {
    const port = parseInt(process.env.PORT ?? '3100', 10);
    await app.listen({ port, host: '0.0.0.0' });
    console.log(`Marketing API running on port ${port}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
