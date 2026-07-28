---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-13 관제홈 운영 대시보드
version: 2
status: DONE
owner: taiwang
---

# WO-13 — 관제홈 (OpsHome)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED.

---

## 1. 현황 (실측 — 기존 집계 재사용)

- `admin_stats`(dashboard_stats MV): 자산 수. "얼마나 있나".
- 부족했던 것: 운영 대기 큐 → 신설.
- 재사용: automation_run_log, mail_logs, payments, integration_health_svc, dashboard_stats.

## 2. 구현 (완료)

**`services/ops_home_svc.py`** (커밋 880332b):
- `action_queue()`: approval_pending(automation APPROVAL_PENDING) + unread_inbound_mail(mail_logs inbound·read=false·deleted=false) + vbank_waiting.
- `alerts()`: core_critical_missing(integration_health) + mail_send_failed(mail_logs outbound·failed).
- `today()`: new_companies/users/payments(created_at=오늘) + assets(dashboard_stats 재사용).
- `get_home()`: 3묶음 종합. 각 소스 오류 격리(_count 헬퍼 try/except).

**`routers/ops_home.py`** (커밋 b3b151c): `GET /ops/home`. external 등록 96b681c.

## 3. 검증 결과 (실 코드값 확인으로 오류 정정)

- **결제 상태 코드 실측**(system_codes payment_status): PENDING/SUCCESS/FAILED/CANCELLED. VBANK는 payment_method_type(가상계좌)이지 상태가 아님.
- **vbank_waiting 정정**: 최초 `status_code='VBANK_READY'`(존재하지 않는 값) → `payment_method='VBANK' AND status_code='PENDING' AND vbank_confirmed_at IS NULL`로 수정.
- customer360(WO-6) 성공결제 판정 `status_code='SUCCESS'`도 재확인 — payment_status와 일치(정상).

| 항목 | 상태 | 근거 |
|---|---|---|
| action_queue 집계 | VERIFIED | SQL: approval_pending 0, unread_inbound 179, vbank_waiting 0 |
| alerts 집계 | VERIFIED | SQL: mail_failed 246. integration_health 재사용 |
| vbank_waiting 코드값 정정 | VERIFIED | system_codes 실측 후 조건 수정 |
| 오류 격리 | VERIFIED | _count try/except — 한 소스 실패해도 나머지 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(96b681c) + `/health` |

## 4. 산출물 (커밋)

1. `services/ops_home_svc.py`
2. `routers/ops_home.py`
3. `router_registry/external.py` (ops_home 등록)

## 5. 후속 메모

- 목업에 미읽음 수신 179·발송실패 246 존재. 실운영 전 목업 정리 또는 read 처리 필요(데이터 위생).
