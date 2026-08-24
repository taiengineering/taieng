# WP-FRONT-01 — FRONTEND SCOPE DECISION (종합)

- baseline: tai-admin@0a61fe5e / tai-api@27970b61
- 상태: ANALYSIS · FINALIZATION · mutation 0 (code/DB/API/repo)
- 본 문서는 STEP 15 최종 종합.

## STEP 15 — 10개 필수 답변

### 1. 기존 자산 그대로 KEEP 가능한 범위
- 공통 인프라: useTaiApi, useAuth, useRowSelection, work-scheduleFormat
- 점검 흐름: my-inspection, inspection-anchor, my-equipment, worker-list
- 문서: document-forms(작성기), engine-document(카탈로그)
- 근거: 원본/ES모듈 이식으로 계약 안정, 백엔드 대조 결과 CONFIRMED, drift 없음

### 2. 기존 자산 수정으로 해결되는 범위
- **P0(status drift)**: statusLabels.ts(공통 헬퍼 추가), work-schedule-list(overdue 1곳), inspection-calendar(write 1곳), safety-dashboard(8 expressions = 통계4 + 필터4)
- **MODIFY-L**: equipment-qr-manager(체크인 이력 수용)
- **MODIFY-M**: factory context 공통화(useFactoryContext adapter)
- 근거: 계약/백엔드는 정상, 프론트 계산·표기·컨텍스트만 보정

### 3. 반드시 NEW가 필요한 범위
- **Runtime Document 관리/검토 lifecycle 1건** (P1)
- 근거: 백엔드 document-engine lifecycle(list/status/evidence/audit) LIVE인데 소비 UI 전무, document-forms(단건 작성기)로 수행 불가

### 4. backend/API 선행이 필요한 범위
- **없음** (프론트 작업 관점). 구현 확정 대상(P0/NEW/MODIFY-L)이 의존하는 required API는 직독으로 LIVE 확인됨. (PARTIAL 계약은 착수 전 개별 검증 잔존 — §API_CONTRACT_AUDIT §4)
- 단, 선택적 강건화: 백엔드 work_schedules PATCH의 status_code normalize(구값 방어)는 백엔드 개선사항이나 P0 해결의 필수 선행은 아님(프론트 write를 canonical로 바꾸면 해결).
- submitted_by / inspector identity는 별도 backend WP(본 WP 무관).

### 5. 현재 구현되어 있으나 dead/unreachable인 자산
- **없음(확인된 범위 내)**. production 메뉴 정본은 `/menus → menu_catalog`이며, 직독 대상 페이지(my-equipment, inspection-anchor, my-inspection, inspection-calendar, work-schedule-list, worker-list, engine-schedule, engine-document, document-forms, equipment-qr-manager, inspection-custom, construction-inspection-*)는 active 메뉴로 확인됨(운영자 DB 직독). 파일 잔존만으로 DEPRECATE 금지.

### 6. 중복 자산 및 MERGE 후보
- **직접 MERGE 후보 없음(확인된 범위 내)**.
- 잠재 정리: `useSafetyDashboard`의 담당자 배정 모달과 `useWorkSchedulePanel`의 배정 로직이 동일 백엔드 경로(PATCH /work-schedules/{id})를 각자 구현 → 공통화 여지(MODIFY 시 부수 정리, MERGE 아님).
- status 완료판정: 3개 페이지의 산발 `!== 'DONE'`을 statusLabels 헬퍼로 수렴(중복 제거) = P0 처리에 포함.

### 7. DEPRECATE 후보
- **없음(확인된 범위 내)**.

### 8. UNKNOWN 잔여 항목
- **UNKNOWN 자산 2**: inspection-custom, engine-schedule (직독 후 KEEP/MODIFY 판정)
- **P2 observation 3** (자산 분류 아님): 알림 flow(alert-list/notification-list) 프론트 미조사; factory context source B(localStorage.selectedFactoryId) 레거시 여부; my-inspection status 필터값 canonical 정합
- **OUT OF SCOPE**: diagnosis/risk-assessment/tbm/education/safety-meeting/holiday/org/compliance 계열 — factory_id 사용 65개에 포함되나 본 WP scope 밖, UNKNOWN에 넣지 않음
- 증거 조회 UI(flow I): evidence 소비 지점은 Runtime Document NEW(GAP-2)에 수렴

### 9. 구현 우선순위 P0/P1/P2

**P0 (즉시 — 안전/정합성 결함)**
- P0-A inspection-calendar: write 'COMPLETED' → 'completed'
- P0-B work-schedule-list: overdue 필터 `!== 'DONE'` → canonical-aware
- P0-C safety-dashboard: 통계4 + 필터4의 `!== 'DONE'` → canonical-aware
- P0 공통: statusLabels.ts에 `isWsCompleted()` 등 canonical-aware 헬퍼 추가

**P1 (기능 확장/신규)**
- Runtime Document 관리/검토 lifecycle (NEW)
- equipment-qr-manager 체크인 이력 수용 (MODIFY-L)
- factory context 공통화 useFactoryContext (MODIFY-M)

