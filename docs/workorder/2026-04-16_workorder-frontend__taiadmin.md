# TAI Safe 프론트 작업지시서 통합본 (2026-04-16)

기획창 2026-04-16 시나리오 테스트 세션 결과물.
3개 작업(FN-03/04/05) 순차·병렬 실행.

**공통 규칙**
- dev 브랜치 전용 (main 직접 커밋 금지)
- 카카오 API 일체 금지 (지도/로그인/알림톡/공유 포함)
- 모바일 360~375px 가독성 필수
- Vuexy 템플릿 + Bootstrap 5 최대 활용
- 과장 표현 금지 ("100% 안전" 같은 단정 표현)

**선행 조건 (백엔드 선 완료 필수)**
```
BE-05 완료 → FN-03 착수
BE-06 완료 → FN-05 착수
BE-07 완료 → FN-04 착수
```

---

## 🎨 FN-03. 법령진단 입력 폼 UX 전면 개편 [P1, 의존: BE-05]

### 배경
체크박스 35개 연속(BUILDING), 자유텍스트 남용, "모름" 선택 불가,
건축물대장 자동채움 부재.

### 기획창 확정 UX 5원칙
1. boolean → 3지선다 (예/아니오/모름)
2. 자유텍스트 → 배열·테이블 UI
3. 체크박스 연속 15개↑ 금지 → 그룹 접기
4. 자동채움 우선 (주소→대장, 사업자번호→공공데이터)
5. UNKNOWN 값은 결제 후 보완 동선 제공

### 할 일

**1) 공통 컴포넌트 6종 제작** (`tai-admin/assets/js/diagnosis-inputs/`)
- **TriStateToggle** — 예/아니오/모름 버튼 3개 토글
  - 예=primary, 아니오=secondary, 모름=outline-warning
- **ProcessTable** — 공정 목록 테이블 (행 추가/삭제, inline validation)
- **SubcontractorTable** — 하도급 업체 테이블
- **MultiSelectGroup** — 그룹화된 체크박스 + 접힘
- **AutofillAddress** — 주소 입력 + 건축물대장 자동채움 버튼
- **AutofillBiz** — 사업자번호 입력 + 공공데이터 자동채움 버튼

**2) BUILDING 입력화면 개편**
- 36개 필드 중 25개 boolean → TriStateToggle
- 5그룹 접힘(기본 닫힘): 소방(5)/위험물(4)/수질환경(4)/다중이용(2)/특수시설(4)
- 주소 필드에 AutofillAddress (7필드 자동채움 연계)

**3) CONSTRUCTION 입력화면 개편**
- `process_list` → ProcessTable (공정명+위험요소 다중선택)
- `subcontractor_count` → SubcontractorTable (행별 상세)
- 위험시설 9개 → 접힘 그룹
- `operation_shift` 라디오 추가 (1교대/2교대/3교대/24시간/유연/모름)

**4) INDUSTRY 입력화면 개편 (PAID1/2/3)**
- PAID1 위험물 9개 체크박스 그룹화
- PAID1에 `operation_shift` 라디오 필수 추가
- PAID2 `process_worker_data` 자유텍스트 → ProcessTable (공정명/직영/하도급/교대)
- PAID3 설비 10개 체크박스 그룹화

**5) "모름" 값 결제 후 보완 UX**
- 결제 완료 화면에 "추가 확인이 필요한 N건" 박스
- "지금 입력하기" 버튼 → `/diagnosis/fill-gaps`
- 나중에 입력 가능 (`diagnosis_status='PAID_PENDING_INPUT'`)

### 디자인 토큰
- Vuexy + Bootstrap 5
- 필수 필드: 빨강 별표
- 자동채움: 녹색 뱃지

### 산출물
- `pages/diagnosis/input-building.html`
- `pages/diagnosis/input-construction.html`
- `pages/diagnosis/input-industry-paid1.html`
- `pages/diagnosis/input-industry-paid2.html`
- `pages/diagnosis/input-industry-paid3.html`
- `pages/diagnosis/fill-gaps.html`
- `assets/js/diagnosis-inputs/*.js` (6개 컴포넌트)

### 완료 조건
- 체크박스 연속 15개↑ 화면 0개
- 자유텍스트 필드 0개 (주소·회사명 제외)
- 주소·사업자번호 자동채움 동작 확인
- 모바일 375px 입력 완주

---

## 🎨 FN-04. ROI 대시보드 (1장 설득 이미지) [P1, 의존: BE-07]

### 배경
"현재 리스크 4,800만원 → TAI Safe 948K + 2주 실천 = 리스크 0원"을
**단 1장의 이미지**로 설득. 건물주·공장장·현장소장이 경영진 보고용 PDF로 제출 가능한 품질.

### 할 일

**1) 신규 페이지** `pages/diagnosis/roi-dashboard.html`
- URL: `safe.taieng.co.kr/diagnosis/{diagnosis_id}/roi`
- 로그인 필수, 본인/같은 company만 접근

**2) 페이지 구조 (반응형 360~1920px)**
```
[상단]    회사명·건물명·생성일시
[히어로]  좌(빨강) 현재리스크 4,800만원
          VS
          우(녹색) TAI Safe 948K
          가운데 큰 화살표 + ×50 배율
[중단]    3열 카드:
          ① 감소율 95%  ② 손익분기 7일  ③ 실천 2주
[하단1]   Before/After 막대그래프 (Chart.js, CSS 애니메이션)
[하단2]   포함기능 3줄 (자동일정/D-3알림/체크리스트)
[하단3]   추천 플랜(STARTER/BUSINESS/ENTERPRISE) + CTA 2개
          - "지금 구독" → KG이니시스 바로결제
          - "의사결정용 PDF 저장" → window.print() or html2pdf
```

