# Platform Core — Engine Namespace & Domain Separation

## 목적
Platform Core와 Engine Domain을 명확히 분리.
Watch Engine 언어가 Platform 전체 언어로 확산되는 것을 방지.

---

## 계층 구조

```
┌───────────────────────────────────────┐
│         Engine Domain Layer          │
│  watch.*  marketing.*  tai.*  ...   │
├───────────────────────────────────────┤
│         Platform Core Layer           │
│  Event Envelope  Runtime Contract    │
│  Tenant  Trace  Retry  Idempotency  │
├───────────────────────────────────────┤
│         Infrastructure Layer          │
│  Supabase  Railway  Cloudflare      │
└───────────────────────────────────────┘
```

## Engine Namespace 등록부

| Namespace | Engine | 소유 | 상태 |
|-----------|--------|------|:---:|
| `watch` | Watch Engine | TAI | ✅ Active |
| `tai` | Regulation Engine | TAI | 🚧 Planned |
| `marketing` | Marketing Engine | 45CM | 🚧 Planned |
| `workflow` | Workflow Engine | 공통 | 🚧 Planned |

## Engine Domain 개념 분류

### Watch Engine (`watch.*`)
| 개념 | Core? | 설명 |
|------|:---:|------|
| integrity | ❌ | 워크플로우 무결성 |
| incident | ❌ | 운영 이슈 |
| governance | ❌ | 테넌트 위험도 |
| recovery | ❌ | 복구 추천 |
| escalation | ❌ | 위험 상향 |
| alert | ❌ | 알림 엔진 |
| synthetic | ❌ | 합성 테스트 |
| pattern | ❌ | 패턴 학습 |

### Platform Core (공통)
| 개념 | Core? | 설명 |
|------|:---:|------|
| event | ✅ | 이벤트 봉투 |
| trace | ✅ | 추적 |
| flow | ✅ | 워크플로우 |
| step | ✅ | 단계 |
| actor | ✅ | 행위자 |
| tenant | ✅ | 테넌트 |
| priority | ✅ | 우선순위 |
| retry | ✅ | 재시도 |
| idempotency | ✅ | 멱등성 |
| notification | ✅ | 알림 봉투 (발송만) |

## Engine Exchange 기준

45CM와 TAI가 엔진을 교환하려면:

1. **Platform Core Contract 준수** — Event Envelope + Tenant + Trace
2. **자체 Namespace 사용** — `watch.*`, `marketing.*`
3. **Engine Interface 구현** — init/process_event/health_check/shutdown
4. **Domain 개념 분리** — Core에 도메인 의미 포함 금지
5. **Tenant Boundary 준수** — cross-tenant 금지

## 디렉토리 구조

```
docs/
├── platform-core/           ← 공통 Runtime 규약
│   ├── event-envelope.md
│   ├── runtime-contract.md
│   └── engine-namespace.md
├── platform-grammar/        ← TAI 플랫폼 문법 (Watch 포함)
│   ├── core-language.md
│   ├── semantic-adapter.md
│   └── ...
├── engines/                 ← 엔진별 도메인 문서
│   ├── watch/
│   │   └── watch-domain.md
│   ├── marketing/   (future)
│   └── tai/         (future)
└── launch/              ← 배포/운영 문서
```
