---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-2 AuditHook — 관리자 행위 감사로그 활성화
version: 1
status: ACTIVE
owner: taiwang
---

# WO-2 — AuditHook (admin_audit_logs 활성화 + 위험조작 훅)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P0 WO-2
- **오브젝트:** AuditHook (도메인 서비스, 상태 PARTIAL → IMPLEMENTED)
- **닫는 시나리오:** S32("누가 이 환불을 처리했나" 추적)
- **선행 결선:** WO-1 RefundService가 첫 소비자(환불이 감사에 남아야 P0 감사 요건이 닫힘)

---

## 1. 현황 (실측 확정)

- `admin_audit_logs` 테이블 **존재**(1건). 스키마:
  `id(uuid), actor_id(uuid,null), action(text,NN), entity_type(text,NN), entity_id(uuid,null), before_data(jsonb), after_data(jsonb), created_at(tz,now())`
- 잘 설계돼 있으나 **어디서도 기록하지 않음** = 사실상 미가동.
- 동종 감사: `document_binding_audit_log`, `document_schema_audit`(문서엔진 전용, 별개).

## 2. 오브젝트 계약 (WORKPLAN §2-A 고정)

```
record(actor, action, entity_type, entity_id, before=None, after=None) -> audit_id
```
- 실패해도 본 작업을 막지 않는다(감사 실패가 환불을 롤백시키면 안 됨 → best-effort, 예외 삼킴+로그).
- service_role로 INSERT(RLS 무관). actor 미상이면 NULL 허용.

## 3. 구현

### 3-1. `services/audit_svc.py` (신설)
```
def record(action, entity_type, entity_id=None, actor_id=None, before=None, after=None) -> Optional[str]:
    try: INSERT admin_audit_logs(...) return id
    except: log.warning(...); return None   # best-effort
```

### 3-2. RefundService 배선 (WO-1 결선)
- `refund_svc.run_refund`/`run_partial_refund` 성공·실패 시점에 `audit.record`:
  - action: `REFUND_FULL` / `REFUND_PARTIAL`
  - entity_type: `payment`, entity_id: payment_id
  - before: {status_code, cumulative_done}, after: {refund_id, amount, status, inicis_result_code}
  - actor_id: cancelled_by(있으면)
- best-effort라 환불 성공 여부와 독립.

## 4. 액션 어휘 (표준화 — 이후 WO들이 동일 규약 사용)

| action | 발생 지점 |
|---|---|
| REFUND_FULL / REFUND_PARTIAL | WO-1 환불 |
| PAYMENT_MANUAL_CONFIRM | 수동 활성화(WO-7) |
| MEMBER_UPDATE / MEMBER_SUSPEND / MEMBER_DELETE | 회원 조작(WO-6) |
| CREDIT_GRANT | 크레딧 발행(WO-3) |
| DATA_SOFT_DELETE / DATA_RESTORE | 휴지통(WO-5) |

이번 WO는 서비스 오브젝트 + REFUND_* 2종 배선까지. 나머지 action은 각 WO에서 동일 `audit.record`로 추가.

## 5. 완료 판정 (IMPLEMENTED)

- `audit_svc.record` 구현, best-effort(예외 삼킴).
- refund_svc 성공/실패 양쪽에서 record 호출.
- 배포 후 `/health` 200, 실제 감사행이 admin_audit_logs에 쌓이는지는 실환불 발생 시(또는 테스트 record 1건) 확인.

## 6. 산출물

1. `services/audit_svc.py` (신설)
2. `services/refund_svc.py` (record 배선 추가)
