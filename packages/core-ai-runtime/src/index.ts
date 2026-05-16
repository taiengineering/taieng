// 45cm AI Runtime — RFC-004 AI Metering compliant
// Engines MUST NOT call LLM providers directly.

import { v4 as uuidv4 } from 'uuid';
import type { AiGenerateRequest, AiGenerateResult, AiUsageLog } from '@45cm/core-shared-types';

export type { AiGenerateRequest, AiGenerateResult, AiUsageLog };

// ─── Provider Adapter Interface ───

export interface ProviderAdapter {
  name: string;
  generate(params: {
    model: string;
    prompt: string;
    maxTokens?: number;
  }): Promise<{
    output: string;
    promptTokens: number;
    completionTokens: number;
    latencyMs: number;
  }>;
}

// ─── Capability → Model Routing (placeholder) ───

const CAPABILITY_MODEL_MAP: Record<string, string> = {
  'marketing.generate_draft': 'gpt-4o-mini',
  'marketing.rewrite_humanize': 'gpt-4o-mini',
  'marketing.classify_intent': 'gpt-4o-mini',
};

// ─── AI Runtime Gateway ───

export class AiRuntime {
  private provider: ProviderAdapter | null = null;
  private usageLogs: AiUsageLog[] = [];

  registerProvider(adapter: ProviderAdapter): void {
    this.provider = adapter;
  }

  async generate(request: AiGenerateRequest): Promise<AiGenerateResult> {
    if (!request.workspaceId) throw new Error('workspaceId is required');
    if (!request.engine) throw new Error('engine is required');
    if (!request.capability) throw new Error('capability is required');

    const requestId = uuidv4();
    const model = CAPABILITY_MODEL_MAP[request.capability] ?? 'gpt-4o-mini';

    // TODO: Check workspace AI budget
    // TODO: Resolve prompt from prompt_registry
    // TODO: Apply workspace policy

    if (!this.provider) {
      // Mock response when no provider is registered
      const mockResult: AiGenerateResult = {
        requestId,
        output: `[MOCK] AI output for capability=${request.capability}`,
        model,
        usage: { promptTokens: 0, completionTokens: 0, estimatedCostUsd: 0 },
        latencyMs: 0,
      };
      this.logUsage(request, mockResult, 'success');
      return mockResult;
    }

    const start = Date.now();
    try {
      const providerResult = await this.provider.generate({
        model,
        prompt: request.input,
      });

      const result: AiGenerateResult = {
        requestId,
        output: providerResult.output,
        model,
        usage: {
          promptTokens: providerResult.promptTokens,
          completionTokens: providerResult.completionTokens,
          estimatedCostUsd: 0, // TODO: cost calculation
        },
        latencyMs: providerResult.latencyMs,
      };

      this.logUsage(request, result, 'success');
      return result;
    } catch (err) {
      const errorResult: AiGenerateResult = {
        requestId,
        output: '',
        model,
        usage: { promptTokens: 0, completionTokens: 0, estimatedCostUsd: 0 },
        latencyMs: Date.now() - start,
      };
      this.logUsage(request, errorResult, 'error');
      throw err;
    }
  }

  private logUsage(
    request: AiGenerateRequest,
    result: AiGenerateResult,
    status: AiUsageLog['status'],
  ): void {
    const log: AiUsageLog = {
      id: uuidv4(),
      workspace_id: request.workspaceId,
      engine: request.engine,
      capability: request.capability,
      provider: this.provider?.name ?? 'mock',
      model: result.model,
      prompt_tokens: result.usage.promptTokens,
      completion_tokens: result.usage.completionTokens,
      estimated_cost_usd: result.usage.estimatedCostUsd,
      latency_ms: result.latencyMs,
      status,
      created_at: new Date().toISOString(),
    };
    this.usageLogs.push(log);
    // TODO: persist to core_ai.ai_usage_log via Supabase
  }

  getUsageLogs(): AiUsageLog[] {
    return [...this.usageLogs];
  }
}

export const aiRuntime = new AiRuntime();
