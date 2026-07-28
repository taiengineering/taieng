---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-13 관제홈 운영 대시보드
version: 1
status: ACTIVE
owner: taiwang
---

# WO-13 — 관제홈 (OpsHome)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-13
- **오브젝트:** ops_home_svc(신설) + 관제홈 엔드포인트
- **닫는 시나리오:** S13(아침에 열면 오늘 처리할 일이 보인다)

---

## 1. 현황 (실측 — 기존 집계 재사용)

- `admin_stats`(GET /admin/stats): dashboard_stats MV — 회사·시설·계약·회원·진단·점검·설비 **자산 수**. "얼마나 있나".
- 부족: **"지금 대응할 게 뭔가"**(운영 대기 큐)가 없음.
- 재사용 소스: automation_run_log(승인대기), mail_logs(미읽음 inbound·발송실패), payments(입금대기 VBANK·오늘 결제), subscriptions(만료임박), integration_health_svc(필수 연동 미설정), companies/users(오늘 신규).

## 2. 설계 — 운영 대기 큐 + 이상 신호 + 오늘의 숫자

**`services/ops_home_svc.py`(신설):**
- `action_queue()`: 처리 대기 — 승인대기 자동화 수(automation_run_log APPROVAL_PENDING), 미읽음 문의(mail_logs inbound read=false), 입금대기(payments VBANK 미완).
- `alerts()`: 이상 신호 — 필수 연동 미설정(integration_health get_health core_critical_missing), 발송 실패(mail_logs status=failed 최근), 만료임박 구독(subscriptions next_billing_at 임박·payments expiring).
- `today()`: 오늘의 숫자 — 신규 회사·회원·결제(created_at=오늘), 자산 통계(dashboard_stats 재사용).
- `get_home()`: 3개 묶음. 각 소스 읽기만. 오류 격리(한 소스 실패해도 나머지 반환).

## 3. 엔드포인트

- `GET /ops/home` — 관제홈 종합(대기 큐 + 이상 신호 + 오늘의 숫자).

## 4. 완료 판정 (IMPLEMENTED)

- ops_home_svc 3묶음, get_home, 라우터, 등록.
- 각 소스 재사용(신규 집계 없음), 오류 격리.
- `/health` 200, 배포 SUCCESS. 목업 표본으로 종합 응답 확인.

## 5. 산출물

1. `services/ops_home_svc.py`
2. `routers/ops_home.py`
3. router_registry 등록(external)
