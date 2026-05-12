# 세션 작업 기록 — 2026-04-11 (tai-admin / safe.taieng.co.kr)

> 레포: taiengineering/tai-admin

---

## 핵심 발견: 실제 서빙 경로

**Cloudflare Pages 루트 = `tadmin/full-version/`**
- `site/full-version/` 는 서빙되지 않음 (이번 세션 초반 오류 경로)
- 이번 세션 초반에 `site/full-version/`에 잘못 배포했다가 점검 후 올바른 경로로 재배포 완료

---

## 완료 작업

### 1. `tadmin/full-version/assets/js/tai/menu-tadmin.js` v4.2.0 (commit: 37e0443)
- 안전정보(safety-info.html) 메뉴 추가 — quote(견적관리) 다음, mypage 앞
- 조건: `lv >= 1`, 아이콘: `tabler-news`

### 2. `tadmin/full-version/assets/js/tai/footer-nav.js` wx위젯 (commit: 37e0443)
- 대시보드(index.html) + WX_ALLOWED_ROLES 체크 후 기상 위젯 동적 삽입
- DOM에서 "다가오는 점검" row 앞에 삽입
- `wxInit()`, `wxCheck()` 전역 함수
- 정상: 파란 카드, 작업중지: 빨간 점멸 카드

### 3. `tadmin/full-version/html/horizontal-menu-template/safety-info.html` 신규 생성 (commit: 202262b)
- kma-weather v1.5.0: `api.taieng.co.kr/weather/now` + `/weather/alert`
- 위치: factory_lat/lon → GPS → 서울 기본
- work_stop.level → 카드 색상 (normal/caution/warning/stop)
- 업종필터 뉴스, 안전 Tip, 판례 하이라이트

---

## 잘못 배포된 파일 (site/full-version/ — 서빙 안됨)
- site/full-version/assets/js/tai/menu-tadmin.js
- site/full-version/assets/js/tai/footer-nav.js
- site/full-version/html/horizontal-menu-template/safety-info.html

---

## API 엔드포인트
| 엔드포인트 | 구조 |
|---|---|
| `GET /weather/now?lat=&lon=` | `{status, weather:{temperature,humidity,wind_speed,rain_1h,precip_type}, work_stop:{required,level,message,triggered}, observed}` |
| `GET /weather/alert` | `{status, alerts:[{region_name,type,level,work_stop_related}], has_work_stop_alert}` |

## PENDING
- `KAKAO_REST_API_KEY` Railway 환경변수 추가 필요
- `posts` 테이블 안전정보 실제 데이터 입력 (현재 fallback 샘플)
