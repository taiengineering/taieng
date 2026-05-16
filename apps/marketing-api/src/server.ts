import Fastify from 'fastify';
import { v4 as uuid } from 'uuid';
import { enqueue, MARKETING_QUEUES } from '@45cm/core-queue-runtime';
import { aiGenerate } from '@45cm/core-ai-runtime';
import { insertDraft, updateDraft, getDraftById, insertApprovalRequest, updateApprovalStatus, insertContent, insertAnalyticsEvent, insertLead, insertUsageLog } from '@45cm/core-db-runtime';
import { collect } from '@45cm/channel-naver-kin';

const app = Fastify({ logger: true });

// ====== Health ======
app.get('/health', async () => ({ status: 'healthy', engine: 'marketing-engine', version: '0.1.0', ts: new Date().toISOString() }));

// ====== Draft Generate (Step 2+5) ======
interface DraftBody { workspaceId: string; input: string; contentId?: string; channelId?: string; }

app.post<{ Body: DraftBody }>('/draft/generate', async (req, reply) => {
  const { workspaceId, input, contentId, channelId } = req.body;
  if (!workspaceId || !input) return reply.status(400).send({ error: 'workspaceId and input required' });
  const traceId = uuid();

  // 1. AI generate
  const ai = await aiGenerate({ workspaceId, engine: 'marketing', capability: 'marketing.generate_draft', input });

  // 2. Save usage log
  const usageLog = await insertUsageLog({
    workspace_id: workspaceId, engine: 'marketing', capability: 'marketing.generate_draft',
    provider: 'openai', model: ai.model, prompt_tokens: ai.usage.promptTokens,
    completion_tokens: ai.usage.completionTokens, estimated_cost_usd: ai.usage.estimatedCostUsd,
    latency_ms: ai.latencyMs, status: 'success', trace_id: traceId,
  });

  // 3. Save draft
  const draft = await insertDraft({
    workspace_id: workspaceId, source_content_id: contentId, channel_id: channelId,
    draft_type: 'reply', body: ai.output, ai_usage_log_id: usageLog.id,
    metadata: { trace_id: traceId },
  });

  // 4. Enqueue humanize
  await enqueue(MARKETING_QUEUES.HUMANIZE, 'humanize', {
    workspace_id: workspaceId, draft_id: draft.id, body: ai.output, trace_id: traceId, correlation_id: traceId,
  });

  return reply.status(201).send({ draft_id: draft.id, trace_id: traceId, model: ai.model, cost_usd: ai.usage.estimatedCostUsd });
});

// ====== Collect Keywords (Step 4) ======
interface CollectBody { workspaceId: string; keyword: string; maxResults?: number; }

app.post<{ Body: CollectBody }>('/collect', async (req, reply) => {
  const { workspaceId, keyword, maxResults } = req.body;
  if (!workspaceId || !keyword) return reply.status(400).send({ error: 'workspaceId and keyword required' });

  const items = await collect({ workspaceId, keyword, maxResults });
  const saved = [];
  for (const item of items) {
    const row = await insertContent({
      workspace_id: workspaceId, source: item.source, external_id: item.externalId,
      content_type: 'question', title: item.title, body: item.body, url: item.url,
      raw_payload: item.rawPayload, collected_at: item.collectedAt,
    });
    saved.push(row);
  }
  return reply.send({ keyword, collected: saved.length, contents: saved });
});

// ====== Slack Approval Callback (Step 6) ======
app.post('/approval/callback', async (req, reply) => {
  const payload = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body as any)?.payload ? JSON.parse((req.body as any).payload) : req.body;
  const action = payload?.actions?.[0];
  if (!action) return reply.status(400).send({ error: 'no action' });

  const [command, approvalId] = (action.value ?? '').split(':');
  if (!approvalId) return reply.status(400).send({ error: 'invalid action value' });

  const userId = payload?.user?.id ?? 'unknown';
  if (command === 'approve') {
    await updateApprovalStatus(approvalId, 'approved', userId);
  } else if (command === 'reject') {
    await updateApprovalStatus(approvalId, 'rejected', userId);
  }
  return reply.send({ text: `Action ${command} applied.` });
});

// ====== Request Approval (Step 6) ======
interface ApprovalBody { workspaceId: string; draftId: string; }

app.post<{ Body: ApprovalBody }>('/approval/request', async (req, reply) => {
  const { workspaceId, draftId } = req.body;
  if (!workspaceId || !draftId) return reply.status(400).send({ error: 'workspaceId and draftId required' });

  const draft = await getDraftById(draftId);
  await updateDraft(draftId, { status: 'pending_approval' });

  // Slack Block Kit message
  const slackToken = process.env.SLACK_BOT_TOKEN;
  const slackChannel = process.env.SLACK_CHANNEL_ID;
  if (!slackToken || !slackChannel) return reply.status(500).send({ error: 'Slack not configured' });

  const approval = await insertApprovalRequest({ workspace_id: workspaceId, draft_id: draftId });

  const body = (draft as any).humanized_body ?? (draft as any).body ?? '';
  const preview = body.length > 300 ? body.slice(0, 300) + '...' : body;

  await fetch('https://slack.com/api/chat.postMessage', {
    method: 'POST',
    headers: { Authorization: `Bearer ${slackToken}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      channel: slackChannel,
      text: `Draft approval request: ${draftId}`,
      blocks: [
        { type: 'header', text: { type: 'plain_text', text: '\ud83d\udcdd Draft Approval Request' } },
        { type: 'section', text: { type: 'mrkdwn', text: `*Draft ID:* ${draftId}\n*Type:* ${(draft as any).draft_type}` } },
        { type: 'section', text: { type: 'mrkdwn', text: `\`\`\`${preview}\`\`\`` } },
        { type: 'actions', elements: [
          { type: 'button', text: { type: 'plain_text', text: '\u2705 Approve' }, style: 'primary', action_id: 'approve_draft', value: `approve:${approval.id}` },
          { type: 'button', text: { type: 'plain_text', text: '\u274c Reject' }, style: 'danger', action_id: 'reject_draft', value: `reject:${approval.id}` },
        ] },
      ],
    }),
  });

  return reply.send({ approval_id: approval.id, status: 'pending', slack_sent: true });
});

// ====== CTA Tracking (Step 7) ======
app.get<{ Params: { ctaId: string }; Querystring: { ws?: string; ref?: string } }>('/c/:ctaId', async (req, reply) => {
  const { ctaId } = req.params;
  const ws = req.query.ws ?? 'unknown';
  const ref = req.query.ref;

  // Record analytics event
  await insertAnalyticsEvent({
    workspace_id: ws, event_type: 'cta.clicked',
    subject_type: 'cta', subject_id: ctaId,
    metadata: { referer: ref, ip: req.ip, ua: req.headers['user-agent'] },
  });

  // Optional lead creation
  if (ref) {
    await insertLead({ workspace_id: ws, source: 'cta_click', source_ref_id: ctaId, metadata: { ref } });
  }

  // Redirect to target (TAI default: free diagnosis)
  const targetUrl = `https://taieng.co.kr/diagnosis?utm_source=45cm&utm_medium=cta&utm_campaign=${ctaId}`;
  return reply.redirect(302, targetUrl);
});

// ====== Start ======
const start = async () => {
  const port = parseInt(process.env.PORT ?? '3100', 10);
  await app.listen({ port, host: '0.0.0.0' });
};
start();
