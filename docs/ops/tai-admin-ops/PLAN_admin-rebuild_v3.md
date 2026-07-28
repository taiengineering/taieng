---

class: plans
type: PLAN
scope: ops
project: tai-admin-ops
title: TAI 어드민 1인 운영체계 재구성 기획 — 확장모듈 6종 반영 통과판
version: 3
status: ACTIVE
owner: taiwang
---

# TAI 어드민 재구성 기획 v3 (확장모듈 6종 + 골 시뮬레이션 통과판)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **선행/대체:** PLAN_admin-rebuild_v2.md (SUPERSEDED by this) · ANALYSIS·RESEARCH 문서
- **v2 대비 변경:** 이커머스/SaaS 어드민 기준 확장 후보 중 **사용자 채택 6종** 정식 편입 — ② 정산·세무 리포트 ③ 감사·활동 로그 ⑫ 공지/배너 ⑬ 파일/자산 ⑭ 웹훅/연동 상태 ⑮ 글로벌 검색 ⑱ 온보딩 체크리스트. (마케팅 그룹은 UI에 이미 존재 — 예하 메뉴 그대로 사용)

---

## 0. 실측 — 채택 6종의 "신설 vs 연결" 판정

Supabase 실측으로 각 모듈이 기존 자산 위 연결인지 신설인지 확정.

| # | 모듈 | 기존 자산(실측) | 판정 |
|---|---|---|---|
| 2 | 정산·세무 리포트 | `settlements`(빈 상태) | **집계 화면만 신설**(원천 payments/refunds 읽기) |
| 3 | 감사·활동 로그 | `admin_audit_logs`(1)·`document_binding_audit_log`·`document_schema_audit` | **훅+조회화면**(기존 활성화) |
| 12 | 공지/배너 | 없음 | **신설**(테이블+화면) |
| 13 | 파일/자산 | `company_files`·`file_categories`·`education_files`·`documents`·`generated_document` | **통합 뷰만**(신규 저장소 불필요) |
| 14 | 웹훅/연동 상태 | `internal_api_registry`·`report_api_registry`·`law_external_catalog`(983) | **api-monitor 승격** |
| 15 | 글로벌 검색 | (프론트 기능) | **신설**(교차검색 API+상단 검색바) |
| 18 | 온보딩 체크리스트 | 고객용 없음(`checklist_*`는 전부 법령진단 엔진용) | **신설**(고객 온보딩 전용) |

> 마케팅: 정본 메뉴(`menu-nav.js`) 실측 결과 **마케팅 그룹은 이미 존재**, 하위 "지식인관리". 예하 메뉴/페이지는 그대로 사용. 마케팅엔진 1.2는 ZONE4에 결선(자리 확보).

---

## 1. 운영 모델 (유지) — 요일별 배제, 이벤트 기반 단일 처리함

요일별 운영은 참조만, 채택 안 함. 운영자는 관제 홈의 처리 대기 큐 하나만 비운다. 상태=큐 잔량. 자동화가 큐를 줄이는 것이 목표(§4).

---

## 2. 화면 구조 — 6 ZONE

v2 4존 + 마케팅(기존) + 확장 6종 편입.

### ZONE 1 — 운영 (상시)
| # | 화면 | 필수 액션 |
|---|---|---|
| 1 | 관제 홈 | 처리 대기 큐 + 상태 신호등 7종 + 핵심 KPI 요약 + **상단 글로벌 검색(⑮)** |
| 2 | 고객 360 | 통합조회 / 비번재설정 / 정지·재개 / 탈퇴·파기·열람 / 휴지통 복구 / **온보딩 진행상태(⑱)** |
| 3 | 결제·구독 원장 | 전체·부분환불 / 크레딧 / 세금계산서 / 구독수명주기 / 이의제기 |
| 4 | 진단 처리함 | 익명 6,062 조회 / 유료전환 / 재실행 |
| 5 | CS 함 | 통합 인박스 / 답변 / 딥링크 |
| 6 | 시스템 로그 | 배치실패 재실행 / deadletter 재발송 / **감사·활동 로그(③)** |

### ZONE 2 — 발송·자동화
| # | 화면 | 내용 | 백엔드 |
|---|---|---|---|
| 7 | 발송 센터 | SMS·메일·앱푸시 통합 콘솔(세그먼트·예약·이력) | messaging·mail·fcm |
| 8 | 발송 설정 | 발신번호·템플릿·라우팅·수신동의 | notification_channel/event/routing |
| 9 | 자동화 규칙 | 이벤트→액션 룰·on/off·실행이력 | event_trigger |
| 13 | **공지/배너 관리(⑫)** | 서비스 점검·정책변경을 앱 내 배너/팝업 일괄 고지. 장애 시 CS 폭주 사전 차단 | **신설 테이블** notice/banner |

### ZONE 3 — 통계·재무
| # | 화면 | 내용 | 백엔드 |
|---|---|---|---|
| 10 | 운영 대시보드 | 매출·MRR·전환율·결제/발송 성공률·CS응답 | admin_stats |
| 11 | 퍼널 분석 | 익명→유료→SaaS 전환·이탈 | admin_stats + anonymous_diagnosis_results |
| 12 | **정산·세무 리포트(②)** | 월별 매출·부가세·환불액 집계 → 세무/회계 export. B2B/B2G·조달청 대응 | settlements + payments/refunds 원천 |

### ZONE 4 — 마케팅 (기존 UI 사용)
| # | 화면 | 내용 |
|---|---|---|
| 14 | 마케팅 그룹(기존) | 지식인관리 등 예하 메뉴 그대로 사용 |
| 15 | 마케팅엔진 1.2 결선 | 담당 작업 산출물을 ZONE2 발송레이어 위에 결선(자리·연결점 확보) |

