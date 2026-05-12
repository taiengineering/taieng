# [FRONTEND] 건설 모듈 E2E UI 검증 작업

작성일: 2026-04-16
담당 윈도우: frontend (tai-admin)
긴급도: High — 백엔드 BUG #1 수정 배포 대기 후 착수
선행 조건: taiengineering/tai-api / docs/workorder-construction-e2e-backend-20260416.md 완료

## 배경
2026-04-16 E2E DB 테스트 결과 건설 모듈의 자동 진단·스케줄 파이프라인이 프로덕션에서 전혀 작동하지 않고 있었음. 백엔드 윈도우에서 construction.py BUG #1 + DB BUG #2 수정 중. 배포 완료 후 UI 레벨 끝까지 검증.

## 검증 대상 (tadmin/ 경로)

### 1. construction-site-list.html
API: GET/POST /construction/sites
- 신규 등록 폼: site_type(BUILDING/CIVIL), contract_amount(억), workers, manager_id
- 등록 응답: response.auto.diagnosis.applicable_count > 0 필수
- 목록에 diagnosis_applicable_count 뱃지
- 테스트: BUILDING 180억 55명 → safety_manager_required=true, 70건 이상

### 2. construction-inspection-anchor.html
API: GET /inspection-sets?factory_id=, PATCH /inspection-sets/{id}
- source=LEGAL_ENGINE 71건 내외 노출
- 빈 상태 runDiagnosis() 버튼 (FE-1 완료)
- 담당자 드롭다운 + 마지막 점검일 date picker
- 앵커 확정 → anchor_confirmed=true, status_code=ACTIVE
- 주의: 일정 완전 자동 생성 아님. 안전관리자가 이전점검일+점검자 지정 후 액션 버튼 필수.

### 3. construction-process-list.html
API: GET/POST /construction/sites/{site_id}/processes
- KCSC 자동검색 (FE-2 완료), 300ms 디바운스
- 선택 시 kcsc_process_id 자동 입력
- 테스트: 철근콘크리트, 거푸집, 가설공사 3개 등록

### 4. construction-work-list.html (PTW)
API: GET/POST /construction/sites/{site_id}/works, PATCH /construction/works/{work_id}/ptw
- ptw_number 자동 채번 (CS-YYYY-00001)
- ptw_status DRAFT 기본 → 승인 시 APPROVED
- worker_count, assigned_manager_id 필수

### 5. construction-worker-list.html
API: GET/POST /construction/sites/{site_id}/workers, PATCH /construction/workers/{worker_id}/entry
- worker_type: DIRECT / SUBCON (SUBCON 시 subcontractor_id)
- 입장/퇴장 토글 → entry_status + last_entry_at
- 테스트: DIRECT 3명 + SUBCON 2명 → 입장 처리

### 6. construction-inspection-list.html
API: GET/POST /construction/sites/{site_id}/inspections, PATCH /construction/inspections/{id}/corrective
- 리스트 표준: 첫 컬럼 체크박스(전체선택), 두 번째 No.
- overall_result 자동 계산: bad 1개 이상 → ISSUE
- ISSUE 선택 시 v2.1.0 백엔드 FCM 자동 발송
- photo_urls 업로드

## 검증 순서 (백엔드 배포 완료 후)
1. safe.taieng.co.kr 로그인 (안전관리자)
2. 현장 신규 등록 (BUILDING 180억 55명) → Network 탭에서 applicable_count > 0 확인
3. inspection-anchor → 71건 내외 노출 확인
4. 1~2개 set에 담당자+마지막 점검일 → 앵커 확정 → work_schedules.planned_date 갱신 확인
5. 공정 3개 등록
6. 작업자 5명 등록
7. 위험작업 1개 등록 → PTW 승인
8. 점검 1건 작성 → 1개 bad → 알림 수신 + DB ISSUE 확인
9. 대시보드에서 담당자 할당 확인

## 완료 기준
- [ ] 백엔드 BUG #1 배포 통보 수신
- [ ] 현장 신규 등록 플로우 통과 (자동진단 > 0)
- [ ] inspection-anchor 법령 기반 리스트 확인
- [ ] 공정/작업/작업자 CRUD 동작
- [ ] 점검 ISSUE 알림 수신 검증
- [ ] 담당자 할당 UI 최종 확인

## 참고
- UI 표준: 첫 컬럼 체크박스, 두 번째 No.
- 작업 전 system_codes 전역변수 확인 (globals.js)
- 테스트 도구: DevTools Network + Console
- 관련 백엔드: taiengineering/tai-api / docs/workorder-construction-e2e-backend-20260416.md
