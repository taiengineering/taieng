# Runtime Isolation Policy

## 환경 구분

| 환경 | environment 값 | 용도 | Alert 발송 | Governance 반영 |
|------|:---:|------|:---:|:---:|
| **production** | `production` | 실제 운영 | ✅ | ✅ |
| **mock** | `mock` | 시나리오 검증 | ❌ | ❌ |
| **staging** | `staging` | 배포 전 검증 | ❌ | ❌ |
| **dev** | `dev` | 개발 | ❌ | ❌ |

## Mock 데이터 식별

```
tenant_id LIKE 'mock_%'   → Mock Tenant
environment = 'mock'      → Mock Event
trace_id LIKE 'mock_%'    → Mock Trace
```

## 분리 규칙

1. **Alert Engine**: `environment = 'production'`만 평가
2. **Governance**: `environment = 'production'`만 계산
3. **Notification**: Mock tenant 발송 금지
4. **PATTERN_SYNC**: Mock 포함 누적 가능 (패턴 학습용)
5. **Cockpit**: 전체 표시 (Mock 레이블 유지)

## Production Guard API

| API | 용도 |
|-----|------|
| `GET /production/env-check` | 환경변수 검증 |
| `GET /production/runtime-stats` | Mock vs Real 통계 |
| `GET /production/safety-guard` | 안전 상태 검증 |
| `GET /production/scheduler-status` | Scheduler 현황 |
| `GET /production/summary` | Production 요약 |

## Railway 배포 체크리스트

### 배포 전
- [ ] `git push origin main` (자동 배포)
- [ ] Railway env: SUPABASE_URL, SUPABASE_KEY 확인
- [ ] Railway env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 설정
- [ ] Railway env: GOTENBERG_URL 확인 (`http://tai-gotenberg.internal:3000`)

### 배포 후
- [ ] `/health` 응답 200 확인
- [ ] `/production/env-check` 환경변수 정상
- [ ] `/production/scheduler-status` Scheduler 로드 확인
- [ ] `/production/safety-guard` CRITICAL 0건 확인
- [ ] `/production/runtime-stats` Mock/Real 분리 확인
- [ ] Cockpit 18섹션 정상 로드 확인
