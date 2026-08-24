# WP-FRONT-01 — USER FLOW MAP

- baseline: `tai-admin@0a61fe5e`
- 각 flow: PAGE → API → INPUT → MUTATION → RESULT → NEXT

## 완결 수치

```
FULLY CLOSED = 9  (A, B, C, D, E, F, G, J, L)
PARTIAL      = 2  (I 증거조회 미확인, K 알림 프론트 미조사)
GAP          = 1  (H 설비 체크인)
TOTAL        = 12
```

> H는 worker submission = 다른 scope(워커앱), admin history = 기존 화면 MODIFY-L로 처리되므로 SCOPE FREEZE를 막지 않는다.

## 요약표

| Flow | 화면 | 상태 |
|---|---|---|
| A 사업장 선택 | 공통 factory selector | ✅ |
| B 점검 세트 / 기준일 | my-inspection(킭2), inspection-anchor | ✅ |
| C 점검 일정 | my-inspection(킭1) | ✅ |
| D 작업 일정 | work-schedule-list | ✅ |
| E 담당자 배정 | work-schedule Panel, safety-dashboard | ✅ |
| F 점검 시작 | my-inspection | ✅ |
| G 점검 완료 | my-inspection, inspection-calendar | ✅ |
| H 설비 체크인 | (없음) | ❌ GAP |
| I 점검 결과/증거 | 완료처리 O, 증거첨부 조회 △ | △ 부분 |
| J 문서 작성/제출 | document-forms | ✅ |
| K 캘린더/기한초과/알림 | inspection-calendar, my-inspection (캘린더 O) / 알림 미조사 | △ PARTIAL |
| L 작업자/담당자 선택 | worker-list(작업자), Panel(담당자) | ✅ |

---

## A. 사업장 선택
- PAGE: 모든 목록 화면 상단 factory selector
- API: `GET /factories?page=1&size=100` (일부 `&company_id=` 명시)
- INPUT: 드롭다운 선택 또는 `route.query.factory_id`
- MUTATION: 없음(조회 컨텍스트)
- RESULT: factoryId ref 설정 + `router.replace`로 URL 동기화
- NEXT: 선택 factory로 하위 목록 로드

## B. 점검 세트 / 기준일 설정
- PAGE: my-inspection(킭2), inspection-anchor
- API: `GET /inspection-sets?factory_id=&source=LEGAL_ENGINE&page=&size=` (폴백 `/inspection-sets/factory/{id}`); `PATCH /inspection-sets/anchor/bulk {items:[{id, schedule_anchor_date, last_inspection_date?}]}`
- INPUT: 세트별 기준일/직전점검일 입력
- MUTATION: anchor bulk 저장
- RESULT: 다음 점검일 재계산
- NEXT: inspection-calendar로 라우팅(예정일 생성)

## C. 점검 일정
- PAGE: my-inspection(킭1)
- API: `GET /inspection/schedules/{factoryId}?month=&status_code=`; 통계 `GET /inspection/status/{factoryId}`
- INPUT: 월/상태 필터
- MUTATION: 없음(조회)
- RESULT: 일정 목록 + 통계카드(전체세트/이번달/완료/기한초과)
- NEXT: 행별 시작/완료 액션(F/G)

## D. 작업 일정
- PAGE: work-schedule-list
- API: `GET /work-schedules?factory_id=&status_code=&obligation_type=&keyword=&page=&size=` [백엔드 CONFIRMED]
- INPUT: 키워드/의무구분/상태 필터, 범례칩(auto/manual/unassigned/overdue/due_soon)
- MUTATION: 없음(조회)
- RESULT: 작업일정 목록
- NEXT: 선택 → 담당자 배정(E)

## E. 담당자 배정
- PAGE: work-schedule Panel, safety-dashboard(모달)
- API: `GET /users?factory_id=&size=200` (배정 후보 = user.id); 단건 `PATCH /work-schedules/{id} {assigned_user_id}`; 복수 `POST /work-schedules/bulk-assign {ids, assigned_user_id}` [전부 CONFIRMED]
- INPUT: 담당자 선택(users), 마감일
- MUTATION: assigned_user_id 저장 → 백엔드가 work_assignments 동기화(WP-04C: factory_id companion PRE-READ, 실패 시 409)
- RESULT: 배정 완료 → 목록 reload
- NEXT: 점검 시작(F)

