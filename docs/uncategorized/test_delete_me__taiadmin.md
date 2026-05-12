# [SAFE] TAI Safe Phase 2 — safe.taieng.co.kr 프론트엔드 작업

**작성일:** 2026-04-16  
**배포 도메인:** safe.taieng.co.kr (Cloudflare Pages)

---

## 배경

2026-04-16 건설 모듈 BUG #1 수정 배포 완료. 3개 현장 DB 복구:
- 강남 센트럴타워 (200억/100명): applicable 207, schedules 178, sets 88
- [E2E테스트] (180억/55명): applicable 205, schedules 177, sets 80
- [검증] BUG#1 수정 (180억/55명): applicable 205, schedules 78, sets 80

---

## 작업 목록

### FS-01 🔴 E2E UI 검증 (기존 파일)
- construction-site-list.html — diagnosis_applicable_count 뱃지 실데이터 노출
- construction-inspection-anchor.html — LEGAL_ENGINE 80건 노출
- construction-process-list.html — KCSC 검색 동작

### FS-02 🔴 construction-work-list.html 신규 (PTW)
- API: GET/POST /construction/sites/{site_id}/works
- API: PATCH /construction/works/{work_id}/ptw
- ptw_number 채번: CS-{YYYY}-{5자리}
- ptw_status: DRAFT(기본) → APPROVED / REJECTED
- 필수: worker_count, assigned_manager_id
- 리스트: 체크박스(1번) + No.(2번)

### FS-03 🟡 construction-worker-list.html 신규
- DIRECT / SUBCON 작업자 관리
- 입장/퇴장 토글

### FS-04 🟡 construction-inspection-list.html 신규
- overall_result: bad 1건 → ISSUE
- 알림 자동 발송

### FS-05 🟢 safety-dashboard.html 날씨 위젯
- 기상청 API + 작업중지 법령 연계

---

## 개발 규칙

- 파일 경로: `tadmin/full-version/html/horizontal-menu-template/`
- 리스트: 첫 컬럼 체크박스(전체선택) + 두 번째 No.
- API: https://api.taieng.co.kr
- 참고: tai_forklift_check_ui_html.html UX 패턴 응용
