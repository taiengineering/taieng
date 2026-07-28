---

class: plans
type: PLAN
scope: ops
project: tai-admin-ops
title: TAI 어드민 1인 운영체계 재구성 기획 — 발송·통계·자동화 확장 통과판
version: 2
status: SUPERSEDED
superseded_by: PLAN_admin-rebuild_v3.md
owner: taiwang
---

> **이 문서는 v3로 대체됨.** 확장모듈 6종(정산·감사·공지·파일·연동·검색·온보딩)이 반영된 정본은 `PLAN_admin-rebuild_v3.md`. 아래는 이력 보존용.

# TAI 어드민 재구성 기획 v2 (발송·통계·자동화 확장 + 골 시뮬레이션 통과판)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **선행/대체:** PLAN_admin-rebuild_v1.md (SUPERSEDED by this) · ANALYSIS·RESEARCH 문서
- **v1 대비 변경:** ① 발송센터(SMS·메일·앱푸시) + 발송 기본설정 정식 편입 ② 통계/분석 존 신설 ③ 자동화 레이어를 아키텍처 원칙으로 격상(LLM/에이전트/매크로 후행 결합 가능) ④ 마케팅엔진 1.2 어드민 가동 자리 확보

---

## 0. 실측 — 자동화 뼈대는 이미 백엔드에 있다

`router_registry/external.py` 정독 결과, 아래 라우터가 **이미 존재**한다. 즉 발송·자동화 엔진은 있는데 **어드민 화면이 이걸 소비하지 않고 있는 것**이 문제다. 없는 걸 만드는 게 아니라 **연결**하는 작업이 핵심.

| 기능 | 기존 라우터 | 어드민 결선 상태 |
|---|---|---|
| SMS | `routers.messaging` (MessageMi) | 화면 미연결 |
| 앱푸시 | `routers.fcm` | push-test만 존재 |
| 메일 | `routers.mail` | tai-mail 스텁(237B) |
| 이벤트 트리거 | `routers.event_trigger` | 미연결 — **자동화 핵심** |
| AI 카피 | `routers.ai_copywrite` | 미연결 — LLM 결합점 |
| 통계 | `routers.admin_stats` | 미연결 |
| 크론 관리 | `routers.cron_manager` | cron-list 부분연결 |
| 알림 레지스트리 | notification_channel/event/routing (DB 7·8건) | 설정 화면 산재 |

**결론:** v1의 "알림 계보 단일화"를 넘어, **발송·트리거·통계·AI를 하나의 자동화 레이어로 묶고 어드민을 그 콘솔로 만든다.**

---

## 1. 운영 모델 (v1 유지) — 요일별 배제, 이벤트 기반 단일 처리함

요일별 운영은 참조만, 채택 안 함. 운영자는 **관제 홈의 처리 대기 큐 하나만 비운다.** 운영 상태는 요일이 아니라 큐 잔량이 정의. 자동화가 큐 항목 자체를 줄이는 것이 목표(§4).

---

## 2. 화면 구조 — 4 ZONE

v1의 3존에 **발송·자동화(ZONE 2)**와 통계를 정식 편입하고, 마케팅엔진 자리를 명시.

### ZONE 1 — 운영 (상시)
| # | 화면 | 필수 액션 |
|---|---|---|
| 1 | 관제 홈 | 처리 대기 큐 + 상태 신호등 7종 + **핵심 KPI 요약** |
| 2 | 고객 360 | 통합조회 / 비번재설정 / 정지·재개 / 탈퇴·파기·열람 / 휴지통 복구 |
| 3 | 결제·구독 원장 | 전체·부분환불(PG실호출) / 크레딧 / 세금계산서 / 구독수명주기 / 이의제기 |
| 4 | 진단 처리함 | 익명 6,062 조회 / 유료전환 / 재실행 |
| 5 | CS 함 | 통합 인박스 / 답변 / 딥링크 |
| 6 | 시스템 로그 | 배치실패 재실행 / deadletter 재발송 / 감사로그 |

