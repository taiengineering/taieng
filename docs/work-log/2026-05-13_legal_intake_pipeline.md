# Legal Intake Pipeline Work Log
## 2026-05-13

## 작업
1. DB 3개 테이블 생성
   - legal_source_registry
   - legal_change_event
   - legal_intake_candidate
2. API 라우터 생성 (routers/legal_intake.py)
3. 6 endpoints (status, change-events, candidates, source-registry, run-cron, mark-review)
4. 자동 publish 차단 CHECK 제약

## 다음
- main.py v5.57.0 등록
- 법제처 API 키 연동
- Admin UI 메뉴 추가 (Cursor)
