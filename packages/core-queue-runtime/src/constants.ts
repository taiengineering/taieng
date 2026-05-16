export function queueName(engine: string, capability: string): string {
  return `45.${engine}.${capability}`;
}

export function dlqName(engine: string, capability: string): string {
  return `45.${engine}.${capability}.dlq`;
}

export const MARKETING_QUEUES = {
  COLLECT:   queueName('marketing', 'collect'),
  CLASSIFY:  queueName('marketing', 'classify'),
  DRAFT:     queueName('marketing', 'draft'),
  HUMANIZE:  queueName('marketing', 'humanize'),
  APPROVAL:  queueName('marketing', 'approval'),
  PUBLISH:   queueName('marketing', 'publish'),
  CTA_TRACK: queueName('marketing', 'cta_track'),
  ANALYTICS: queueName('marketing', 'analytics'),
} as const;

export const AI_QUEUES = {
  GENERATE: queueName('ai', 'generate'),
} as const;

export const DEFAULT_RETRY = {
  maxRetry: 3,
  backoff: { type: 'exponential' as const, delay: 30_000 },
};
