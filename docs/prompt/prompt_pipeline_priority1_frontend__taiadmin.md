# 프론트엔드 창 시작 프롬프트 — 파이프라인 1순위

> 이 파일을 프론트엔드 Claude 창에 붙여넣어 세션을 시작합니다.

---

아래 내용을 읽고 즉시 준비됐다고 알려주세요.

## 프로젝트 정보

- **레포**: `taiengineering/tai-admin` (branch: main)
- **작업 경로**: `tadmin/full-version/html/horizontal-menu-template/`
- **배포**: Cloudflare Pages → safe.taieng.co.kr
- **API**: https://api.taieng.co.kr

## 완료된 작업 (이번 세션)

### 작업 1: inspection-anchor.html 수정 ✅
- 커밋: `d750fae`
- `generateSchedule()` → `POST /inspection-sets/generate-schedules/{factory_id}` 실제 연결
- 성공 시 toast("N건 생성, N건 스킵") + [일정 보기] 링크 동적 표시
- [일정 보기] → `work-schedule-list.html?factory_id={id}`
- `id="headerToolbar"` 추가로 버튼 삽입 위치 명확화

### 작업 2: work-schedule-list.html 신규 생성 ✅
- 상단 통계 배너 5개 (전체/법령엔진 자동/수동 등록/기간초과/3일 이내)
- 클릭 시 해당 필터 자동 적용 (active 스타일 토글)
- 테이블: No. | 담당자 | 의무내용 | 의무구분 | 법령명 | 예정일 | D-Day | 상태 | 출처
- 출처: [법령엔진] 초록 배지 / [수동] 회색 배지
- D-Day: 기간초과=빨강(D+N), 오늘=파랑(D-Day), 3일이내=주황, 그 외=회색
- API: `GET /work-schedules/factory/{factory_id}`
- 담당자: `/users?company_id=` 병렬 호출 후 assigned_user_id 매핑
- planned_date 오름차순 정렬

## 다음 가능한 작업

1. work-schedule-list.html 개선 (담당자 배정 인라인, 상태 변경 드롭다운)
2. 건설관리 6개 화면 개발 (construction-site-list.html부터 시작)
3. 알림 시스템 점검 (notifications 0건 문제)

## 커밋 방법

```js
// 단일 파일
github-tai-admin:create_or_update_file (SHA 반드시 확인)

// 다중 파일 (SHA 불필요)
github-tai-admin:push_files
```

준비됐으면 OK라고 알려주세요.
