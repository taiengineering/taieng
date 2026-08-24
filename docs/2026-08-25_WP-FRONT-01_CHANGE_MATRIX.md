# WP-FRONT-01 — CHANGE MATRIX

- baseline: `tai-admin@0a61fe5e`
- 분류: KEEP / MODIFY-S / MODIFY-M / MODIFY-L / NEW / MERGE / DEPRECATE / UNKNOWN
- 대상: inspection/schedule/equipment/document/worker/factory-context 관련 직접 자산 + 공통 인프라

각 행: file · route · 현재 역할 · flow · API contract · factory context · 판정 · 근거 · 변경 내용 · backend dep · priority

---

## 공통 인프라

### composables/useTaiApi.ts
- route: (공통) · 역할: API wrapper · flow: 전체 · contract: CONFIRMED · factory: n/a
- **판정: KEEP** · 근거: 단일 계약(request/list/upload/download), 전 페이지 안정 사용 · 변경: 없음 · backend dep: 없음 · priority: -

### composables/useAuth.ts
- route: (공통) · 역할: 인증/factory 기본값 저장 · flow: 전체 · contract: CONFIRMED · factory: A(localStorage.factory_id) 원천
- **판정: KEEP** · 근거: 로그인/가드 안정. 계약 이슈(contracts/my)는 이미 수정됨 · 변경: 없음(단 factory context 공통화 시 참조원) · backend dep: 없음 · priority: -

### utils/statusLabels.ts
- route: (공통) · 역할: status 라벨 정본 · flow: D/G/K · contract: n/a · factory: n/a
- **판정: MODIFY-S** · 근거: 라벨은 canonical 정본이나 완료판정 헬퍼(isWsCompleted) 부재 → 각 페이지가 `!== 'DONE'` 산발 · 변경: canonical-aware `isWsCompleted()` 등 헬퍼 추가(공통화) · backend dep: 없음 · **priority: P0** (P0-A/B/C의 공통 해결 지점)

### utils/work-scheduleFormat.ts
- route: work-schedule-list · 역할: 표시 유틸 · flow: D · contract: n/a · factory: n/a
- **판정: KEEP** · 근거: STATUS_OPTIONS/statusBadge 이미 canonical, 완료판정 함수는 날짜/배정 기반 · 변경: 없음(헬퍼는 statusLabels로 공통화) · priority: -

### composables/useRowSelection.ts
- **판정: KEEP** · 근거: 목록 선택 공통 패턴, drift 없음 · priority: -

---

## flow 핵심 페이지

### work-schedule-list (index.vue, useWorkScheduleList.ts, useWorkSchedulePanel.ts)
- route: /work-schedule-list · 역할: 작업일정 조회 + 담당자 배정 · flow: D/E
- contract: GET /work-schedules, PATCH /{id}, POST /bulk-assign, GET /users — **전부 CONFIRMED**
- factory: C(route.query) + D(local) + F(API query)
- **판정: MODIFY-S** · 근거: 계약은 정상(추정→CONFIRMED). filteredItems `case 'overdue'`에 `status_code !== 'DONE'` 1곳(**P0-B**) · 변경: overdue 완료판정을 canonical-aware로 교체 · backend dep: 없음 · **priority: P0**

### my-inspection (index.vue, useMyInspectionList.ts, useMyInspectionPanel.ts)
- route: /my-inspection · 역할: 점검 세트/일정/시작/완료 · flow: B/C/F/G
- contract: /inspection/status, /inspection-sets, /inspection/schedules, /inspection/start, /inspection/complete — CONFIRMED
- factory: C + D + E(path)
- **판정: KEEP** · 근거: 원본 이식, 계약 안정, 확정 defect 없음 · 변경: 없음 · backend dep: 없음 · priority: -
- 관찰(P2): status_code 필터 파라미터 전송값('SCHEDULED')이 canonical과 일치하는지 정합 확인은 **P2 observation**(확정 defect 아님). 자산 판정은 KEEP 단일.

### inspection-anchor (index.vue, useInspectionAnchorList.ts)
- route: /inspection-anchor · 역할: 기준일 설정 · flow: B
- contract: GET /inspection-sets, PATCH /inspection-sets/anchor/bulk — CONFIRMED
- factory: C + D + F
- **판정: KEEP** · 근거: 원본 이식, 계약·흐름 완결(→ 캘린더 라우팅) · 변경: 없음 · priority: -

### inspection-calendar (useInspectionCalendarList.ts, index.vue)
- route: /inspection-calendar · 역할: 캘린더 + 완료처리 · flow: K/G
- contract: GET /work-schedules(범위), GET /inspection-sets/factory-preview, PATCH /work-schedules/{id} — CONFIRMED/PARTIAL
- factory: C + D + F
- **판정: MODIFY-S** · 근거: `PATCH {status_code:'COMPLETED'}` write drift(**P0-A**) · 변경: write 값 'COMPLETED'→'completed' · backend dep: 없음(선택: 백엔드 PATCH normalize 추가 가능) · **priority: P0**

