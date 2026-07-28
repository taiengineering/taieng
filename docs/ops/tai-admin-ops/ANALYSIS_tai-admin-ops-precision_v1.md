---

class: records
type: ANALYSIS
scope: ops
project: tai-admin-ops
title: TAI 어드민 1인 운영체계 구축 — 정밀분석
version: 1
status: ACTIVE
owner: taiwang
---

# TAI 어드민 1인 운영체계 구축 — 정밀분석 v1

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada (project: tai-admin-ops)
- **대상:** admin.taieng.co.kr (tai-admin 레포 `admin/`)
- **서비스 범위:** 법령진단 · SaaS 2종만. 그 외 메뉴(수선/매칭/전문가/견적/컨설팅/건설/교육 등)는 미서비스로 제외 판정.
- **성공조건:** 향후 발생 가능한 소비자 이슈(결제·환불·계정·데이터·문의) 및 서비스 이슈(장애·발송실패·배치실패)에 어드민 화면만으로 전부 대응 가능.
- **종료조건:** 운영이 가능한 수준.

정밀분석은 **추정이 아니라 실측**으로 수행: GitHub 파일 인벤토리(admin 80페이지 + assets/js), `tai-api/router_registry/*` 및 `routers/payment*.py`·`services/payment_svc.py` 정독, Supabase `vwlahtguyggrhvslabax` 실 카운트.

---

## 1. 실측 — 서비스가 어디까지 살아있는가

| 테이블 | 실건수 | 해석 |
|---|---|---|
| companies | 179 | 목업 다수 포함 추정 |
| users | 20 | 실사용자 거의 없음 |
| payments | 132 | 테스트 위주 |
| subscriptions | 32 | 존재하나 |
| **billing_keys** | **0** | 정기결제(자동청구) 한 번도 안 돎 |
| contracts | 4 | |
| diagnosis_purchases | 16 | 유료진단 |
| **anonymous_diagnosis_results** | **6,062** | **무료진단만 실제 트래픽 존재** |
| inquiries | 3 | |
| notification_queue / logs / deadletter | 0 / 0 / 0 | 알림 레거시 계보 사망 |
| runtime_notification_event | 30,500 | 실제 알림 흐름은 이쪽 |
| cron_job_log | 292,350 | 배치는 돌고 있음 |
| **admin_audit_logs** | **1** | 관리자 행위 감사 미가동 |
| settlements / health_alerts | 0 / 0 | 미사용 |

**핵심:** 살아있는 유일한 퍼널은 익명 무료진단(6,062건). 그 뒤의 유료화·구독·CS 사슬은 전부 비어 있다. "어드민이 미서비스로 채워진 것"이 문제가 아니라, **살아있는 퍼널을 운영할 화면이 어드민에 없는 것**이 진짜 문제.

---

## 2. 어드민 80페이지 재분류

| 구분 | 수 | 처리 |
|---|---|---|
| **A. 운영 필수 (남김)** | 17 | index, member-list, company-list, factory-list, payment-list, contract-list, price-setting, anon-diagnosis-list, diagnosis-step1, inquiry-list, fix-chat-list, identity-verify, notification-center, notification-setting, message-templates, cron-list, system-codes |
| **B. 조건부** | 9 | permission, faq-setting, api-monitor-internal/external, operational-awareness-center, tai-mail, push-test, report-v1 계열(중복정리 후 1) |
| **C. 미서비스 → 메뉴 제거** | 26 | repair2, quote2, matching, expert2, consulting, settlement, kin-management, contract-kmong2, education2, construction5, personnel-list, equipment-list, facility-equipment/process, inspection-list, maps-leaflet 등 |
| **D. 엔진/개발 → 어드민 분리** | 23 | engine-* 11, legal-engine-quality, document-* 4, watch-engine, workflow-registry, auto-qa-dashboard, diagram-gallery, doc-setting 등 |
| **E. 죽은 파일** | 5 | mail-list/mail-send(각 237B 빈 스텁), report_v1/report-v1 중복, auth 중복 |

- **D(23)는 45cm 이관 결정과 겹침.** 법령엔진 의무도출을 45cm로 넘긴 이상 engine-* 화면이 TAI 운영 어드민에 있을 이유 없음 → 별도 도메인/45cm 측 분리.
- **부수효과:** 2026-07-22 admin Vue3 이식 범위 81 → 운영필수17+조건부9 = **26페이지로 축소** = 이식비용 1/3. 정리 없이 이식하면 죽은 화면 55개를 Vue3로 재생산하게 됨.

---

## 3. 결손 (코드 레벨 정독으로 확정)

### P0 — 돈과 법

1. **환불 미구현 (확정).** `services/payment_svc.py`:
   - `run_refund(...)` → `raise PaymentPrepareError(501, "환불 기능은 아직 구현되지 않았습니다.")`
   - `run_partial_refund(...)` → `raise 501`
   - 라우터(`routers/payment.py`)는 `/payments/{id}/refund`·`/partial-refund` 껍데기만 존재.
   - 별개로 `routers/payment_ops.py`의 `/cancel`은 이니시스 호출 없이 DB status만 변경(이중장부 위험). → **취소/환불 경로가 2개로 갈라져 있고 진짜 환불은 미구현.**
   - `refunds` 대장 테이블 없음 → 환불 사유·금액·처리자·PG응답 기록 불가.
