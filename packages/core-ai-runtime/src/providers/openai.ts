import OpenAI from 'openai';

let client: OpenAI | null = null;

function getClient(): OpenAI {
  if (!client) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('OPENAI_API_KEY is required');
    client = new OpenAI({ apiKey });
  }
  return client;
}

export async function openaiGenerate(params: {
  model: string;
  systemPrompt?: string;
  userPrompt: string;
  maxTokens?: number;
  temperature?: number;
}): Promise<{
  output: string;
  promptTokens: number;
  completionTokens: number;
  model: string;
  providerRequestId: string;
}> {
  const start = Date.now();
  const res = await getClient().chat.completions.create({
    model: params.model,
    messages: [
      ...(params.systemPrompt ? [{ role: 'system' as const, content: params.systemPrompt }] : []),
      { role: 'user' as const, content: params.userPrompt },
    ],
    max_tokens: params.maxTokens ?? 2048,
    temperature: params.temperature ?? 0.7,
  });
  return {
    output: res.choices[0]?.message?.content ?? '',
    promptTokens: res.usage?.prompt_tokens ?? 0,
    completionTokens: res.usage?.completion_tokens ?? 0,
    model: res.model,
    providerRequestId: res.id,
  };
}
