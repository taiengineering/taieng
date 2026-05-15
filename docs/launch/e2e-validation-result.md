# TAI Safe — Real SaaS Business Flow E2E Validation

작성일: 2026-05-15

---

## 1. Customer Journey E2E 검증 결과

| # | 단계 | 상태 | 근거 |
|---|------|:---:|------|
| 1 | 회원가입 | ✅ | users 19건 존재 |
| 2 | 본인인증 | ⚠️ | KG이니시스 통합인증 CI 기반, 승인 대기 |
| 3 | 결제 | ❌ | payments 110건 전부 PENDING — 실제 결제 처리 완료 건 0 |
| 4 | Tenant(사업장) 생성 | ✅ | factories 330건 |
| 5 | 권한 부여 | ⚠️ | roles 18건 존재, 결제→권한 연결 미검증 |
| 6 | 진단 실행 | ⚠️ | diagnosis_session 1건, rule_results 0건 |
| 7 | SaaS Workflow 사용 | ⚠️ | factory_process 9건, 결제 기반 활성화 미검증 |
| 8 | 결과물 생성 | ⚠️ | generated_document 1건, document_form_master 63건 |
| 9 | Cockpit 연결 | ✅ | Watch Engine 18섹션 Cockpit 구현 |
| 10 | 알림/거버넌스 연결 | ✅ | Alert + Governance + Identity 구조 완료 |

---

## 2. Payment → Tenant Activation

| 항목 | 상태 | 상세 |
|------|:---:|------|
| PG 코드 연동 | ✅ | KG이니시스 연동 코드 완료 |
| PG 승인 | ❌ | KG이니시스 승인 대기 중 |
| 도메인 전환 | ❌ | new.taieng.co.kr → taieng.co.kr 대기 |
| **결제 성공 건수** | **0건** | **110건 전부 PENDING** |
| **활성 구독 건수** | **0건** | **24건 PENDING, 1건 FAILED** |
| 결제 → 권한 활성화 | ❓ | 실제 결제 완료 후 검증 불가 |
| 중복 결제 방지 | ❓ | 실제 검증 불가 |
| 결제 취소 | ❓ | 실제 검증 불가 |
| Tenant isolation | ⚠️ | factory_id 기반 분리, RLS 보류 |

**핵심 문제: KG이니시스 승인 전까지 실제 결제 E2E 검증 불가.**

---

## 3. Tenant Bootstrap

| 항목 | 상태 | 비고 |
|------|:---:|------|
| Factory(사업장) 생성 | ✅ | 330건 |
| Default roles | ✅ | 18건 등록 |
| 결제 → 사업장 연결 | ❓ | subscription에 factory_id 컨럼 존재, 활성 플로우 미검증 |
| Default governance | ❌ | Watch Engine tenant_operational_registry 2건 (수동) |
| Default visibility | ❌ | 자동 생성 로직 없음 |
| Default notification audience | ❌ | 자동 생성 로직 없음 |
| Synthetic baseline | ❌ | tenant별 synthetic 미구현 |

**핵심 문제: Tenant 생성 시 자동 bootstrap 로직 미구현. 수동 등록 필요.**

---

## 4. Worker Workflow UX

| 항목 | 상태 | 비고 |
|------|:---:|------|
| 공정등록 | ⚠️ | factory_process 9건 존재, UX 검증 필요 |
| 점검세트 | ❓ | inspection_sets 테이블 확인 필요 |
| 문서생성 | ⚠️ | generated_document 1건, form_master 63건 |
| 작업자 응답 3~5초 | ❓ | 성능 테스트 미실시 |
| 입력 플로우 자연스러움 | ❓ | 실제 사용자 테스트 필요 |
| Field confusion | ❓ | SelectBar mismatch 이력 있음 (Watch Engine으로 탐지 가능) |

---

## 5. Document MVP

| 항목 | 상태 | 비고 |
|------|:---:|------|
| document_form_master | ✅ | 63종 등록 |
| document_schema_registry | ✅ | 3,873건 |
| generated_document | ⚠️ | 1건 (최소 검증) |
| runtime_document_data | ⚠️ | 1건 |
| runtime_document_activation | ❌ | 0건 — 활성화된 문서 없음 |
| Gotenberg PDF 생성 | ✅ | Railway Singapore 운영 중 |
| 다운로드 가능 | ✅ | Gotenberg 기반 |
| Tenant 데이터 반영 | ❓ | 실제 사업장 데이터 바인딩 검증 필요 |

