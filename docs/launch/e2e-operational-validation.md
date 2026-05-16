# TAI Safe — Real Operational E2E & SaaS Readiness Validation

작성일: 2026-05-16

---

## 1. E2E 검증 범위

| 영역 | 테이블 | 라우터 | Scheduler | Cockpit | Admin 페이지 |
|------|:---:|:---:|:---:|:---:|:---:|
| Watch Engine | 22 | 13 | 9 | 18섹션 | 1 |
| Operational Control | 3 | 1 | - | - | 3 |
| Document Pipeline | 4 | 1 | - | - | 1 |
| Identity/Governance | 3 | 2 | - | 2섹션 | - |
| **합계** | **32** | **17** | **9** | **20섹션** | **5** |

---

## 2. Tenant Onboarding

| 단계 | 상태 | 데이터 |
|------|:---:|------|
| 회원가입 | ✅ | 19명 |
| 사업장 생성 | ✅ | 330개 |
| 본인인증 | ⚠️ | KG이니시스 통합인증 대기 |
| 결제 | ❌ | 110건 전부 PENDING (0건 성공) |
| 구독 활성화 | ❌ | 0건 ACTIVE |
| Role 적용 | ✅ | roles 18건, identity_role_mapping 14건 |
| Menu visibility | ✅ | get_menu_visibility() 구현 |
| Cockpit 접근 | ✅ | 18섹션 + 5 admin 페이지 |
| Notification 대상 | ✅ | resolve_notification_audience() |

**차단 요인: KG이니시스 승인 → 결제 0건 성공**

---

## 3. Workflow / Document

| 단계 | 상태 | 데이터 |
|------|:---:|------|
| 공정등록 | ✅ | factory_process 9건 |
| Watch Engine emit | ✅ | business_event 42건 |
| Integrity 평가 | ✅ | integrity_event 12건 (active 8) |
| Document activation (auto hook) | ✅ | TASK 23 hook 삽입 완료 |
| runtime_document_activation | ✅ | 3건 |
| generated_document | ✅ | 2건 |
| Gotenberg PDF | ✅ | 코드 완료, Railway 배포 필요 |
| Download URL | ✅ | API + redirect 구현 |
| form_master | ✅ | 63종 |
| schema_registry | ✅ | 3,873건 |
| workflow_document_registry | ✅ | 10종 MVP |

**Document Pipeline: 구조 완료. Railway 배포 시 즉시 동작.**

---

## 4. Notification

| 항목 | 상태 |
|------|:---:|
| Alert rule (6개) | ✅ |
| Message template (6개) | ✅ |
| Notification routing (6개) | ✅ |
| Cooldown/Dedupe | ✅ |
| Mute/Snooze | ✅ |
| Telegram 발송 | ⚠️ 환경변수 미설정 |
| Audience resolution | ✅ (routing registry 연동) |
| Delivery = Delivery only | ✅ (판단 금지 문서화) |

---

## 5. Governance / Risk

| 항목 | 상태 | 데이터 |
|------|:---:|------|
| Tenant registry | ✅ | 2건 (tai, anonymous) |
| Tenant impact engine | ✅ | HEALTHY~CRITICAL 계산 |
| Escalation (L1~L4) | ✅ | rule-based |
| Incident priority (P1~P4) | ✅ | Priority Engine |
| Workflow risk score | ✅ | LOW~CRITICAL |
| Stability tracker | ✅ | STABLE~CRITICAL |
| Recovery recommendation | ✅ | 9개 매핑 |
| Playbooks | ✅ | 5개 |
| Patterns | ✅ | 5개 |
| Identity visibility | ✅ | 7 roles, 14 mappings |

---

## 6. Failure / Recovery

| 시나리오 | 상태 |
|----------|:---:|
| field_mismatch 탐지 | ✅ |
| SLA violation 탐지 | ✅ |
| repeated_failure 생성 | ✅ |
| workflow_instability 생성 | ✅ |
| Recovery recommendation 매칭 | ✅ |
| Playbook 연결 | ✅ |
| Action log (ACK/RESOLVE/IGNORE) | ✅ (2건) |
| Alert cooldown/dedupe | ✅ |
| Fail-safe (hook 실패 → workflow 정상) | ✅ |

---

## 7. Cockpit 운영성

