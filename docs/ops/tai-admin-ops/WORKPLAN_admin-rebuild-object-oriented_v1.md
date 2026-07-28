---

class: plans
type: WORKPLAN
scope: ops
project: tai-admin-ops
title: TAI 어드민 재구성 구축 작업계획 — 오브젝트 3층 방식
version: 1
status: ACTIVE
owner: taiwang
---

# TAI 어드민 재구성 구축 작업계획 v1 — 오브젝트 3층 방식

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **선행:** PLAN_admin-rebuild_v3.md (정본 기획, 37시나리오 통과)
- **성격:** 기획 v3의 6 ZONE·확장6종을 **오브젝트+계약 방식**으로 구축하기 위한 작업계획. 45cm 3층 방법론(공유 오브젝트/Page 오브젝트/공개 계약, CONFIRMED·PARTIAL·REJECTED, IMPLEMENTED·VERIFIED)을 어드민 운영체계에 적용.

---

## 1. 원칙 (변경 없음, 45cm 3층 계승)

- UI·기능은 **오브젝트로 제작되고 자기 의미를 소유**한다. 오브젝트 간 연결은 **공개 계약(인터페이스)으로만** 이루어진다.
- 동일 연결은 재사용한다. 외부 자산(이니시스/MessageMi/Vuexy)은 오브젝트 구현 **내부에 내장**되고 공개 계약에는 노출되지 않는다.
- **섣부른 공통화 금지.** 데이터포인트 2개 미만이면 공유 오브젝트로 승격하지 않는다(REJECTED 유지, 재검토 조건 명시).
- 결제상태·법령자산은 **원천을 읽고 되쓴다**(어드민 DB 복제 금지). GPT 엔진 자산 격리.

---

## 2. 오브젝트 모델 — 3층

이번 구축은 프론트 이식이 아니라 **백엔드 도메인 + 어드민 화면 신규 구축**이므로 오브젝트를 3층으로 나눈다.

### 2-A. 도메인 서비스 오브젝트 (백엔드, tai-api)

| 오브젝트 | 공개 계약 | 구현 위치 | 상태 |
|---|---|---|---|
| **RefundService** | `run_refund(payment_id, reason, by)`, `run_partial_refund(payment_id, amount, reason, by)` → refunds 기록 + 이니시스 실호출 | `services/payment_svc.py`(501 교체) + `services/refund_svc.py` | PARTIAL — 시그니처는 있음, 본문이 `raise 501`. 본문 구현 대상 |
| **CreditLedger** | `grant(company_id, amount, source, expires_at)`, `apply(credit_id, payment_id)`, `balance(company_id)` | `services/credit_svc.py`(신설) | REJECTED-as-existing → 신설 |
| **AuditHook** | `record(actor, action, entity, before, after)` | `services/audit_svc.py` + 미들웨어 | PARTIAL — 테이블 존재(1건), 훅 미배선 |
| **InvoiceService** | `issue(payment_id)`, `reissue(invoice_id)`, `status(payment_id)` | `services/invoice_svc.py`(신설) | 신설 |
| **SoftDelete** | `soft_delete(table, id, by)`, `restore(table, id)`, `list_trash(table)` | `services/soft_delete_svc.py` + `deleted_at` 컬럼 | 신설(컬럼 DDL 선행) |
| **NotifyDispatcher** | `send(channel, target, template_id, params)` — SMS/MAIL/PUSH 단일 진입 | 기존 messaging·mail·fcm 래핑 | CONFIRMED-as-existing — 래핑만 |
| **AutomationEngine** | `register_rule(rule)`, `fire(event, payload)` → 액션 인터페이스 | `services/automation_svc.py` + event_trigger | PARTIAL — event_trigger 존재, 규칙엔진 미배선 |
| **StatsProvider** | `kpi_daily()`, `funnel()`, `settlement(month)` | admin_stats + 집계 뷰 | PARTIAL — admin_stats 존재, 뷰 신설 |

**액션 인터페이스(계약 고정 — 후행 결합 지점):**
`Action = {type, params}`, type ∈ `SEND_SMS|SEND_MAIL|SEND_PUSH|CALL_WEBHOOK|CREATE_TASK|LLM_DRAFT|AGENT_RUN|MACRO`. AutomationEngine은 이 계약만 알고, LLM/에이전트/매크로는 **새 type 등록으로만** 추가(엔진 개조 금지).

### 2-B. 공유 UI 오브젝트 (프론트, admin)

| 오브젝트 | 공개 계약 | 상태 |
|---|---|---|
| **ApiClient** | `request(method, endpoint, body?)`, `list(endpoint)` | CONFIRMED(safe 이식서 검증 자산 재사용) |
| **SystemCodesStore** | `get(categories)` | CONFIRMED |
| **Toast** | `show(type, message)` | CONFIRMED |
| **Auth** | `requireAuth()`, `role` | CONFIRMED |
| **RowSelection** | `allChecked/someChecked/toggleAll/toggleOne/isChecked` | CONFIRMED — 리스트 페이지 필수(첫 컬럼 전체선택 체크박스) |
| **GlobalSearch(⑮)** | `search(q)` → 회원·결제·문의 교차 | 신설 |
| **AuditViewer(③)** | `query(filters)` → v_audit_unified | 신설 |
| **DryRunPreview** | `preview(rule|blast)` → 대상수·샘플 | 신설(대량발송 안전장치) |

