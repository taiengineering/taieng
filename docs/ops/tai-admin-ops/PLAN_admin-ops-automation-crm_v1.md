---

class: plans
type: PLAN
scope: ops
project: tai-admin-ops
title: TAI 어드민 실운영·자동화·CRM — 3축 갭분석 및 우선순위 구축계획
version: 1
status: PENDING
owner: taiwang
---

# TAI 어드민 실운영·자동화·CRM — 갭분석 및 구축계획 (v1)

- **골**: `G-ms5pdquz-9e76e5` (선행 `G-ms4je4z3-33eada` 승계/SUPERSEDED)
- **작성 근거**: 2026-07-29 프론트(`tai-admin@feat/admin-rebuild`) · 백엔드(`tai-api@main`) · DB(`vwlahtguyggrhvslabax`) 실측
- **선행 문서**: `HANDOFF_session-20260729_v1.md`

---

## 0. 이 문서의 판정 요약

어드민 리빌드는 **화면 이식은 됐으나 조회 전용**이다. 백엔드는 예상보다 훨씬 갖춰져 있고, **결손의 대부분은 프론트 미연결**이다. 이것이 이번 실측의 핵심 발견이다.

| 축 | 백엔드 | 프론트 | 실질 상태 |
|---|---|---|---|
| 운영(결제 처리) | 액션 API 7종 전부 존재 | 버튼 0개 | **프론트만 붙이면 됨** |
| 자동화 | 엔진 6엔드포인트 존재·등록됨 | **화면 자체가 없음** | 프론트 신설 필요 |
| CRM | 통합검색·고객360 존재·등록됨 | 검색바 고아, 고객360 화면 없음 | 프론트 신설 + 백엔드 소폭 보강 |

---

## 1. 실측 사실 (근거)

### 1-1. 선행 진단 중 **뒤집힌 것 2건** — 중요

| 기존 진단(HANDOFF) | 실측 결과 | 근거 |
|---|---|---|
| "통합검색 global_search_svc 완성됐으나 **상단바 미연결**" → 서비스만 있는 것으로 읽힘 | **백엔드는 라우터까지 정상 등록 완료.** `GET /search` 즉시 호출 가능 | `routers/global_search.py`, `router_registry/saas_core.py` |
| "수동활성화는 ledger 응답에 contract_id가 없어 **백엔드 보강 선행 필요**" | **목록 API는 이미 contract_id를 반환한다.** `GET /payments`는 `v_payments_list` 뷰를 `select("*")` 조회하고, 이 뷰에 `contract_id uuid` 컬럼이 실재 | DB 실측(`information_schema.columns`, ref `vwlahtguyggrhvslabax`) |

→ **수동활성화는 백엔드 선행 없이 지금 붙일 수 있다.** 상세 드로어(ledger) 응답에만 없으므로, 목록 행에서 `contract_id`를 넘기면 된다. ledger `select`에 컬럼 1개 추가는 별건의 위생 작업.

### 1-2. 결제 액션 API 실측 시그니처

| 엔드포인트 | 바디 | 게이트 |
|---|---|---|
| `POST /payments/{id}/cancel` | `reason?`, `cancelled_by?` (**contract_id 불필요** — 서버가 payments에서 조회) | 없음, 즉시 가능 |
| `POST /payments/manual/confirm` | `payment_id`, `contract_id` (**둘 다 필수**) | 없음, 즉시 가능 |
| `POST /payments/{id}/refund` | `reason`, `cancelled_by` | **B-1 (이니시스 실환불)** |
| `POST /payments/{id}/partial-refund` | `amount`, `reason`, `cancelled_by` | **B-1** |
| `POST /payments/{id}/invoice/tax` | `corpNum`, `corpName`, `ceoName`, `email?`… | **A-2 (팝빌)** |
| `POST /payments/{id}/invoice/cash` | `trade_usage`, `identity_num`, `by?` | **A-2** |
| `POST /payments/{id}/credit` | `diagnosis_purchase_id?`, `amount?`, `memo?`, `by?` | 없음 |

### 1-3. 백엔드 지뢰 — 환불 라우트 중복 정의

`POST /payments/{payment_id}/refund` 가 **두 곳에 정의**돼 있다.

- `routers/payment.py` → 바디 `reason`, **`cancelled_by`**
- `routers/payment_ledger.py` → 바디 `reason`, **`by`**

