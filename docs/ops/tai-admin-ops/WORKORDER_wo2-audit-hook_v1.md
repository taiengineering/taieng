---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-2 AuditHook — 관리자 운영 감사로그 활성화
version: 2
status: ACTIVE
owner: taiwang
---

# WO-2 — AuditHook (운영 감사로그 admin_ops_audit_logs + 위험조작 훅)

- **작성일:** 2026-07-28 (v2: 별도 테이블 A안 채택·검증 반영)
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-2
- **오브젝트:** AuditHook (도메인 서비스)
- **닫는 시나리오:** S32("누가 이 환불을 처리했나" 추적)
- **최종 상태:** 코드·배포·스키마·기록 **VERIFIED**.

---

## 0. 중요 실측 — admin_audit_logs는 재사용 불가(엔진 전용)

정밀분석에서 "admin_audit_logs 1건 = 미가동"이라 봤으나, 실측 결과 **문서 리뷰 엔진 전용 테이블**이었다. `action` 컬럼에 CHECK 제약이 걸려 있어 엔진 어휘만 허용:
`REVIEW_STARTED, REVIEW_APPROVED, REVIEW_REJECTED, FAMILY_CREATED, TOKEN_ADDED, RULE_APPROVED, REPROCESSING_TRIGGERED, ROLLBACK_EXECUTED, REFERENCE_LINKED, ATTACHMENT_LINKED, ESCALATED, KEEP_AS_UNKNOWN, REJECT_NON_ACTIONABLE`

→ REFUND_FULL 등 운영 action 삽입 시도가 CHECK 위반으로 거부됨(실측). 이대로면 best-effort 훅이 조용히 실패해 감사가 안 남는다.

**결정(A안): 운영 감사 전용 테이블 신설.** 엔진 감사(admin_audit_logs)와 운영 감사를 분리. 운영 테이블은 action 자유 어휘.

## 1. 신설 테이블 admin_ops_audit_logs (적용·검증 완료)

```sql
CREATE TABLE public.admin_ops_audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id uuid, action text NOT NULL, entity_type text NOT NULL, entity_id uuid,
  before_data jsonb, after_data jsonb, created_at timestamptz NOT NULL DEFAULT now()
);
-- idx: (entity_type,entity_id), action, created_at DESC
```
- 마이그레이션 git 고정: `20260728141759_create_admin_ops_audit_logs.sql`
- Supabase 적용 완료(RLS off — payments 계열 일관, service_role 전용).
- 검증: 8컬럼·인덱스4 생성, `REFUND_FULL` action+jsonb 삽입 성공(엔진 테이블에선 막히던 것), 삭제 후 residual 0.

## 2. 오브젝트 계약 (구현 완료)

```
record(action, entity_type, entity_id=None, actor_id=None, before=None, after=None) -> Optional[audit_id]
```
- best-effort: 예외 삼킴+로그. 감사 실패가 환불을 롤백시키지 않음.
- 대상 테이블: `admin_ops_audit_logs`(엔진 전용 admin_audit_logs 사용 금지).
- 구현: `services/audit_svc.py`.

## 3. RefundService 배선 (완료)

`refund_svc.run_refund`/`run_partial_refund` 성공·실패 양쪽에서 `audit_svc.record`:
- action: `REFUND_FULL` / `REFUND_PARTIAL`, entity_type: `payment`, entity_id: payment_id
- before: {status_code, cumulative_done}, after: {refund_id, amount, status, result_code, (payment_status)}
- actor_id: cancelled_by

## 4. 액션 어휘 (표준 — 이후 WO 공용)

| action | 발생 |
|---|---|
| REFUND_FULL / REFUND_PARTIAL | WO-1(배선완료) |
| PAYMENT_MANUAL_CONFIRM | WO-7 |
| MEMBER_UPDATE / MEMBER_SUSPEND / MEMBER_DELETE | WO-6 |
| CREDIT_GRANT | WO-3 |
| DATA_SOFT_DELETE / DATA_RESTORE | WO-5 |

## 5. 검증 결과 (2026-07-28, MCP 실측)

| 항목 | 상태 | 근거 |
|---|---|---|
| admin_audit_logs 재사용 불가 판정 | VERIFIED | CHECK 제약 실측(엔진 어휘 13종만) |
| admin_ops_audit_logs 신설 | VERIFIED | 마이그레이션 git 고정 + Supabase 적용 + 8컬럼·idx4 확인 |
| REFUND_FULL 기록 가능 | VERIFIED | 삽입 성공(엔진 테이블 거부와 대비), residual 0 |
| audit_svc.py 구현 | VERIFIED | 커밋 15705a34 |
| refund_svc 배선 | VERIFIED | 커밋 80bd420 |
| Railway 배포 | VERIFIED | 배포 SUCCESS(15705a34) + `/health` 통과 |
| 실환불 감사행 생성 | PENDING | 실결제 환불 발생 시 자동 기록(코드 경로 검증됨) |

## 6. 산출물 (전부 커밋)

1. `supabase/migrations/20260728141759_create_admin_ops_audit_logs.sql` (적용됨)
2. `services/audit_svc.py` (신설, admin_ops_audit_logs 기록)
3. `services/refund_svc.py` (REFUND_* 배선)