### ZONE 2 — 발송·자동화 (신설, 상시 아님·이벤트 시)
| # | 화면 | 내용 | 백엔드 |
|---|---|---|---|
| 7 | **발송 센터** | SMS·메일·앱푸시 **통합 발송 콘솔**(수동 발송·대상 세그먼트·예약·발송이력·성공/실패) | messaging·mail·fcm |
| 8 | **발송 설정** | 채널별 인증정보·발신번호·템플릿·라우팅·수신동의/거부·디지스트 정책 | notification_channel/event/routing/template |
| 9 | **자동화 규칙** | 이벤트→액션 룰(진단완료→전환유도, 만료D-7→알림, 결제실패→독촉). 룰 on/off·실행이력 | event_trigger |

### ZONE 3 — 통계·분석 (신설)
| # | 화면 | 내용 | 백엔드 |
|---|---|---|---|
| 10 | **운영 대시보드** | 매출·구독(MRR/해지)·진단전환율·결제성공률·발송성공률·CS응답시간 | admin_stats |
| 11 | **퍼널 분석** | 익명진단→유료→SaaS 전환 퍼널, 이탈 지점 | admin_stats + anonymous_diagnosis_results |

### ZONE 4 — 마케팅엔진 1.2 (가동 자리 확보)
| # | 화면 | 내용 |
|---|---|---|
| 12 | **마케팅엔진 콘솔** | 사용자가 별도 작업 중인 마케팅엔진 1.2를 어드민에서 가동. 캠페인·세그먼트·발송을 ZONE2 발송레이어 위에서 구동. **상세 스펙은 마케팅엔진 담당 작업의 산출물을 이 자리에 결선**(이번 기획은 자리·연결점만 확보, 엔진 내부는 별도 문서) |

### ZONE 5 — 설정 / 엔진(분리)
price-setting, system-codes, permission, faq-setting / engine-* 23 → 45cm·별도도메인.

---

## 3. 데이터 모델 (v1 + 발송·통계·자동화)

v1의 refunds·credits·audit·세금계산서·soft delete 유지. 추가:

### 3-1. 발송 로그 단일화 (기존 계보 정리)
- 정본: `runtime_notification_event`(30,500)·`_metrics`(9,443)·`_deadletter`.
- 사망 계보(`notification_queue/logs` 0건)는 은퇴. 발송센터는 정본만 읽는다.
- 컬럼 요건: channel(SMS|MAIL|PUSH), target, template_id, status(SENT|FAIL|RETRY), fail_reason, sent_at.

### 3-2. 자동화 규칙 (event_trigger 활용 + 레지스트리)
```
automation_rule: id, name, trigger_event, condition_json,
  action(SEND_SMS|SEND_MAIL|SEND_PUSH|CREATE_TASK|CALL_WEBHOOK),
  action_params_json, enabled, last_run_at, run_count, created_by
automation_run_log: id, rule_id, fired_at, result, payload_json
```

### 3-3. 통계 (admin_stats 뷰)
- 원천 집계 뷰만 신설, 데이터 복제 금지. 예: `v_kpi_daily`, `v_funnel_conversion`.

---

## 4. 자동화 아키텍처 원칙 — LLM/에이전트/매크로 후행 결합

"최대한 자동화" 요구를 아키텍처로 못박는다. 자동화는 3층으로 분리하고, **상위 지능(LLM/에이전트/매크로)은 나중에 갈아끼울 수 있게 액션 인터페이스만 고정**한다.

```
[감지] 이벤트 버스 (event_trigger)
   ↓  trigger_event
[판단] 규칙 엔진 (automation_rule.condition_json)
   ↓  결정된 action + params
[실행] 액션 인터페이스 (표준 계약)
        ├─ SEND_SMS/MAIL/PUSH → messaging·mail·fcm
        ├─ CALL_WEBHOOK       → 외부/내부
        ├─ CREATE_TASK        → 관제 홈 큐
        └─ (후행) LLM_DRAFT / AGENT_RUN / MACRO → ai_copywrite 등
```