`router_registry/payment.py` 로드 순서(`payment` → `payment_test` → `payment_ops` → `payment_ledger`)상 FastAPI 선등록 우선으로 **실제 동작하는 것은 `payment.py`(`cancelled_by`)** 이고, `payment_ledger.py` 정의는 사문(死文)이다.

부분환불도 URL이 두 개 공존한다: `/payments/{id}/partial-refund` (payment.py) vs `/payments/{id}/refund/partial` (payment_ledger.py).

**위험**: 프론트가 `payment_ledger.py`의 스펙(`by`)을 보고 구현하면 **처리자 정보가 조용히 누락**된다. 에러가 나지 않으므로 발견이 늦다. 환불 UI 착수 **전에** 정리해야 한다.

### 1-4. 자동화 엔진 — 백엔드 완비 / 프론트 부재

`routers/automation.py` (prefix `/automation`, `external.py`에 등록됨) 6엔드포인트:

`GET /automation/rules` · `POST /automation/rules` · `PATCH /automation/rules/{id}/toggle` · `POST /automation/fire` · `GET /automation/runs` · `POST /automation/runs/{run_id}/approve`

- 이벤트: `mail.inbound`, `payment.failed`, `payment.success`, `subscription.expiring`, `manual`
- 액션: `SEND_MAIL`, `SEND_SMS`, `CREATE_TASK`, `CALL_WEBHOOK`, `LLM_DRAFT`
- 실행상태: `SKIPPED / APPROVAL_PENDING / RUN / APPROVED_RUN / FAILED`
- 테이블: `automation_rule`, `automation_run_log`

**갭 3가지**

1. **어드민에 automation 화면이 없다.** `pages/` 84개 slug 중 자동화 계열 0개. → 관제홈 `approval_pending`에 링크가 없는 근본 원인.
2. **자동 발화 결선이 `mail.inbound` 1건뿐.** `payment.failed`, `subscription.expiring`은 코드상 발화 지점이 없어 수동 `POST /automation/fire`로만 동작.
3. `CREATE_TASK`·`LLM_DRAFT`는 반환값만 있는 **스텁**(실제 적재/호출 없음).

### 1-5. CRM 축

**통합검색** — 백엔드 `GET /search?q=&types=&limit=` 정상. 반환 `{type, id, title, subtitle, company_id}`, 대상 `company/user/factory/payment`.

프론트 `layouts/components/NavSearchBar.vue`는 **존재하지만 어느 레이아웃에도 포함돼 있지 않다**(`DefaultLayoutWithHorizontalNav.vue`·`WithVerticalNav.vue` 모두 미import). 게다가 내용이 **Vuexy 템플릿 원본 그대로**로, `useApi('/app-bar/search')` fake-db를 호출하고 제안 목록이 `dashboards-analytics`·`apps-calendar` 등 **이 프로젝트에 존재하지 않는 route name**을 참조한다.

> **주의**: 이 컴포넌트를 그대로 navbar에 붙이면 존재하지 않는 route resolve 실패로 **무한로딩 사고(커밋 4d19138)가 재발**할 수 있다. 반드시 TAI용으로 재작성한다.

**고객360** — 백엔드 `GET /companies/{id}/360`, `GET /companies/{id}/factory-billing` 존재·등록됨. 반환 키:
`company, counts, payments, subscription, diagnosis, credit_balance, invoices, refunds, recent_audit, onboarding, billing`

**갭**

- **프론트 화면 0개** (customer360 계열 slug 없음)
- 응답에 **`inquiries`(문의) 없음**, **`contracts`(계약) 없음**
- `payments`는 집계 요약(`count/success_count/total_amount/last_paid_at`)뿐, **건별 이력 없음**
- `onboarding = None` 하드코딩(주석: WO-17 전까지 null)인데 `routers.onboarding_ops`는 이미 등록됨 → 연결 미완

→ 골 PASS 기준 "고객의 결제·문의·계약 이력이 한 화면"은 **현재 API로 충족 불가**. 백엔드 보강이 필수.

### 1-6. 그 외 결손

- **문의 답장**: `PATCH /admin/inquiries/{id}`가 `answer` 저장 + `replied_at` 기록까지만. **고객에게 실제 발송하는 로직 없음.** 발송하려면 `POST /notify/send`를 별도 호출해야 하며 자동 연동이 없다.
- **감사로그 조회 API 없음**: `services/audit_svc.py`는 있고 6개 서비스가 기록하지만 `routers/`에 참조 0건. 노출은 고객360의 `recent_audit` 10건뿐. → **운영 처리 이력을 어드민에서 추적할 수 없다.**
- **관제홈**: `GET /ops/home` 조회 전용. 처리대기 3항목 중 `unread_inbound_mail`만 `/mail-list` 이동, `approval_pending`·`vbank_waiting`은 링크조차 없음.