## F. 점검 시작
- PAGE: my-inspection
- API: `POST /inspection/start/{wid} {inspector_name}`
- INPUT: inspector_name(localStorage user_name)
- MUTATION: 일정 상태 → 진행
- RESULT: 토스트 + 목록/통계 갱신
- NEXT: 점검 완료(G)

## G. 점검 완료
- PAGE: my-inspection(모달), inspection-calendar(완료처리)
- API: `POST /inspection/complete/{wid} {completed_at, summary}`; 캘린더는 `PATCH /work-schedules/{id} {status_code}`
- INPUT: 완료일, 요약
- MUTATION: 일정 상태 → 완료
- **⚠ P0-A**: inspection-calendar가 `{status_code:'COMPLETED'}`(대문자)로 write. canonical은 `completed`(소문자).
- RESULT: 토스트 + 갱신
- NEXT: 캘린더/대시보드 반영

## H. 설비 체크인 — GAP
- PAGE: **없음** (tai-admin/vue3에 `/equipment-checkins` 호출 0건)
- 백엔드: `equipment_checkins.py` LIVE. `POST /equipment-checkins`(익명 현장 스캔), `GET /equipment-checkins`(로그인 이력), `GET /equipment-checkins/{id}`
- 판정: 제출 UI(POST 익명)는 워커앱/PWA 소관(tai-admin scope 밖). 관리자 이력 UI(GET)는 tai-admin scope지만 미구현 → equipment-qr-manager 확장(MODIFY-L)으로 수용

## I. 점검 결과 / 증거
- PAGE: 완료처리(my-inspection/inspection-calendar) O. 증거/사진/첨부 조회 UI △(미확인)
- 백엔드: `evidence_bridge.py` LIVE, `document-engine/documents/{id}/evidence` LIVE
- 판정: 완료 흐름은 있으나 증거 조회/감사 UI 부재 → Runtime Document lifecycle(NEW)에 포함 검토

## J. 문서 작성 / 제출
- PAGE: document-forms(List + Generate)
- API: `GET /document-forms?per_page=200`; `GET /document-forms/{id}`; `POST /document-engine/documents {form_schema_id, factory_id, company_id, created_by}`; `PATCH /document-engine/documents/{docId} {runtime_data_json, updated_by}`; `POST /document-engine/documents/{docId}/generate {export_type}`
- INPUT: 서식 선택 + 동적 폼 입력
- MUTATION: runtime 문서 생성/동기화 → PDF 생성
- RESULT: PDF 미리보기/다운로드
- NEXT: (단건 완결. 횡단 검토/승인 lifecycle은 미구현 → NEW 후보)

## K. 캘린더 / 기한초과 / 알림
- PAGE: inspection-calendar(캘린더 그리드 + preview), my-inspection(기한초과 배지), safety-dashboard(overdue 위젯)
- API: `GET /work-schedules?planned_date_from=&planned_date_to=&factory_id=`; `GET /inspection-sets/factory-preview?factory_id=&months=2`; `GET /overdue/summary`, `/overdue/history`, `POST /overdue/urge/{id}`
- MUTATION: 완료처리(P0-A), 독촉 발송
- **⚠ P0-B/C**: 기한초과/미완료 판정에 `status_code !== 'DONE'` 사용 → canonical `completed` 오분류
- 알림(alert-list/notification-list): 백엔드 `notifications.py` LIVE. 프론트 페이지 존재하나 본 WP 미직독(별도 확인)

## L. 작업자 / 담당자 선택
- PAGE: worker-list
- API: 산업 `GET /worker-registry?factory_id=&job_type_code=&department_id/team_id/group_id=&is_active=&keyword=&page=&size=`; 건설 `GET /construction/sites/{id}/workers`; 캐스케이드 `/departments`, `/teams`, `/groups`
- 핵심 구분: **worker_registry(현장 작업자, TBM/교육 대상) ≠ users(시스템 계정, 담당자 배정 대상)**. 둘은 별도 엔티티, 프론트에서 통합 금지.
