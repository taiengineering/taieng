# Engine Monitoring Admin Integration
## 2026-05-13

## 작업

1. `routers/engine_monitoring.py` 생성 (7 endpoints)
2. `tadmin/full-version/html/admin/engine-monitoring.html` 생성
3. Summary + 6 Tab 구조 구현
4. 감사 실행 버튼 (/integrity/run-audit 연결)
5. 60초 자동 갱신

## API 라우터
- engine_monitoring.py: 7 endpoints
- integrity_monitor.py: 4 endpoints (Phase I 에서 생성)

## 다음 단계
main.py v5.55.0 등록