### 1-7. 위생 이슈 (사고 예방)

| 항목 | 내용 |
|---|---|
| 리포트 3중 중복 | `report-v1`, `report-v1-viewer`, `report_v1` 셋 다 메뉴 노출. 과거 `report-v1-legacy` 오타로 무한로딩 발생 이력 |
| `engine-legal-ai` 중복 | 개발자도구에 동일 route가 query만 달리 2회 등록 |
| 도달 불가 화면 18개 | 메뉴 주석 처리로 URL 직접입력으로만 접근 (매칭·위험·미서비스 계열) |
| payment-ledger 데드코드 | `selected`/`allSelected` 체크박스가 어떤 액션에도 미연결 |
| 전역변수 오염 | 대소문자 중복 카테고리 다수, `test`·`testaa`·빈문자열 카테고리, `subscription_status` 부재 |

---

## 2. 갭 → 작업 매핑

우선순위는 **(a) 운영 정지 리스크 (b) 골 PASS 기여도 (c) 선행 의존** 순으로 판정했다.

### P0 — 실운영 개통 (게이트 불필요, 즉시 착수)

| # | 작업 | 층 | 근거 갭 | 비고 |
|---|---|---|---|---|
| P0-1 | **환불 라우트 중복 제거** — `payment_ledger.py`의 `refund`·`refund/partial` 사문 정의 삭제, `payment.py`로 단일화 | BE | §1-3 | **P3-1 착수 전 필수 선행.** 지금 하면 삭제만 |
| P0-2 | 결제원장 상세에 **결제취소** 액션 | FE | §1-2 | `payment_id`만 필요. 가장 안전 |
| P0-3 | 결제원장 목록에 **수동활성화(입금확인)** 액션 | FE | §1-1 | 목록행 `contract_id` 사용. 백엔드 선행 불요 |
| P0-4 | ledger 응답 `select`에 `contract_id` 추가 | BE | §1-1 | 1컬럼. 상세 드로어에서도 수동활성화 가능해짐 |
| P0-5 | 처리 결과 토스트 + 목록 자동 갱신 + 실패 시 에러 표기 | FE | — | 액션의 완결 조건 |

**P0 완료 시 효과**: 결제원장이 "보는 화면"에서 "처리하는 화면"이 된다. 골 PASS (1) 충족.

### P1 — CRM 개통

| # | 작업 | 층 | 근거 갭 |
|---|---|---|---|
| P1-1 | `customer360_svc` 응답에 **`inquiries`·`contracts` 추가**, `payments`에 최근 건별 목록 추가 | BE | §1-5 |
| P1-2 | `onboarding` 하드코딩 `None` → `onboarding_ops` 실연결 | BE | §1-5 |
| P1-3 | **고객360 화면 신설** (`pages/customer-360/`) — 회사 요약 / 결제·계약·문의 탭 / 감사이력 | FE | §1-5 |
| P1-4 | **NavSearchBar 전면 재작성** — Vuexy 잔재·죽은 route 제거, `GET /search` 연결 | FE | §1-5 |
| P1-5 | navbar에 검색바 장착 + 검색결과 → 고객360 진입 동선 | FE | §1-5 |

**P1 완료 시 효과**: "고객 이름 검색 → 그 고객의 모든 것" 동선 성립. 골 PASS (3) 충족.

> **P1-4 안전수칙**: 재작성 시 route name은 반드시 `pages/<slug>/` 실재 폴더와 대조한다. 미존재 route 참조가 무한로딩 사고의 직접 원인이었다.

### P2 — 자동화 개통

| # | 작업 | 층 | 근거 갭 |
|---|---|---|---|
| P2-1 | **자동화 화면 신설** (`pages/automation/`) — 룰 목록·등록·토글, 실행이력, 승인대기 처리 | FE | §1-4 |
| P2-2 | 관제홈 `approval_pending` → 자동화 승인대기로 연결 | FE | §1-6 |
| P2-3 | 관제홈 `vbank_waiting` → 결제원장(가상계좌 미입금 필터)으로 연결 | FE | §1-6 |
| P2-4 | `payment.failed` · `subscription.expiring` **발화 결선** | BE | §1-4 |
| P2-5 | 문의 답장 시 `POST /notify/send` 연동 (저장→발송) | BE+FE | §1-6 |