| 기능 | 상태 |
|------|:---:|
| 18섹션 UI | ✅ |
| 60초 polling | ✅ |
| 이슈 ACK/해결/무시 | ✅ |
| 복구 조치 5버튼 | ✅ |
| 알림 규칙 설정/무음 | ✅ |
| 플레이북 조회 | ✅ |
| 패턴 동기화 | ✅ |
| 반복탐지 실행 | ✅ |
| Telegram 테스트 | ✅ (환경변수 필요) |
| Operational Control Surface | ✅ |

---

## 8. 병목 / 위험 요소

| # | 위험 | 심각도 | 설명 |
|---|------|:---:|------|
| 1 | Railway 미배포 | P0 | scheduler v1.7 + 13 router 미반영. 현재 Railway는 구버전 |
| 2 | Payment 0건 성공 | P0 | KG이니시스 승인 대기. 유료 SaaS 운영 불가 |
| 3 | Telegram 환경변수 | P1 | BOT_TOKEN + CHAT_ID 미설정 → alert 발송 불가 |
| 4 | Synthetic 계정 | P1 | TEST_EMAIL/PASSWORD/FACTORY_ID 미설정 |
| 5 | PATTERN_SYNC 중복 누적 | P1 | dedupe 보강 필요 |
| 6 | RLS 미적용 | P1 | Watch Engine 22테이블 RLS 보류 |
| 7 | Playwright 미설치 | P2 | Browser Synthetic 전용 |
| 8 | data-testid 미추가 | P2 | CSS fallback으로 운영 가능 |
| 9 | Tenant bootstrap 자동화 | P2 | 현재 수동 등록만 |
| 10 | form-templates HTML 업로드 | P2 | 63종 중 일부만 HTML 존재 |

---

## 9. SaaS Readiness 판정

| 영역 | 상태 | 조건 |
|------|:---:|------|
| Watch Engine | ✅ READY | Railway 배포 시 |
| Notification | ⚠️ WARNING | Telegram 환경변수 설정 시 READY |
| Workflow | ✅ READY | emit_event + hook 완료 |
| Document | ⚠️ WARNING | Railway 배포 + Gotenberg 접근 시 READY |
| Governance | ✅ READY | 구조 완료 |
| Worker UX | ⚠️ WARNING | 성능 테스트 미실시 |
| Payment | ❌ BLOCKED | KG이니시스 승인 대기 |
| Tenant Onboarding | ⚠️ WARNING | 결제 제외 시 부분 가능 |

### 최종 판정

| 단계 | 판정 | 조건 |
|------|:---:|------|
| **Internal Beta** | ✅ 가능 | Railway 배포 + 환경변수 설정 |
| **Pilot 고객** | ⚠️ 조건부 | 무료 진단 + Watch Engine 운영 |
| **유료 SaaS** | ❌ 불가 | Payment E2E + Document MVP 검증 필요 |

---

## 10. P0/P1/P2 재분류

### P0 — 런치 차단
| # | 리스크 |
|---|--------|
| 1 | Railway 배포 (scheduler v1.7 + 13 Watch Engine router + Document hook) |
| 2 | Payment E2E (KG이니시스 승인 → 결제 → 권한 → SaaS) |
| 3 | 진단→SaaS Setup 연결 |

### P1 — 운영 가능하지만 위험
| # | 리스크 |
|---|--------|
| 4 | Telegram 환경변수 (BOT_TOKEN + CHAT_ID) |
| 5 | Synthetic 계정 (TEST_EMAIL + PASSWORD + FACTORY_ID) |
| 6 | PATTERN_SYNC dedupe 보강 |
| 7 | RLS 적용 |
| 8 | INTERNAL_API_SECRET 로테이션 |

### P2 — 운영 중 개선
| # | 리스크 |
|---|--------|
| 9 | Playwright + Chromium |
| 10 | data-testid 프론트 추가 |
| 11 | Tenant bootstrap 자동화 |
| 12 | Playbook/Recovery CRUD UI |
| 13 | form-templates HTML 업로드 |

---

## 11. 즉시 실행 필요 항목

1. **Railway 배포** — `tai-api` main push (Watch Engine + Document Pipeline 전체)
2. **환경변수 7개** — Telegram 2 + Synthetic 3 + Playwright 2
3. **tai-admin 확인** — Cloudflare Pages 자동 배포 (Cockpit 18섹션 + admin 5페이지)

## 12. 권장 순서

1. Railway 배포 + 환경변수 (Watch Engine 즉시 운영)
2. Internal Beta 시작 (무료 진단 + Watch Engine 관제)
3. KG이니시스 승인 → Payment E2E
4. 진단→SaaS tenant bootstrap
5. Document MVP 10종 실제 생성 검증
6. Pilot 고객 온보딩
