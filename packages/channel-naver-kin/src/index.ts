// Naver Kin Channel Adapter — RFC-006 compliant
// Adapter MUST NOT call AI or contain business logic

export interface NormalizedContent {
  source: string;
  externalId: string;
  title: string;
  body: string;
  author?: string;
  url: string;
  collectedAt: string;
  rawPayload: Record<string, unknown>;
}

export interface CollectInput {
  workspaceId: string;
  keyword: string;
  maxResults?: number;
}

const API_URL = 'https://openapi.naver.com/v1/search/kin.json';

export async function collect(input: CollectInput): Promise<NormalizedContent[]> {
  const clientId = process.env.NAVER_CLIENT_ID;
  const clientSecret = process.env.NAVER_CLIENT_SECRET;
  if (!clientId || !clientSecret) throw new Error('NAVER_CLIENT_ID/SECRET required');

  const params = new URLSearchParams({
    query: input.keyword,
    display: String(input.maxResults ?? 10),
    sort: 'date',
  });

  const res = await fetch(`${API_URL}?${params}`, {
    headers: { 'X-Naver-Client-Id': clientId, 'X-Naver-Client-Secret': clientSecret },
  });
  if (!res.ok) throw new Error(`Naver API ${res.status}: ${await res.text()}`);

  const json = await res.json() as { items?: Array<{ title: string; description: string; link: string; }> };
  const items = json.items ?? [];

  return items.map((item, i) => ({
    source: 'naver_kin',
    externalId: `nk-${Buffer.from(item.link).toString('base64url').slice(0, 32)}`,
    title: stripHtml(item.title),
    body: stripHtml(item.description),
    url: item.link,
    collectedAt: new Date().toISOString(),
    rawPayload: item as unknown as Record<string, unknown>,
  }));
}

function stripHtml(s: string): string {
  return s.replace(/<[^>]*>/g, '').replace(/&[a-z]+;/gi, ' ').trim();
}