**핵심 문제: 스키마/폼 구조는 있지만, 실제 10종 MVP 문서 생성 E2E 검증 필요.**

---

## 6. Operational Connection

| 연결 | 상태 | 비고 |
|------|:---:|------|
| Workflow → business_event | ✅ | emit_event() SDK 3개 flow |
| business_event → integrity | ✅ | Evaluator + 4 rules + SLA |
| integrity → incident | ✅ | Priority + Risk + Repeated |
| incident → alert | ✅ | 6 rules + Telegram |
| alert → notification | ✅ | Delivery layer |
| incident → governance | ✅ | Tenant Impact |
| governance → identity | ✅ | Visibility Scope |
| 전체 Cockpit 연결 | ✅ | 18섹션 |

**Operational Connection: 완전 구현.**

---

## 7. Cockpit 운영성

| 항목 | 평가 |
|------|------|
| 운영자 대응 가능성 | ✅ ACK/해결/무시 + 5개 복구 버튼 |
| Alert fatigue 방지 | ✅ threshold + cooldown + dedupe + mute |
| Issue workflow | ✅ ACTIVE → ACK → RESOLVED/IGNORED |
| Tenant visibility | ✅ Identity Core visibility scope |
| Recovery/Action | ✅ 복구 추천 + 조치 기록 + 플레이북 |
| Control Surface 방향 | ✅ Dashboard 아닌 Operational Control |

---

## 8. P0/P1/P2 재분류

### P0 — 런치 차단

| # | 리스크 | 상태 | 조치 |
|---|--------|:---:|------|
| 1 | **Payment E2E** | ❌ | KG이니시스 승인 → 결제 성공 → 권한 활성 전체 |
| 2 | **진단→SaaS Setup** | ❌ | 진단 결과 → SaaS tenant bootstrap |
| 3 | **SaaS 운영 E2E** | ❌ | 결제~업무사용 전체 플로우 |
| 4 | **Document MVP 10종** | ❌ | 스키마 있지만 실제 생성 E2E 미검증 |
| 5 | **Worker UX 3~5초** | ❓ | 성능 테스트 미실시 |

### P1 — 운영 가능하지만 위험

| # | 리스크 |
|---|--------|
| 6 | Railway 배포 (scheduler v1.7 + 11 router) |
| 7 | Telegram 환경변수 설정 |
| 8 | Synthetic 계정 설정 |
| 9 | Tenant bootstrap 자동화 |
| 10 | PATTERN_SYNC dedupe 보강 |
| 11 | RLS 적용 |
| 12 | INTERNAL_API_SECRET 로테이션 |

### P2 — 운영 중 개선

| # | 리스크 |
|---|--------|
| 13 | Playwright + Chromium |
| 14 | data-testid 프론트 추가 |
| 15 | Playbook/Recovery CRUD UI |
| 16 | _is_tenant_admin() 실제 연동 |
| 17 | 잘못 올린 파일 삭제 |

---

## 9. 즉시 수정 필요 항목

1. **Railway 배포** — tai-api main push (Watch Engine 즉시 운영 가능)
2. **환경변수 7개 설정** — Telegram + Synthetic + Playwright
3. **tai-admin git push** — Cockpit 18섹션 배포

## 10. 런치 가능 여부

| 범위 | 판단 | 조건 |
|------|:---:|------|
| **Watch Engine** | ✅ 가능 | Railway 배포 + 환경변수 |
| **진단 서비스** | ⚠️ 부분 가능 | 무료 진단은 작동, 유료는 결제 필요 |
| **SaaS 전체** | ❌ 불가 | Payment + 진단→SaaS + Document 필수 |

### 권장 순서
1. Railway 배포 + 환경변수 (Watch Engine 즉시 운영)
2. KG이니시스 승인 → Payment E2E
3. 진단 → SaaS tenant bootstrap
4. Document MVP 10종 생성 검증
5. Worker UX 성능 테스트
