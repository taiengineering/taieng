---

class: plans
type: PLAN
scope: ops
project: tai-admin-ops
title: TAI 어드민 1인 운영체계 재구성 기획 — 골 시뮬레이션 통과판
version: 1
status: ACTIVE
owner: taiwang
---

# TAI 어드민 1인 운영체계 재구성 기획 v1 (골 시뮬레이션 통과판)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **선행:** ANALYSIS_tai-admin-ops-precision_v1.md, RESEARCH_saas-admin-benchmark_v1.md
- **골 통과기준(이 기획이 반드시 충족):** 소비자 이슈(결제·환불·계정·데이터·문의) + 서비스 이슈(장애·발송실패·배치실패)에 **어드민 화면만으로 전부 대응 가능**.
- **골 종료조건:** 운영이 가능한 수준.

---

## 0. 운영 모델 — 요일별 배제, 이벤트 기반 단일 처리함

벤치마크의 "요일별 모드"는 **참조만 하고 채택하지 않는다.** 1인이라도 소비자 이슈는 요일을 가리지 않고 발생하므로, 고정 요일제는 결제·환불·장애 대응을 지연시킨다.

**채택 모델: 이벤트 기반 단일 관제 홈(처리 대기함).**
- 운영자는 매일 **관제 홈의 '처리 대기 큐' 하나만 비운다.** 큐가 비면 운영 완료.
- 모든 이슈(신규결제·환불요청·미답변문의·발송실패·배치실패·장애신호)가 유형과 무관하게 이 큐로 수렴한다.
- 각 큐 항목은 **한 번의 클릭으로 처리 화면으로 딥링크**된다(컨텍스트 스위칭 최소화).
- 요일이 아니라 **큐 잔량**이 운영 상태를 정의한다.

---

## 1. 화면 구조 — 3 ZONE, ZONE1만 상시

정밀분석의 6화면을 기준으로, 시뮬레이션(§3)에서 도출된 필수 액션을 각 화면에 배선한다.

### ZONE 1 — 운영 (상시)

| # | 화면 | 통합 대상 | 필수 액션(시뮬레이션 도출) |
|---|---|---|---|
| 1 | **관제 홈** | index | 처리 대기 큐(결제/환불/문의/발송실패/배치실패/장애) + 시스템 상태 신호등 7종 |
| 2 | **고객 360** | member+company+factory | 회원·회사·시설·결제·구독·진단·발송·문의 통합 조회 / 비번재설정 / 계정 정지·재개 / 탈퇴·개인정보 파기·열람(export) / **휴지통 복구** |
| 3 | **결제·구독 원장** | payment+contract | 전체환불·부분환불(PG 실호출) / 전환크레딧 / 세금계산서 발행·재발행 / 구독 수명주기(재청구·독촉·해지) / 수동활성화 / VBANK 확인 / 이의제기 상태 |
| 4 | **진단 처리함** | anon-diagnosis+diagnosis-step1 | 익명 6,062건 조회 / 유료 전환 / 진단 재실행 |
| 5 | **CS 함** | inquiry+fix-chat+tai-mail | 통합 인박스 / 답변 / 고객360·결제원장 딥링크 |
| 6 | **시스템 로그** | cron+api-monitor2 | 배치 실패 필터·재실행 / 알림 deadletter 재발송 / **관리자 감사로그** |

### ZONE 2 — 설정 (가끔)
price-setting, system-codes, notification-setting, message-templates, permission, faq-setting

### ZONE 3 — 엔진/개발 (분리)
engine-* 23 → 45cm 이관 또는 별도 도메인. TAI 운영 어드민에서 제외.

---

## 2. 데이터 모델 (신설·활성화 대상)

시뮬레이션 통과에 필요한 최소 스키마. 기존 자산은 원천으로 읽고, 아래만 신설한다.

