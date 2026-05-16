import { v4 as uuid } from 'uuid';
import { openaiGenerate } from './providers/openai';
import type { AiGenerateRequest, AiGenerateResult } from '@45cm/core-shared-types';

const CAPABILITY_MODEL: Record<string, string> = {
  'marketing.generate_draft': 'gpt-4o-mini',
  'marketing.rewrite_humanize': 'gpt-4o-mini',
  'marketing.classify_intent': 'gpt-4o-mini',
};

const COST_PER_1K: Record<string, { input: number; output: number }> = {
  'gpt-4o-mini': { input: 0.00015, output: 0.0006 },
  'gpt-4o':      { input: 0.0025,  output: 0.01 },
};

export async function aiGenerate(req: AiGenerateRequest): Promise<AiGenerateResult & { providerRequestId: string }> {
  if (!req.workspaceId) throw new Error('workspaceId required');
  if (!req.engine) throw new Error('engine required');
  if (!req.capability) throw new Error('capability required');

  const model = CAPABILITY_MODEL[req.capability] ?? 'gpt-4o-mini';
  const requestId = uuid();
  const start = Date.now();

  const res = await openaiGenerate({
    model,
    systemPrompt: (req.context as any)?.systemPrompt,
    userPrompt: req.input,
    maxTokens: (req.context as any)?.maxTokens,
    temperature: (req.context as any)?.temperature,
  });

  const latencyMs = Date.now() - start;
  const rates = COST_PER_1K[model] ?? COST_PER_1K['gpt-4o-mini'];
  const cost = (res.promptTokens / 1000) * rates.input + (res.completionTokens / 1000) * rates.output;

  return {
    requestId,
    output: res.output,
    model: res.model,
    usage: { promptTokens: res.promptTokens, completionTokens: res.completionTokens, estimatedCostUsd: Math.round(cost * 1_000_000) / 1_000_000 },
    latencyMs,
    providerRequestId: res.providerRequestId,
  };
}
