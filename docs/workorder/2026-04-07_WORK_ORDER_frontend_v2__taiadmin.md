# 프론트 작업지시서 v2 (2026-04-07 재지시)

## 확인된 현재 상태
- safety-dashboard.html: 없음 (두 디렉토리 모두 확인 완료)
- 대상: tadmin (tadmin.taieng.co.kr)
- tadmin 경로: site/full-version/html/vertical-menu-template-no-customizer/
- assets 경로: ../../assets/ (확인 완료)
- 메뉴는 HTML 안에 직접 포함 (menu-tadmin.js 방식 아님)

---

## 작업: safety-dashboard.html 생성

### 저장 경로
`site/full-version/html/vertical-menu-template-no-customizer/safety-dashboard.html`

### 참고 템플릿 구조
- `dashboards-analytics.html` (vertical-menu-template-no-customizer 디렉토리에 있음)의 헤더/nav/푸터 구조 그대로 복사
- `data-template="vertical-menu-template-no-customizer"` 유지
- `../../assets/` 경로 기준

---

### 화면 구성

#### 1. 상단 요약 카드 (4개 가로 배치)
| 카드 | 색상 | 내용 |
|---|---|---|
| D-0 마감 | bg-label-danger | 오늘 planned_date 건수 |
| D-3 이내 | bg-label-warning | 3일 이내 planned_date 건수 |
| 이번달 | bg-label-primary | 이번달내 planned_date 건수 |
| 미배정 | bg-label-secondary | assigned_user_id = null 건수 |
- 각 카드 클릭 시 하단 테이블에 필터 적용

#### 2. 일정 목록 테이블
칸럼: No. | 설명 | 법령 | 마감일 | 담당자 | 상태
- 담당자가 없으면 [미배정] 보라색 배지 + 클릭시 배정 모달 오픈
- 마감일 D-0이면 빨간색 헤더

#### 3. 담당자 배정 모달
- 제목: 담당자 배정
- 그룹 선택드롭다운 (API: GET /groups?factory_id=...)
- 작업자 선택드롭다운 (API: GET /users?group_id=...)
- 배정하기 버튼: PATCH https://api.taieng.co.kr/work-assignments/{id}
- 성공 시: 모달 닫기 + 테이블 즉시 갱신

---

### API 엔드포인트
```
GET  https://api.taieng.co.kr/work-schedules?factory_id={id}&source_type=LEGAL
GET  https://api.taieng.co.kr/work-assignments?factory_id={id}
PATCH https://api.taieng.co.kr/work-assignments/{id}
GET  https://api.taieng.co.kr/legal-engine/result/{factory_id}
```

### factory_id 처리
- localStorage에서 `selectedFactoryId` 가져오거나
- URL 파라미터로 받기 (?factory_id=...)
- 없으면 테스트 ID 하드코딩 허용

---

### 사이드 패널 (우측)
- 선임 N건 / 점검 N건 / 신고 N건
- GET /legal-engine/result/{factory_id}에서 summary 데이터 파싱

---

### 주의사항
1. dashboards-analytics.html 확인 후 동일 헤더/네비게이션/푸터 구조 사용
2. 완료 후 SHA 처리 필요 없음 (신규 파일)
3. work_schedules 코럼 구조: id, factory_id, company_id, description,
   law_name, law_article, planned_date, status_code, assigned_user_id,
   obligation_type, source_type, rule_code
4. API 응답에서 데이터 없으면 빈 화면 + 상태메시지 표시
5. 확인 후 보고: 실제로 파일이 push됐는지 SHA 반드시 명시