### 2-1. `refunds` (신설) — P0
```
id, payment_id(FK), refund_type(FULL|PARTIAL), amount,
cumulative_refunded, reason_code, reason_text,
inicis_refund_tid, inicis_raw(jsonb), status(REQUESTED|DONE|FAILED),
processed_by, created_at
```
- 규칙: 한 payment에 다건 허용, `cumulative_refunded ≤ payments.total_amount` 강제. 사유 필수.
- `run_refund`/`run_partial_refund`의 `raise 501`을 이니시스 `iniapi/refund` 실호출로 교체하고 이 대장에 기록.

### 2-2. `credits` (신설) — P0
```
id, company_id(FK), source(DIAGNOSIS_CONVERT|MANUAL), amount,
balance, expires_at, applied_payment_id, status(ACTIVE|USED|EXPIRED),
created_by, created_at
```
- 가격 V4 "30일 내 SaaS 전환 시 전환크레딧 100%" 실행 수단.

### 2-3. `admin_audit_logs` (기존 활성화) — P0
- 이미 존재(1건). 결제취소·환불·수동활성화·회원수정·데이터삭제·크레딧 발행 전 구간에 훅 삽입.
- before_data/after_data/actor_id/action/entity 불변 기록.

### 2-4. 세금계산서 상태 (신설 컬럼 또는 `tax_invoices`) — P0
```
payment_id(FK), biz_no, email, status(PENDING|ISSUED|CANCELLED),
issued_at, issue_tid, reissue_of
```

### 2-5. soft delete / 휴지통 (신설) — 시뮬레이션 신규 갭
- **현황 실측:** companies/factories/users/company_contacts 모두 `is_active`만 존재, **`deleted_at` 없음** → 삭제 시점·복구 불가.
- 조치: 대상 테이블에 `deleted_at timestamptz NULL` 추가. 삭제=soft(=deleted_at 세팅), 고객360 "휴지통" 탭에서 30일 내 복구.

---

## 3. 골 시뮬레이션 — 통과기준 대비 시나리오 검증

통과기준의 8개 이슈 유형별로 구체 시나리오를 만들고, **어드민만으로 끝까지 처리 가능한지** 판정한다. GAP은 §1·§2에서 이미 닫은 항목.

### 소비자 이슈

| # | 시나리오 | 처리 경로(화면→액션→데이터) | 판정 |
|---|---|---|---|
| S1 | 카드 승인됐으나 서비스 미활성(후처리 실패) | 고객360서 결제 SUCCESS/service_status 불일치 확인 → 결제원장 수동활성화(manual/confirm) | PASS |
| S2 | 가상계좌 입금했는데 미반영 | 결제원장 VBANK 상태조회 → 수동확인 | PASS |
| S3 | 이중결제 | 고객360서 중복 식별 → 결제원장 전체환불(refunds) | PASS(§2-1) |
| S4 | 7일 내 청약철회 | 결제원장 전체환불 → 이니시스 실호출 → refunds 기록 | PASS(§2-1) |
| S5 | 사용분 차감 부분환불 | 결제원장 부분환불 → 누적환불액 검증 | PASS(§2-1) |
| S6 | 진단→SaaS 30일 내 전환크레딧 | 결제원장 크레딧 발행·적용 | PASS(§2-2) |
| S7 | 로그인 불가/비번 재설정 | 고객360 비번재설정 액션 | PASS(§1) |
| S8 | 회원 탈퇴 + 개인정보 파기 | 고객360 탈퇴·파기 처리 | PASS(§1) |
| S9 | 회사·시설 정보 오류 수정 | 고객360(factory/company 편집) | PASS |
| S10 | 미납으로 계정 정지·재개 | 고객360 정지/재개 | PASS(§1) |
| S11 | 고객 실수로 시설 삭제→복구 | 고객360 휴지통 30일 복구 | PASS(§2-5) |
| S12 | 진단 결과 오류→재실행 | 진단처리함 재실행(trigger_diagnosis) | PASS |
| S13 | 개인정보 열람권·데이터 export | 고객360 export | PASS(§1) |
| S14 | 일반 문의 접수·답변 | CS함 답변(inquiries) | PASS |
| S15 | 수리연결 채팅 | CS함(fix_chat 통합) | PASS |
| S16 | 문의가 환불·계정조치로 연결 | CS함→고객360/결제원장 딥링크 | PASS(§1) |