### ZONE 5 — 자산·연동
| # | 화면 | 내용 | 백엔드 |
|---|---|---|---|
| 16 | **파일/자산 관리(⑬)** | 계약서·증빙·리포트PDF·이미지 중앙 통합뷰·검색 | company_files·file_categories·education_files·documents·generated_document 통합 |
| 17 | **웹훅/연동 상태(⑭)** | 이니시스·MessageMi·law.go.kr·KOSHA·juso 키·상태·최근호출 | internal_api_registry·report_api_registry·law_external_catalog·health probe |

### ZONE 6 — 설정 / 엔진(분리)
price-setting, system-codes, permission, faq-setting / engine-* 23 → 45cm·별도도메인.

---

## 3. 데이터 모델 (v2 + 확장 6종)

v2의 refunds·credits·audit·세금계산서·soft delete·automation_rule·통계뷰 유지. 추가:

### 3-1. 공지/배너 (⑫ 신설)
```
notice: id, type(BANNER|POPUP|MAINTENANCE), title, body,
  audience(ALL|PLAN|SEGMENT), audience_filter_json,
  starts_at, ends_at, priority, enabled, created_by, created_at
```

### 3-2. 온보딩 체크리스트 (⑱ 신설 — 고객 온보딩 전용)
```
onboarding_checklist_item: id, step_key, label, order, required
onboarding_progress: id, company_id(FK), step_key, done_at
```
- ※ 기존 `checklist_*`는 법령진단 엔진용이므로 재사용 금지. 별도 테이블.

### 3-3. 감사 로그 통합 조회 (③ 뷰)
- `admin_audit_logs`(활성화) + `document_binding_audit_log` + `document_schema_audit`를 한 화면에서 필터 조회하는 통합 뷰 `v_audit_unified`.

### 3-4. 정산·파일·연동 — 신규 테이블 없음
- 정산(②): `settlements` + payments/refunds 원천 집계 뷰만.
- 파일(⑬): 기존 5개 테이블 UNION 뷰 `v_files_unified`.
- 연동(⑭): 기존 레지스트리 3종 + health probe 조합.

---

## 4. 자동화 아키텍처 원칙 (v2 유지)

[감지] event_trigger → [판단] automation_rule → [실행] 액션 인터페이스(SEND_*·WEBHOOK·CREATE_TASK·LLM_DRAFT·AGENT·MACRO).
원칙: 결정론 우선 / 액션은 계약(interface) / 전량 감사 / 위험액션 승인게이트 / 대량발송 dry-run. 상위 지능(LLM·에이전트·매크로)은 새 액션 타입으로 후행 결합.

**확장 6종의 자동화 결합점:**
- 공지/배너(⑫): 장애 probe(⑭·health) 발생 → 자동화 규칙이 유지보수 배너 자동 게시.
- 온보딩(⑱): 가입 후 미완료 스텝 → 자동 넛지 발송(발송센터).
- 정산(②): 월말 배치가 정산 리포트 자동 생성 → 관제 홈 큐.

---

## 5. 골 시뮬레이션 — v2 30개 유지 + 확장 6종 7개 추가

v2의 S1~S30 전부 PASS 유지. 추가:

| # | 시나리오 | 처리 경로 | 판정 |
|---|---|---|---|
| S31 | 월 매출·부가세·환불 세무자료 제출 | 정산·세무 리포트 export | PASS(②) |
| S32 | "누가 이 환불을 처리했나" 추적 | 감사·활동 로그 통합조회 | PASS(③) |
| S33 | 서비스 점검 공지 일괄 게시 | 공지/배너 관리 게시 | PASS(⑫) |
| S34 | 특정 고객 계약서·증빙 즉시 열람 | 파일/자산 통합뷰 검색 | PASS(⑬) |
| S35 | 이니시스/law.go.kr 연동 상태·최근호출 확인 | 웹훅/연동 상태 | PASS(⑭) |
| S36 | 회원·결제·문의 교차 즉시 점프 | 상단 글로벌 검색 | PASS(⑮) |
| S37 | 신규 가입자 설정 미완료 추적·넛지 | 고객360 온보딩 상태 + 자동 넛지 | PASS(⑱) |

**결과: 총 37개 전부 PASS.** 확장 6종이 어드민 안에서 완결. 골 통과기준(소비자·서비스 이슈 어드민 완결)을 상회 충족.

---

## 6. 구축 순서

**P0 (골 통과 필수):** refunds·credits·**감사로그(③)**·세금계산서·soft delete·개인정보.
**P1 (상시 운영):** 고객360(+온보딩 상태⑱) / 구독수명주기 / 발송센터+발송설정 / 알림 단일화 / **파일·자산 통합뷰(⑬)** / **웹훅·연동 상태(⑭)** / **글로벌 검색(⑮)**.
**P2 (자동화·관제·재무):** 자동화 규칙엔진 / 관제 홈 큐+상태판+KPI / 통계 대시보드 / **정산·세무 리포트(②)** / **공지·배너(⑫)** / **온보딩 체크리스트(⑱)**.
**P3 (성장):** 마케팅엔진 1.2 결선. 미서비스·엔진 메뉴 정리. Vue3 이식.

> 의존: 공지·배너(⑫)는 발송/probe 레이어 뒤, 온보딩 넛지(⑱)는 발송센터 뒤, 정산(②)은 refunds 뒤. 그래서 P0(감사)·P1(발송·파일·연동) → P2(정산·공지·온보딩) 순.

---

## 7. 범위·격리 (유지)
GPT 엔진 자산 격리. 결제상태 원천 읽기. `apply_migration`/`execute_sql`, CONFIRMED 불변. 카카오 API 전면 금지. 마케팅 "소개비/소개수수료" 용어 금지(플랫폼 크레딧으로).
