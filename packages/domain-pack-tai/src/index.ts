// 45cm Domain Pack — TAI (산업안전 SaaS)
// RFC-011 Domain Pack compliant
// Runtime MUST NOT hardcode TAI-specific logic
// This pack is injected via domain_pack_bindings

// ─── Domain Pack Interface ───

export interface DomainPack {
  key: string;
  version: string;
  keywords: DomainKeyword[];
  ctas: DomainCta[];
  promptKeys: string[];
  config: Record<string, unknown>;
}

export interface DomainKeyword {
  keyword: string;
  intent: string;
  priority: 'P1' | 'P2' | 'P3' | 'P4';
}

export interface DomainCta {
  name: string;
  ctaType: 'free_offer' | 'paid_validation' | 'subscription_conversion';
  targetUrl: string;
}

// ─── TAI Pack: Default Keywords ───

export const TAI_KEYWORDS: DomainKeyword[] = [
  { keyword: '중대재해처벌법', intent: 'legal_inquiry', priority: 'P1' },
  { keyword: '산업안전보건법', intent: 'legal_inquiry', priority: 'P1' },
  { keyword: '안전관리자 선임', intent: 'compliance_question', priority: 'P2' },
  { keyword: '과태료 기준', intent: 'penalty_inquiry', priority: 'P2' },
  { keyword: '위험성평가', intent: 'assessment_question', priority: 'P2' },
  { keyword: '안전보건관리체계', intent: 'system_question', priority: 'P3' },
  { keyword: '건설현장 안전', intent: 'construction_safety', priority: 'P3' },
  { keyword: '산업재해 예방', intent: 'prevention_question', priority: 'P3' },
];

// ─── TAI Pack: Default CTAs ───

export const TAI_CTAS: DomainCta[] = [
  {
    name: '무료 법령진단',
    ctaType: 'free_offer',
    targetUrl: 'https://taieng.co.kr/diagnosis',
  },
  {
    name: '유료 전문 진단',
    ctaType: 'paid_validation',
    targetUrl: 'https://taieng.co.kr/diagnosis/pro',
  },
  {
    name: '안전관리 SaaS 구독',
    ctaType: 'subscription_conversion',
    targetUrl: 'https://taieng.co.kr/pricing',
  },
];

// ─── TAI Pack: Prompt Keys ───

export const TAI_PROMPT_KEYS = [
  'tai.draft.naver_kin_reply',
  'tai.draft.blog_post',
  'tai.draft.linkedin_post',
  'tai.humanize.formal_korean',
  'tai.classify.safety_intent',
] as const;

// ─── TAI Pack Export ───

export const taiPack: DomainPack = {
  key: 'tai-pack',
  version: '0.1.0',
  keywords: TAI_KEYWORDS,
  ctas: TAI_CTAS,
  promptKeys: [...TAI_PROMPT_KEYS],
  config: {
    industry: 'industrial_safety',
    locale: 'ko-KR',
    brandVoice: 'professional_korean_formal',
  },
};