### 서비스 이슈

| # | 시나리오 | 처리 경로 | 판정 |
|---|---|---|---|
| S17 | 결제 불가(이니시스 장애) | 관제 홈 상태판 payment probe(critical) | PASS |
| S18 | PDF 생성 실패(Gotenberg) | 관제 홈 Gotenberg probe | PASS |
| S19 | 프록시(iwinV) 다운→law.go.kr/이니시스 IP 실패 | 관제 홈 프록시 probe(**신규 추가 필요**) | PASS(신규 probe 등록) |
| S20 | DB/Railway 다운 | 관제 홈 인프라 probe | PASS |
| S21 | SMS 미발송(MessageMi 실패) | 시스템로그 알림 deadletter | PASS(§1·P1-7) |
| S22 | 알림 재발송 | 시스템로그 deadletter 재시도 | PASS |
| S23 | cron 배치 실패 | 시스템로그 실패필터·재실행 | PASS |
| S24 | 정기결제 자동청구 실패(3회 PAUSE) | 구독 수명주기 + 시스템로그 | PASS(§1·P1-6) |

### 시뮬레이션 결과
- **총 24 시나리오 전부 PASS** — 단, PASS 근거가 §1(화면 액션)·§2(신설 데이터)·신규 probe에 의존하는 항목이 있음.
- **시뮬레이션이 새로 발견한 갭 3건**(정밀분석에 없던 것): S11 휴지통 복구(`deleted_at` 부재 실측), S13 개인정보 열람·export, S19 프록시 probe. → §1·§2에 반영 완료.
- **미충족 시 불통과 조건:** refunds/credits/audit/세금계산서/휴지통 중 하나라도 미구현이면 해당 S가 GAP → **통과기준 미달**. 따라서 이들은 P0.

---

## 4. 통과 판정

이 기획대로 §1 화면·§2 데이터·신규 probe를 구현하면 **24개 시나리오 전부 어드민 내에서 완결** → 골 통과기준 충족. 미구현 항목이 남으면 그 시나리오만큼 불통과이므로, 구축 순서는 P0(통과 필수)부터.

---

## 5. 구축 순서 (골 통과에 필요한 순)

**P0 — 이 단계까지 끝나야 유료 고객 대응 가능(S3·S4·S5·S6·S8·S11 통과)**
1. refunds 대장 + `run_refund`/`run_partial_refund` 이니시스 실연동
2. credits 원장(전환크레딧)
3. admin_audit_logs 전구간 훅
4. 세금계산서 발행 상태
5. soft delete(`deleted_at`) + 휴지통 복구
6. 개인정보 파기·열람 export

**P1 — 상시 대응(S16·S21·S22·S24 통과)**
7. 고객 360 통합 화면(원천 뷰 집계)
8. 구독 수명주기 운영
9. 알림 계보 단일화 + deadletter 화면

**P2 — 관제(S17~S20 통과)**
10. 관제 홈 처리 대기 큐 + 상태판(health probe 집계 + 프록시 probe 신규)
11. 미서비스26+엔진23 메뉴 제거·분리
12. Vue3 이식은 정리 후 26페이지 범위로 착수

---

## 6. 범위·격리

- GPT 소관 엔진 자산(Deterministic Compiler·Check Engine)은 이번 범위 밖, 격리 유지.
- 데이터 작업은 `apply_migration`(DDL)/`execute_sql`(DML), CONFIRMED 레코드 불변, `ON CONFLICT DO NOTHING`.
- 결제 상태는 어드민 DB에 복제하지 않고 payments/이니시스를 원천으로 읽는다(벤치마크 원칙).
