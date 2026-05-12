# 크론 관리 화면 — 프론트엔드 작업 지시서
## 대상 레포: tai-admin
## 대상 파일: html/horizontal-menu-template/cron-list.html (NEW)

---

## 1. 메뉴 위치
어드민 사이드바: **시스템관리 > 크론 관리**

---

## 2. 화면 구성

### 상단: 통계 카드 (4개 가로)
- 전체 크론 수 (`GET /cron/stats` → `total_jobs`)
- 활성 크론 수 (`active_jobs`)
- 오늘 실행 회수 (`today_runs`)
- 오늘 실패 회수 (`today_failed`) — 0이면 녹색, 1이상이면 빨간색

### 중단: 크론 목록 테이블

**필터**: 카테고리 (ALL/LAW/DATA/SYSTEM/REPORT) + 활성/비활성

**컄럼명**:
| No | 코드 | 이름 | 카테고리 | cron 표현식 | 주기 설명 | 마지막실행 | 상태 | 조작 |

**상태 바지**:
- `SUCCESS` → 녹색 배지
- `FAILED` → 빨간 배지
- `RUNNING` → 노란 배지 (스피너 애니메이션)
- 덕(`-`) → 회색 (실행 이력 없음)

**조작 버튼**:
- ▶ 즉시실행 (POST `/cron/jobs/{job_code}/run`)
- ✏ 수정 (모달 오픈)
- ⏸ 활성/비활성 토글 (PATCH `/cron/jobs/{job_code}`)
- 휴지통 삭제 (시스템 크론 제외)

### 하단: 실행 로그
- 최근 50개 (`GET /cron/logs`)
- 콴럼: 실행시간 / 코드 / 트리거(SCHEDULE/MANUAL) / 소요시간 / 상태 / 결과 요약
- 실패로그는 빨간 배경색 하이라이트

---

## 3. 모달: 크론 수정

필드:
- 작업명 (job_name)
- 설명 (job_description)
- cron 표현식 (cron_expression) + 실시간 미리보기 (다음 실행 시각 계산)
- 주기 설명 (schedule_desc)
- 실패 알림 (notify_on_fail 토글)

다음 실행 시각 미리보기: cron 표현식 입력시 크론 파싱 라이브러리로 실시간 계산 표시
```javascript
// cron-parser 라이브러리 사용
// CDN: https://cdn.jsdelivr.net/npm/cron-parser@4.9.0/lib/index.js 내얭 없음
// 대신: API로 표현식 정보 텍스트로만 표시
```

---

## 4. 모달: 신규 크론 등록

필드:
- 코드 (job_code) — 영숫자+언더바 고정
- 이름 (job_name)
- 카테고리 (category) — select: LAW/DATA/SYSTEM/REPORT
- 엔드포인트 URL (endpoint_url)
- HTTP 메서드 (GET/POST)
- cron 표혉식
- 주기 설명
- 타임아웃(초)

---

## 5. API 연동 정리

| 사용 | 엔드포인트 |
|------|----------|
| 목록 조회 | GET /cron/jobs |
| 단건 조회 | GET /cron/jobs/{job_code} |
| 신규 등록 | POST /cron/jobs |
| 수정 | PATCH /cron/jobs/{job_code} |
| 삭제 | DELETE /cron/jobs/{job_code} |
| 즉시실행 | POST /cron/jobs/{job_code}/run |
| 로그 | GET /cron/logs |
| 통계 | GET /cron/stats |
| 리로드 | POST /cron/reload |

---

## 6. 완료 기준
- [ ] 크론 목록 화면 정상 조회
- [ ] 즉시실행 클릭 → 로그에 담조전 표시
- [ ] 토글 활성/비활성 정상 동작
- [ ] 신규 등록 / 수정 모달 작동
- [ ] 실행 로그 표시 (성공/실패 구분)