**P2 (조사/판정 보류) — UNKNOWN 자산 2 + observation 3**
- UNKNOWN 자산: inspection-custom, engine-schedule (직독 후 판정)
- observation: 알림 flow(K) 프론트 확인; selectedFactoryId 레거시 여부; my-inspection status 필터값 canonical 정합(확정 defect 아님)

### 10. 예상 후속 WP 분리안
- **WP-FRONT-02 (수정)**: P0 status drift 3건 + statusLabels 공통 헬퍼. 가장 시급, 독립 실행 가능.
- **WP-FRONT-03 (신규)**: Runtime Document 관리/검토 화면.
- **WP-FRONT-04 (확장)**: equipment-qr-manager 체크인 이력 + factory context 공통화.
- **WP-FRONT-05 (E2E)**: A~L flow 통합 E2E.
- **별도 backend WP**: submitted_by writer, inspector identity 정리(프론트 무관).

---

## 최종 분류 카운트

> 대상: inspection/schedule/equipment/document/worker/factory-context 직접 자산 + 공통 인프라. diagnosis/risk/tbm/education 등 scope 주변부는 OUT OF SCOPE로 분리.

> 계수 단위: 자산(페이지/컴포저블/유틸) 단위. document-forms와 engine-document는 서로 다른 화면이므로 각각 별도 계수. 하나의 자산은 하나의 분류에만 속한다. UNKNOWN은 **자산**만 계수하고, 관찰 항목은 P2 OBSERVATION으로 분리한다.

| 분류 | count | 항목 |
|---|---:|---|
| KEEP | 10 | useTaiApi, useAuth, useRowSelection, work-scheduleFormat, my-inspection, inspection-anchor, my-equipment, worker-list, document-forms, engine-document |
| MODIFY-S | 3 | statusLabels(헬퍼추가), work-schedule-list(P0-B), inspection-calendar(P0-A) |
| MODIFY-M | 2 | safety-dashboard(P0-C), factory context 공통화(useFactoryContext) |
| MODIFY-L | 1 | equipment-qr-manager(체크인 이력) |
| NEW | 1 | Runtime Document 관리/검토 lifecycle |
| MERGE | 0 | (없음; 배정로직 공통화는 MODIFY 부수) |
| DEPRECATE | 0 | (없음) |
| UNKNOWN | 2 | inspection-custom, engine-schedule |
| **분류 대상 총계** | **19 assets** | |

**P2 OBSERVATIONS = 3** (자산 분류 아님)
- alert/notification flow (K 알림 프론트 미조사)
- selectedFactoryId legacy context 여부
- my-inspection status filter canonical 확인

**OUT OF SCOPE / NOT COUNTED**
- diagnosis / risk-assessment / tbm / education / safety-meeting / holiday / org / compliance 계열 — factory_id 사용 65개에는 포함되나 본 WP inspection/schedule/equipment/document/worker/factory-context scope 밖. UNKNOWN에 넣지 않음.

| 우선순위 | count | 항목 |
|---|---:|---|
| P0 | 4 | statusLabels helper, work-schedule-list, inspection-calendar, safety-dashboard |
| P1 | 3 | Runtime Document NEW, equipment history MODIFY-L, factory context MODIFY-M |
| P2 | 5 | UNKNOWN asset 2(inspection-custom, engine-schedule) + observation 3(알림 flow, selectedFactoryId, my-inspection status 필터) |

---

## 핵심 결론

1. **대규모 신규 프론트 개발은 필요 없다.** 실측 결과 NEW는 1건(Runtime Document lifecycle).
2. **주 작업은 기존 자산 정합성 수정.** 특히 P0 status vocabulary drift(안전 통계 오계산 포함)가 가장 시급.
3. **"추정 API"는 실재했다.** work-schedule-list의 추정 계약(GET/PATCH/bulk-assign)은 백엔드에 전부 존재. 백엔드가 프론트 화면에 맞춰 이미 구현.
4. **프론트도 백엔드처럼 상당 부분 이미 만들어져 있다.** A~L 12개 flow: FULLY CLOSED 9 / PARTIAL 2(I 증거조회, K 알림) / GAP 1(H 설비 체크인). GAP(H)마저 워커앱 scope(제출) + 기존 화면 확장(관리자 이력)으로 처리.
5. **factory 격리는 backend가 강제**하므로 프론트 보안엔진 불필요. factory context는 UX 정합성(MODIFY-M) 문제.

## SCOPE FREEZE 제안
위 카운트와 P0/NEW 판정으로 FRONTEND IMPLEMENTATION SCOPE FREEZE 가능. UNKNOWN 자산 2건(inspection-custom, engine-schedule) + P2 observation 3은 P2로 분리하여 freeze를 막지 않음(후속 직독 시 KEEP/MODIFY로 흡수 예상, NEW 추가 가능성 낮음).