**P2 완료 시 효과**: 처리대기가 실처리로 연결되고, 결제실패·구독만료가 자동 대응된다. 골 PASS (2) 충족.

### P3 — 게이트 이후 / 후속

| # | 작업 | 게이트 |
|---|---|---|
| P3-1 | 환불(전액·부분) UI + 실호출 | **B-1** 첫 실결제 검증 |
| P3-2 | 세금계산서·현금영수증 발행 UI + 실호출 | **A-2** 팝빌 |
| P3-3 | 크레딧 발행 UI | 없음(우선순위 낮음) |
| P3-4 | **감사로그 조회 API 신설 + 화면** | 없음 |
| P3-5 | 전역변수 정합성 교정(대소문자 중복 정본 확정, `test` 삭제, `subscription_status` 신설) | 없음 |
| P3-6 | 위생: 리포트 3중 중복 정리, `engine-legal-ai` 중복 제거, 도달불가 18화면 처분 | 없음 |
| P3-7 | `CREATE_TASK`·`LLM_DRAFT` 스텁 실구현 | 없음 |

---

## 3. 실행 순서 (의존 반영)

```
P0-1(BE 중복제거) ──┐
P0-2 취소 ──────────┤
P0-3 수동활성화 ────┼─► P0 배포·검증
P0-4 ledger 보강 ───┤
P0-5 토스트/갱신 ───┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
P1-1/1-2 (BE 보강)        P1-4 검색바 재작성
        ▼                       ▼
P1-3 고객360 화면 ◄──────  P1-5 navbar 장착·동선
        └───────────┬───────────┘
                    ▼
              P1 배포·검증
                    ▼
P2-1 자동화 화면 ─► P2-2/2-3 관제홈 연결 ─► P2-4/2-5 결선
                    ▼
              P2 배포·검증
                    ▼
              P3 (게이트 해제 후)
```

---

## 4. 준수 규칙 (작업 시 필수)

**3계층 아키텍처** (정본 `docs/WORKPLAN_object-oriented-3layer_20260721.md`)

- API 접근은 **ApiClient(`useTaiApi`)** 를 통해서만
- 코드값(상태값) 조회는 **SystemCodesStore(`useSystemCodesStore.get()`)** 를 통해서만 — **하드코딩 금지**
- 화면 구성: `index.vue` + `use<Xxx>.ts` composable (현행 표준 패턴)
- 컴포넌트 간 내부 ref 직접참조 금지 (props/emit/공개반환값만)
- build·typecheck 통과 필수

**신규 화면 신설 시 (P1-3, P2-1)**

- 새 slug 생성 → `navigation/horizontal/index.ts`에 등록 시 **route name을 실재 폴더명과 반드시 대조**
- 필터/선택 옵션은 처음부터 전역변수 조회로 작성 (유형A 위반 재발 방지)

**작업 원칙**

- 실측 없이 가정 금지
- 완료판정은 `IMPLEMENTED / VERIFIED / DONE / PENDING` 만. 검증 없는 완료선언 금지
- INSERT는 `ON CONFLICT DO NOTHING`
- 카카오 API 전면금지

**배포 확인**

- Cloudflare Pages `tai-admin-admin-vue3`, 프로덕션 브랜치 `feat/admin-rebuild`
- tai-api는 `main` push → Railway 자동배포

---

## 5. 미확인 항목 (진행 중 확인 필요)

| 항목 | 상태 |
|---|---|
| `router_registry` 6개 그룹 내역 (legal_engine / document_engine / runtime_bridge / inspection / diagnosis / construction) | 미확인 |
| `notification_*_api.py` 6개 파일의 등록 여부 | 미확인 |
| `pages/index/index.vue`의 `definePage` route name (`root` 여부) | 미확인 |
| guri-cf `github_get_file`이 요청 경로와 무관한 파일을 반환한 사례 1건 | 재현 시 `github_api` contents로 교차검증 |

---

## 6. 참조

- `HANDOFF_session-20260729_v1.md` — 선행 세션 핸드오프
- `WORKPLAN_object-oriented-3layer_20260721.md` — 3계층 규칙 정본
- `RUNBOOK_human-gates_v1.md` — 사람 게이트 (A-2 팝빌, B-1 이니시스)
- 워크오더: WO-6 고객360 · WO-7 결제원장 · WO-11 통합검색 · WO-12 자동화엔진 · WO-13 관제홈 · WO-17 온보딩