2. **전환크레딧 원장 없음.** 가격 V4 "30일 내 SaaS 전환 시 전환크레딧 100%" 정책 → `credits` 테이블 부재. 정책만 있고 실행수단 없음.
3. **admin_audit_logs 미가동(1건).** 결제취소·수동활성화(`/payments/manual/confirm`)·회원수정 등 위험조작이 무기록. 1인이라 오히려 필수(분쟁 시 제3자 없음).
4. **세금계산서 발행 상태 관리 없음.** `invoice_biz_no`/`invoice_email` 필드만 존재. B2B/B2G·조달청 진입 시 즉시 문제.

### P1 — 대응 가능성

5. **고객 360 부재.** 회원→회사→시설→결제→구독→진단→발송→문의를 7개 화면에서 수동 대조. 1인 CS 소요 10배.
6. **구독 수명주기 운영 화면 없음.** 빌링 로직(`run_billing_charge`/`run_billing_cancel`, 실패 3회 PAUSE)은 실연동돼 있으나 billing_keys=0 → 자동갱신 시작 즉시 미수금 관제 불가.
7. **알림 계보 이원화.** `notification_*`(사망) / `runtime_notification_*`(3만건) 공존, deadletter 화면 없음 → "SMS 안 왔어요" 대응 불가.
8. **회원 탈퇴·개인정보 삭제 처리 화면 없음.** 개인정보보호법 대응 불가.

### P2 — 관제

9. 통합 장애 관제(Railway·Supabase·Gotenberg·iwinV프록시·이니시스 상태 한 화면) 부재. `services/health_registry`의 probe는 존재하므로 집계 화면만 필요.
10. 미서비스 26 + 엔진 23 메뉴 제거·분리.

---

## 4. 운영 가능 최소 구성 — 3존, ZONE1만 매일

**ZONE 1 — 운영 (6화면)**

| # | 화면 | 통합대상 | 핵심 |
|---|---|---|---|
| 1 | 관제 홈 | index | 오늘 처리할 것(신규결제/환불요청/미답변문의/실패건) + 상태 6신호등 |
| 2 | 고객 360 | member+company+factory | 검색1회로 전 이력 한 화면 |
| 3 | 결제·구독 원장 | payment+contract | 결제/환불(PG실호출)/세금계산서/전환크레딧/구독수명주기 |
| 4 | 진단 처리함 | anon-diagnosis+diagnosis-step1 | 익명6062 퍼널·유료전환·재실행 |
| 5 | CS 함 | inquiry+fix-chat+tai-mail | 통합 인박스 |
| 6 | 시스템 로그 | cron+api-monitor2 | 배치/알림/에러/관리자감사 |

**ZONE 2 — 설정:** price-setting, system-codes, notification-setting, message-templates, permission, faq-setting
**ZONE 3 — 엔진/개발:** engine-* 23 → 별도 도메인/45cm 이관

---

## 5. 우선순위 (구축계획)

**P0 (유료 고객 받기 전 필수)**
1. 이니시스 취소/환불 실연동(`run_refund`/`run_partial_refund` 구현) + `refunds` 대장 신설(부분환불 누적·사유·처리자·PG응답 원문). `/cancel` 경로와 통합.
2. 전환크레딧 원장(`credits`) 신설.
3. `admin_audit_logs` 실가동(결제/회원/데이터 변경 전구간 훅).
4. 세금계산서 발행 상태 관리.

**P1**
5. 고객 360 화면. 6. 구독 수명주기 운영. 7. 알림 계보 단일화 + deadletter 화면. 8. 회원 탈퇴·개인정보 삭제.

**P2**
9. 관제 홈 + 통합 상태판(health probe 집계). 10. 미서비스26+엔진23 메뉴 정리. 11. Vue3 이식은 정리 이후 26페이지 범위로 착수.

---

## 6. 정정 이력 (정독으로 뒤집힌 판정)

- 1차 판정: "환불은 DB만 바꾸고 PG 미호출" — `payment_ops.py`만 보고 내린 오판.
- 2차 판정: "`payment.py`에 이니시스 환불 실연동됨" — 라우터 껍데기만 보고 내린 오판.
- **최종(확정): `services/payment_svc.py` 정독 결과 `run_refund`/`run_partial_refund` 모두 `raise 501`. 환불 자체가 미구현.**
- 교훈: 라우터 존재 ≠ 기능 존재. 서비스 레이어까지 정독해야 결손 확정 가능.

---

## 7. 다음 단계

이 문서로 **정밀분석·결손식별·우선순위 확정 = 종료조건 충족.** 후속은 P0-1(환불 실연동 + refunds 대장) WO 작성부터. GPT 소관 엔진 자산은 이번 범위 밖(격리 유지).