### safety-dashboard (useSafetyDashboard.ts)
- route: /safety-dashboard · 역할: 통합 대시보드(일정 통계/차트/미이행/날씨/담당자배정) · flow: D/E/K
- contract: GET /work-schedules, /users, /overdue/*, /weather/*, PATCH /work-schedules/{id} — CONFIRMED/PARTIAL
- factory: A(localStorage) + D + F. company_id 스코핑 + 시설1개 자동선택
- **판정: MODIFY-M** · 근거: raw `status_code !== 'DONE'` **8 expressions**(**P0-C**) = statistics 4(statD0/statD3/statMonth/statUnassigned) + filteredSchedules branches 4(d0/d3/month/unassigned) → 완료 일정 미완료 오계산(안전 오계산) · 변경: 통계/필터를 canonical-aware isWsCompleted로 교체(표시부는 이미 정본) · backend dep: 없음 · **priority: P0**

### inspection-custom (useInspectionCustomList.ts, Panel)
- route: /inspection-custom · 역할: 커스텀 점검 · flow: 점검 보조
- **판정: UNKNOWN** · 근거: 본 WP 미직독(우선순위 밖) · 변경: 직독 후 확정 · priority: P2

### engine-schedule (useEngineScheduleList.ts, Panel)
- route: /engine-schedule · 역할: 스케줄 엔진 · flow: D 보조
- **판정: UNKNOWN** · 근거: 미직독 · priority: P2

---

## 설비

### my-equipment (useMyEquipmentList.ts, useEquipmentAddModal.ts, index.vue)
- route: /my-equipment · 역할: 설비 자산 목록 · flow: (설비 관리)
- contract: GET /equipment-assets — CONFIRMED
- factory: C + D + F. company_id 스코핑 + 시설1개 자동선택(정교)
- **판정: KEEP** · 근거: 원본 이식, factory 스코핑 정교 · 변경: 없음 · priority: -

### equipment-qr-manager (useEquipmentQrManagerList.ts, useEquipmentQrPanel.ts)
- route: /equipment-qr-manager · 역할: QR/RFID 설비 관리(목록) · flow: H 인접
- contract: GET /factories, GET /equipment-assets — CONFIRMED. **GET /equipment-checkins UNUSED**
- factory: D + F
- **판정: MODIFY-L** · 근거: 백엔드 equipment_checkins GET(관리자 이력) LIVE인데 미소비. 이 화면이 설비+QR/RFID를 이미 다루므로 체크인 이력/상태/필터 수용 가능 · 변경: 체크인 이력 조회/필터 탭 추가(GET /equipment-checkins) · backend dep: 없음(GET 이미 존재) · priority: P1

---

## 문서

### document-forms (useDocumentFormsList.ts, Generate.ts, Factory.ts, index.vue)
- route: /document-forms · 역할: 서식 작성 → runtime 문서 생성 → PDF · flow: J
- contract: /document-forms, /document-engine/documents(POST/PATCH/generate) — CONFIRMED
- factory: D + body(factory_id)
- **판정: KEEP** · 근거: ES모듈 원본 이식, 단건 작성 흐름 완결 · 변경: 없음 · priority: -

### engine-document (useEngineDocumentList.ts, useEngineDocumentDetail.ts)
- route: /engine-document · 역할: 서식 카탈로그(LEGAL/STANDARD/FREE) · flow: J 보조
- contract: /engine/forms/* — PARTIAL
- **판정: KEEP** · 근거: 카탈로그 조회(runtime 문서 아님), 역할 분리 명확 · 변경: 없음 · priority: -

### (NEW) Runtime Document 관리/검토
- route: (신규) · 역할: 생성 문서 횡단 목록/상태전이/검토승인/증빙/감사
- contract: GET /document-engine/documents, POST /{id}/status, /transitions, /{id}/evidence, /{id}/audit-log, /metrics — **전부 UNUSED(LIVE)**
- **판정: NEW** · 근거: 백엔드 lifecycle LIVE인데 소비 UI 전무. document-forms(단건 작성기)로 수행 불가(횡단 검토 큐는 다른 역할) · 변경: 신규 route(문서목록 + 상태 + 검토/승인 + 증빙 + 감사) · backend dep: 없음(전부 LIVE) · priority: P1

---

## 작업자

### worker-list (useWorkerList.ts, useWorkerPanel.ts, useWorkerBulkUpload.ts, index.vue)
- route: /worker-list · 역할: 현장 작업자(worker_registry / site workers) 관리 · flow: L
- contract: /worker-registry, /construction/sites/{id}/workers, /departments|teams|groups — CONFIRMED/PARTIAL
- factory: A(기본선택) + D + F. business_sector 분기
- **판정: KEEP** · 근거: 원본 이식, 계약 확인. worker_registry≠users 구분 정확 · 변경: 없음 · priority: -

---

## factory context (공통 관심사)

### (신규 예정) composables/useFactoryContext.ts
- 역할: factory 선택 컨텍스트 통일(useAuth + route.query + selector adapter)
- **판정: MODIFY-M** · 근거: A/B/C/D 소스가 페이지마다 정본이 달라 UX 불일치(보안 아님 — 백엔드 scope guard 강제) · 변경: 기존 패턴을 묶는 adapter 컴포저블 1개 추가 + 페이지 점진 적용 · backend dep: 없음 · priority: P1

---

## 설비 체크인 제출(작업자)
- **판정: (tai-admin scope 밖)** · 근거: POST /equipment-checkins는 익명 현장 스캔 = 워커앱/PWA 소관 · 변경: tai-admin에서 NEW 금지 · priority: -

## Known issue (별도 backend WP)
- submitted_by, inspector identity — 프론트 미소비/간접. 본 WP 구현 없음. §KNOWN_ISSUE 참조.