원칙:
1. **결정론 우선.** 규칙으로 되는 건 규칙으로. LLM은 카피 생성·분류·요약 등 "판단이 모호한 곳"에만 액션으로 주입.
2. **액션은 계약(interface).** SEND_*·WEBHOOK·TASK·LLM_DRAFT를 동일 시그니처로. 나중에 매크로/에이전트를 새 액션 타입으로 추가만 하면 됨(엔진 개조 불필요).
3. **모든 자동 실행은 감사·이력.** automation_run_log + admin_audit_logs. 자동화가 낸 사고도 추적 가능해야 함.
4. **사람 승인 게이트 옵션.** 위험 액션(환불·대량발송)은 rule에 `require_approval` 플래그 → 관제 홈 큐로 올려 1인이 원클릭 승인.
5. **드라이런.** 규칙은 발송 전 대상 수·미리보기를 보여주는 dry-run 필수(대량발송 사고 방지).

이 구조면 지금은 규칙+수동, 나중에 LLM 초안·에이전트 자동실행·매크로를 **액션으로 꽂기만** 하면 된다.

---

## 5. 골 시뮬레이션 — v1 24개 유지 + 발송·통계·자동화 6개 추가

v1의 S1~S24 전부 PASS 유지(화면 배선 동일). 추가 시나리오:

| # | 시나리오 | 처리 경로 | 판정 |
|---|---|---|---|
| S25 | 특정 세그먼트에 공지 SMS 발송 | 발송센터 세그먼트→dry-run→발송→이력 | PASS(§2 ZONE2) |
| S26 | 발신번호·템플릿 변경 | 발송설정 | PASS |
| S27 | 만료 D-7 자동 알림 | 자동화규칙 on + run_log | PASS(§3-2) |
| S28 | 결제실패 자동 독촉 | 자동화규칙(require_approval 옵션) | PASS(§4) |
| S29 | 이번 달 매출·전환율 확인 | 운영 대시보드 | PASS(§2 ZONE3) |
| S30 | 대량발송 오발송 방지 | dry-run 대상수·미리보기 | PASS(§4-5) |

**결과: 30개 전부 PASS.** 발송·설정·통계·자동화가 어드민 안에서 완결 → 골 통과기준을 v1보다 넓게 충족(발송·통계는 통과기준의 "서비스 이슈 발송실패" 및 운영 상시 요건에 직접 대응).

---

## 6. 구축 순서 (v1 P0~P2 + 발송·자동화·통계·마케팅)

**P0 (골 통과 필수):** v1의 refunds·credits·audit·세금계산서·soft delete·개인정보.
**P1 (상시 운영):** 고객360 / 구독수명주기 / **발송센터+발송설정(ZONE2 7·8)** / 알림정본 단일화.
**P2 (자동화·관제):** **자동화 규칙엔진(9)** / 관제 홈 큐+상태판+KPI / **통계 대시보드(10·11)**.
**P3 (성장):** **마케팅엔진 1.2 결선(12)** — 담당 작업 산출물 준비되면 ZONE2 발송레이어 위에 결선. 미서비스·엔진 메뉴 정리. Vue3 이식(정리 후 범위).

> 마케팅엔진은 발송·자동화 레이어(ZONE2)가 선행돼야 위에 얹힌다. 순서상 P1(발송)·P2(자동화) → P3(마케팅) 의존.

---

## 7. 범위·격리 (v1 유지)
GPT 엔진 자산 격리. 결제상태 원천 읽기. `apply_migration`/`execute_sql`, CONFIRMED 불변. 카카오 API 전면 금지(발송은 MessageMi·mail·FCM만).