> Panel/ListView는 safe 이식서에서 REJECTED-as-공유(데이터포인트 부족). 어드민에서도 동일 관례 유지 — 페이지별 `useXxxList`/`useXxxPanel` 관례로 재사용, 강제 공유 클래스 금지. 두 번째 데이터포인트 생기면 재검토.

### 2-C. Page 오브젝트 (화면마다 자기완결)

각 화면 = 상태 스토어 + 데이터 로딩 composable + 화면 컴포넌트. 페이지 특화 하위 오브젝트는 해당 페이지 디렉토리 내부. 리스트 페이지 필수: (1) 첫 컬럼 전체선택 체크박스, (2) 둘째 컬럼 No.

---

## 3. 완료 판정 (IMPLEMENTED / VERIFIED)

**IMPLEMENTED** (백엔드 오브젝트):
1. 공개 계약 시그니처대로 구현, `raise 501` 잔존 없음
2. 원천 읽기/되쓰기(어드민 DB 복제 없음), CONFIRMED 레코드 불변
3. 모든 쓰기 액션이 AuditHook 경유
4. `/health` 200 유지, DDL은 `apply_migration`·DML은 `execute_sql`

**IMPLEMENTED** (프론트 Page):
1. 원본/대상 정독 후 구현, `window.` 직접대입·인라인 onclick 없음
2. API는 ApiClient만, 코드값은 SystemCodesStore만
3. 리스트 필수 2컬럼 규칙 준수

**VERIFIED**: 위 + 실제 실행 확인. **페이지마다 요청하지 않고 각 P단계 마감 시 일괄 검증.**

- 금지: "100% 완료"·"사실상 PASS" 등 검증 없는 완료 선언. 상태는 IMPLEMENTED/VERIFIED/UNKNOWN만.

---

## 4. 구축 순서 — WO 단위 (기획 v3 §6 대응)

각 WO는 오브젝트 1~2개를 IMPLEMENTED까지. 격리 자산 제외, 살아있는 연결만.

### P0 — 골 통과 필수 (유료 고객 대응 전제)
- **WO-1 RefundService**: refunds DDL → `run_refund`/`run_partial_refund` 이니시스 실연동(`iniapi/refund`) → 누적환불 검증 → AuditHook. (S3·S4·S5)
- **WO-2 AuditHook**: `admin_audit_logs` 활성화 + 결제/회원/삭제/크레딧 쓰기 전구간 미들웨어. (S32)
- **WO-3 CreditLedger**: credits DDL + grant/apply/balance. (S6)
- **WO-4 InvoiceService**: 세금계산서 status DDL + issue/reissue. (S31 선행)
- **WO-5 SoftDelete**: 대상 테이블 `deleted_at` DDL + soft_delete/restore/trash. (S11)

### P1 — 상시 운영
- **WO-6 고객360 Page** (+온보딩 상태⑱ 표시): 원천 뷰 집계. (S1·S7·S8·S13·S37)
- **WO-7 결제·구독 원장 Page**: RefundService·CreditLedger·InvoiceService 결선 + 구독수명주기. (S2·S24)
- **WO-8 NotifyDispatcher + 발송센터/발송설정 Page**: 3채널 단일화 + DryRunPreview. (S25·S26)
- **WO-9 파일/자산 통합뷰(⑬)**: v_files_unified. (S34)
- **WO-10 웹훅/연동 상태(⑭)**: 레지스트리+probe 승격 + 프록시 probe 신규. (S19·S35)
- **WO-11 GlobalSearch(⑮)**: 교차검색 API + 상단 검색바. (S36)

### P2 — 자동화·관제·재무
- **WO-12 AutomationEngine + 자동화규칙 Page**: 액션 인터페이스 + require_approval + run_log. (S27·S28)
- **WO-13 관제 홈 Page**: 처리 대기 큐 + 상태판(probe 집계) + KPI. (S17~S20)
- **WO-14 StatsProvider + 통계 대시보드/퍼널 Page**: 집계 뷰. (S29)
- **WO-15 정산·세무 리포트(②)**: settlement 집계 + export. (S31)
- **WO-16 공지·배너(⑫)**: notice DDL + 게시 Page + probe→배너 자동화. (S33)
- **WO-17 온보딩 체크리스트(⑱)**: onboarding DDL + 넛지 자동화. (S37 완결)

### P3 — 성장·정리
- **WO-18 마케팅엔진 1.2 결선**: ZONE2 발송레이어 위 결선(담당 산출물 대기).
- **WO-19 메뉴 정리**: 미서비스26+엔진23 제거·분리.
- **WO-20 Vue3 이식**: 정리 후 26페이지 범위.

---

## 5. WO 착수 규약

- WO 문서는 단계별 번호 지정, 격리 자산 제외, 살아있는 연결만 확인. Cursor 핸드오프가 필요한 대형 파일(200줄+/20KB+)은 Router/Service/Schema/Tests 분리(한 파일 400줄·15KB 이내).
- INSERT는 `ON CONFLICT DO NOTHING`. CONFIRMED 레코드 불변. DDL `apply_migration`, DML `execute_sql`.
- 배포 확인 `/health` 200. 문서는 `taieng/docs/ops/tai-admin-ops/`에만.
- 각 WO는 이 계획서의 오브젝트 계약(§2)을 변경하지 않는다. 계약 변경이 필요하면 이 계획서를 먼저 개정(vN+1).

---

## 6. 첫 착수: WO-1 (RefundService)

P0 최상단. refunds 대장 DDL → payment_svc의 `raise 501` 2개를 이니시스 실연동으로 교체 → AuditHook 경유 → 부분환불 누적 검증. 구축 지시 시 WO-1 상세 문서부터 작성.