**3) PDF 저장 기능**
- html2pdf.js 라이브러리 (CDN)
- @media print 전용 CSS
- 파일명: `TAI_Safe_ROI_{회사명}_{yyyymmdd}.pdf`
- A4 1장 정확히 맞춤

**4) 데이터 연결**
- `GET /diagnosis/{id}/roi` API 한 번으로 전체 렌더
- roi 데이터 없으면 "재진단 필요" 배너 (v2026.04 미만 대응)

**5) "이 리포트로 할 수 있는 것" 섹션**
- 1장 PDF 다운로드
- 경영진 보고용 이미지
- 본사 안전팀 공유 URL (이메일/슬랙만, 카카오 금지)

### 디자인 원칙
- 숫자가 주인공 (금액 최소 font-size 32px)
- 색상: 리스크=#dc2626, 구독=#059669
- 아이콘: lucide-icons 또는 bootstrap-icons
- 장식 금지 — 임원 의사결정 문서 톤

### 산출물
- `pages/diagnosis/roi-dashboard.html`
- `assets/js/roi-dashboard.js`
- `assets/css/roi-dashboard.css` (print 포함)

### 완료 조건
- 3초 내 렌더
- PDF A4 1장 정확히 맞춤
- 모바일 360px 설득력 유지

### 금기
- 카카오 공유·로그인 금지
- 과장 표현 금지
- 리스크 수치 임의 생성 금지 (API 응답 기반만)

---

## 🎨 FN-05. 결과 리포트 v2026.04 렌더러 [P2, 의존: BE-06]

### 배경
기존 result_html 생성 로직 미확인. 결제 후 실물 리포트 부재.
v2026.04 단일 스키마로 4 sector × 4 tier 전부 렌더.

### 할 일

**1) 페이지** `pages/diagnosis/report.html`
- URL: `safe.taieng.co.kr/diagnosis/{diagnosis_id}/report`

**2) 렌더 섹션 (v2026.04 필드 매핑)**
- 표지: 회사명·sector·tier·generated_at·valid_until·schema_version
- 헤드라인: `headline.summary` + severity 배지
- 적용 법령: `applicable_laws` 테이블
- 의무사항: `obligations` 카드형 (risk_level별 정렬, evidence 접힘)
- 위험 요약: `risk_summary` 도넛차트
- 경고: `warnings` 리스트 (level별 색상)
- 점검 스케줄: `inspection_schedule` 캘린더 히트맵
- 노출액: `exposure.penalty_max_krw` 강조
- 다음 액션: `next_actions` 버튼 행
- ROI 미니카드: `roi` 필드 요약 + "자세히" → FN-04 이동

**3) 3가지 형식 동시 지원**
- 화면 보기 (HTML 반응형)
- 인쇄용 PDF (@media print, A4 4~8장)
- 요약 1장 PDF (ROI 대시보드 재활용)

**4) 공통 컴포넌트 5종** (`assets/js/diagnosis-report/`)
- ObligationCard
- EvidencePanel (접힘식 근거)
- RiskGauge (도넛)
- ScheduleCalendar (히트맵)
- ExposureCard

**5) 결과 내 진단 동선**
- obligations 각 항목 "해결하기" 버튼 → `action_url`
- TAI Safe 구독자: 자동일정·담당자 배정 노출
- 비구독자: "구독시 자동처리됨" 배지 + CTA

**6) 누락 필드 graceful fallback**
- v2026.04 미만 스키마는 "업데이트 필요" 배너 + 마이그레이션 유도
- 누락된 선택적 필드는 섹션 자체 숨김

### 산출물
- `pages/diagnosis/report.html`
- `assets/js/diagnosis-report/*.js` (5개 컴포넌트)
- `assets/css/diagnosis-report.css` (print 포함)

### 완료 조건
- 4 sector × 4 tier (INDUSTRY 4단계 + BUILDING/CONSTRUCTION 2단계) 전부 렌더
- 인쇄 PDF A4 출력 정상
- 모바일 360px 가독성

### 금기
- v2026.04 미준수 JSON 임의 보완 렌더링 금지 (버전 배너만)
- 카카오 공유 금지

---

## 📊 진행 보고 규칙

각 작업 완료시 기획창에 보고:
- PR 링크
- 스크린샷 (before/after, 모바일 포함)
- 특이사항/블로커

---

## 🚀 실행 프롬프트 (이 문서 받고 바로 복붙)

```
TAI Safe 프론트 작업 착수.
저장소: tai-admin (dev 브랜치)

순서:
1. BE-05 완료 확인 → FN-03 즉시 착수 
   (공통 컴포넌트 6종 먼저 만들고 sector별 화면 조립)
2. BE-07 완료 → FN-04 착수 (1장 PDF가 핵심 결과물)
3. BE-06 완료 → FN-05 착수 (FN-04와 병렬 가능)

참고: workorder-frontend-20260416.md

제약:
- 카카오 API 일체 금지
- 모바일 360px 가독성 필수
- Vuexy 템플릿 최대 활용
- main 직접 커밋 금지

각 작업 완료시 PR + 스크린샷 보고.
```
