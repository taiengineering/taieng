# TASK: 네이버 지식iN 모니터링 파이프라인

## 목적

- 산업안전·과태료 등 **키워드로 지식iN 검색 결과를 주기적으로 수집**하고 **Supabase `naver_kin_log`에 적재**한다.
- **자동 답변·자동 게시·스팸성 게시 로직은 포함하지 않는다.** (읽기 전용 모니터링)

## 데이터 소스

- 네이버 오픈 API **지식iN 검색** (`/v1/search/kin.json`)
- 인증: `X-Naver-Client-Id`, `X-Naver-Client-Secret`

## 저장소

- Supabase 테이블 `public.naver_kin_log` (스키마는 저장소 `README.md`의 SQL 참고)

## 실행 환경

- **Railway** Cron 서비스 (UTC 기준 스케줄)
- 일일 실행 예: **KST 09:00 = UTC 00:00** → `cronSchedule`: `0 0 * * *`

## 스크립트

- `naver_monitor.py`: 검색 → 중복 제외 적재 → 종료 (장기 실행 없음)

## 금지 사항

- 지식iN·블로그·카페 등 **어떤 형태의 자동 게시/답변 API 호출도 넣지 말 것.**
