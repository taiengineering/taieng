# TAI Safe — Launch Blocking Risk

작성일: 2026-05-15

---

## P0 — 즉시 런치 차단

| # | 리스크 | 상태 | 조치 필요 |
|---|--------|:---:|----------|
| 1 | **Payment E2E 미완료** | ❌ | KG이니시스 승인 대기 + 도메인 전환 |
| 2 | **진단→SaaS Setup 연결** | ❌ | 진단 결과 → tenant 생성 → workflow bootstrap 플로우 필요 |
| 3 | **SaaS 운영 E2E** | ❌ | 결제 → 권한 → SaaS 접근 → 업무 사용 전체 플로우 |
| 4 | **Document MVP 10종** | ❌ | 문서 생성 기능 최소 범위 |
| 5 | **Worker UX 3~5초 응답** | ❓ | 성능 테스트 필요 |

## P1 — 운영 가능하지만 위험

| # | 리스크 | 상태 | 조치 필요 |
|---|--------|:---:|----------|
| 6 | **Railway 배포 후 Scheduler 검증** | ⚠️ | scheduler v1.7 + 11개 라우터 첫 배포 |
| 7 | **Telegram 환경변수 설정** | ⚠️ | BOT_TOKEN + CHAT_ID |
| 8 | **Synthetic 계정 설정** | ⚠️ | TEST_EMAIL + PASSWORD + FACTORY_ID |
| 9 | **PATTERN_SYNC 중복 누적 방지** | ⚠️ | dedupe 로직 보강 필요 |
| 10 | **db.database vs db.supabase_client import 통일** | ⚠️ | scheduler.py는 db.database, watch_engine은 db.supabase_client |
| 11 | **INTERNAL_API_SECRET 로테이션** | ⚠️ | 세션 중 노출 이력 |
| 12 | **RLS 미적용** | ⚠️ | Watch Engine 17개 테이블 RLS 보류 상태 |

## P2 — 운영 중 개선 가능

| # | 리스크 | 상태 | 비고 |
|---|--------|:---:|------|
| 13 | Playwright + Chromium Railway 설치 | ❌ | Browser Synthetic 전용 |
| 14 | data-testid 프론트 추가 | ❌ | CSS fallback으로 운영 가능 |
| 15 | SLA threshold 운영 조정 | ✅ | UI에서 조정 가능 |
| 16 | Playbook/Recovery CRUD UI | ❌ | 현재 DB 직접 등록만 |
| 17 | _is_tenant_admin() 실제 연동 | ❌ | stub 상태 |
| 18 | 잘못 올린 파일 삭제 | ❌ | tai-admin의 오래된 경로 2개 |
| 19 | Vultr 프록시 / Railway 고정 IP | ❌ | law.go.kr 판례 API용 |
| 20 | KOSHA API APICODE_ERROR | ❌ | data.go.kr 계정 활성화 확인 |

---

## 런치 가능 여부 판단

### Watch Engine 단독: ✅ 런치 가능
- Railway 배포 + 환경변수 설정만으로 즉시 운영 가능
- 17개 DB + 9개 Scheduler + 11개 Router + 18개 Cockpit UI
- Fail-safe 전체 구현

### SaaS 전체: ❌ 런치 불가
- Payment E2E 미완료 (결제 → 권한 → SaaS 흐름)
- 진단 → SaaS 연결 미완료
- Document MVP 미완료

### 권장 순서
1. Railway 배포 + 환경변수 설정 (Watch Engine 즉시 운영)
2. Payment E2E (KG이니시스 승인 후)
3. 진단 → SaaS 연결
4. Document MVP
5. Worker UX 성능 최적화
