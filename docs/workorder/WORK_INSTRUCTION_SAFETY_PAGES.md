# 작업지시서: 안전정보 4개 페이지 정비

## 개요

`taieng` 레포 (`nexas/` 폴더)의 안전정보 메뉴 4개 페이지를 정비합니다.
각 페이지는 **최신 자료 리스트 + 검색** 구조로 만듭니다.

## 공통 규칙

### Supabase 접속 정보
```javascript
const SB = 'https://vwlahtguyggrhvslabax.supabase.co/rest/v1';
const KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bGFodGd1eWdncmh2c2xhYmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyOTE1OTYsImV4cCI6MjA5Mjg2NzU5Nn0.Yp6P7ahaCuna_gwYC8_S2KD081Ov9Fs65e9o_AenP48';
const H = { 'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Prefer': 'count=exact' };
```

### 페이지 공통 구조 (4개 모두 동일)
```
1. Hero 섹션 (상단)
   - 페이지 제목 + 설명
   - 검색바 (대형, Enter/버튼 검색)
   - 통계 숫자 (3~4개)

2. 최신 자료 리스트 (검색 전 기본 표시)
   - 페이지 진입 시 최신 20건 자동 로드
   - 카드 형태로 리스트 표시
   - 각 카드: 제목 + 분류배지 + 날짜 + 링크버튼

3. 필터 칩 (검색바 아래)
   - 카테고리 / 업종 필터
   - 클릭 시 즉시 필터링

4. 검색 결과 + 페이지네이션
   - 검색어 입력 시 검색 결과로 전환
   - URL 파라미터 지원 (?q=추락&cat=CASE_STUDY&page=2)
   - 번호형 페이지네이션

5. 푸터 출처 표시
   - "본 자료는 한국산업안전보건공단에서 공공누리 제1유형으로 개방한 공공저작물입니다."
```

### 공통 HTML 템플릿
```html
<link rel="icon" href="assets/img/fevicon.png">
<link rel="stylesheet" href="assets/css/bootstrap.min.css">
<link rel="stylesheet" href="assets/css/fontawesome.min.css">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/tai-main.css">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">

<!-- body class="sc5" -->
<div id="tai-header"></div>
<!-- 페이지 콘텐츠 -->
<div id="tai-footer"></div>

<script src="assets/js/jquery.3.6.min.js"></script>
<script src="assets/js/bootstrap.min.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/header.js"></script>
<script src="assets/js/nav-auth.js"></script>
<script src="assets/js/footer.js"></script>
```

### 디자인 공통 규칙
- Hero 배경: 그라데이션 (페이지별 색상 다름)
- 검색바: max-width 640px, border-radius 16px, 포커스 시 마우스 형태 변경
- 카드: #fff 배경, 1.5px border #e8eaed, border-radius 14px, hover 시 shadow
- 필터 칩: border-radius 999px, active 시 #0d1b2a 배경 + 흰색 글자
- 페이지네이션: 번호 버튼형, active 시 #0d1b2a
- 모바일 대응: @media(max-width:768px) 에서 카드 단일 컬럼
- 글씨: 'Noto Sans KR', sans-serif

---

## 페이지 1: 안전자료 (safety-news.html) — 수정

### 현재 상태
- 파일: `nexas/safety-news.html` (이미 존재)
- 현재: 검색 결과만 표시, 최신 리스트 없음
- **수정 필요: 검색 전 최신 20건 리스트 표시 추가**

### DB 테이블: `kosha_safety_materials`
```
id (text PK), title (text), url (text), 
category (text), sector (text),
product_type (text), collected_at (timestamptz)
```

### 카테고리 값
```javascript
const CAT_LABEL = {
  EDUCATION: '교육자료', CASE_STUDY: '사고사례', GUIDE: '가이드',
  POSTER: '포스터·홍보', VIDEO_VR: '영상·VR', HEALTH: '보건·건강',
  RESEARCH: '연구·보고서', CHECKLIST: '체크리스트',
  FOREIGN: '외국인자료', REGULATION: '법령', OTHER: '기타'
};
const SEC_LABEL = { CONSTRUCTION: '건설', MANUFACTURING: '제조', SERVICE: '서비스', COMMON: '공통' };
```

### Hero 색상: navy gradient
```css
background: linear-gradient(160deg, #0d1b2a 0%, #1a3a5c 100%);
```

### API 호출 예시
```javascript
// 최신 20건 (기본 표시)
fetch(`${SB}/kosha_safety_materials?select=id,title,url,category,sector&order=collected_at.desc&limit=20`, {headers: H})

// 검색
fetch(`${SB}/kosha_safety_materials?select=id,title,url,category,sector&title=ilike.*${q}*&order=collected_at.desc&limit=20&offset=${offset}`, {headers: H})

// 카테고리 필터
fetch(`${SB}/kosha_safety_materials?...&category=eq.EDUCATION`, {headers: H})

// 업종 필터
fetch(`${SB}/kosha_safety_materials?...&sector=eq.CONSTRUCTION`, {headers: H})

// 건수 (컨텐트-레인지 헤더에서)
const total = parseInt(response.headers.get('content-range')?.split('/')[1] || '0');
```

### 필터 구성
- 자료유형: 전체 / 교육자료 / 사고사례 / 가이드 / 포스터 / 영상·VR / 보건 / 연구 / 체크리스트 / 외국인
- 업종: 전체 / 건설 / 제조 / 서비스

### SEO
```html
<title>안전보건자료 검색 | TAI 엔지니어링 — 산업안전 교안·사례·가이드 10,000건+</title>
<meta name="description" content="KOSHA 안전보건자료 10,000건 이상 무료 검색. 교안, 사고사례, 가이드, 포스터, VR 영상 등.">
<link rel="canonical" href="https://taieng.co.kr/safety-news">
```

### 핵심 수정 사항
1. `fetchResults()` 함수에서 검색어가 없을 때 `최신 자료` 섹션 표시
2. 검색어 입력 시 검색 결과로 전환
3. 아이콘 + 카테고리 배지로 카드 표시

---

## 페이지 2: 재해사례 (accident-cases.html) — 신규 생성

### DB 테이블: `kosha_accident_cases`
```
id (text PK), title (text), business (text), 
content (text - HTML), board_no (text), 
reg_dt (text), collected_at (timestamptz)
```

### 데이터 특성
- title 예시: `[4/17, 서울 성북구] 이동식 비계에서 도장 작업 중 바닥으로 떨어짐`
- title에 날짜(월/일)+ 지역이 포함되어 있음
- content는 HTML (KOSHA 포털 원본) — 표시할 때 텍스트만 추출하거나 HTML 렌더링
- **2,802건**

### 추가 테이블: `kosha_construction_accidents`
```
id (text PK), accident_type (text), work_type (text),
occurrence_date (text), accident_summary (text),
risk_reduction (text), collected_at (timestamptz)
```
- **1,039건** (건설업 일별 중대재해)
- 이 데이터는 탭으로 분리하거나 통합 표시

### Hero 색상: red gradient
```css
background: linear-gradient(160deg, #1a0000 0%, #7f1d1d 50%, #991b1b 100%);
```

### 필터 구성
- 탭: 국내재해사례 (2,802건) / 건설중대재해 (1,039건)
- 검색: title 필드에서 ilike 검색

### API 호출
```javascript
// 국내재해사례 최신 20건
fetch(`${SB}/kosha_accident_cases?select=id,title,board_no,reg_dt&title=neq.&order=collected_at.desc&limit=20`, {headers: H})

// 검색
fetch(`${SB}/kosha_accident_cases?select=id,title,board_no,reg_dt&title=ilike.*${q}*&order=collected_at.desc&limit=20&offset=${offset}`, {headers: H})

// 건설중대재해 최신 20건
fetch(`${SB}/kosha_construction_accidents?select=id,accident_type,work_type,occurrence_date,accident_summary&order=collected_at.desc&limit=20`, {headers: H})
```

### 카드 디자인 (재해사례)
```html
<div class="ac-card">
  <div class="ac-icon"><i class="fas fa-exclamation-triangle"></i></div>
  <div>
    <div class="ac-title">[4/17, 서울 성북구] 이동식 비계에서 도장 작업 중 바닥으로 떨어짐</div>
    <div class="ac-meta">
      <span class="badge badge-danger">사망 1명</span>
    </div>
  </div>
</div>
```

### SEO
```html
<title>재해사례 검색 | TAI 엔지니어링 — 산업재해 사고사례 2,800건+</title>
<meta name="description" content="KOSHA 국내 산업재해 사고사례 2,800건 이상 검색. 추락, 끼임, 충돌, 감전 등 재해사례를 확인하고 유사 사고를 예방하세요.">
<link rel="canonical" href="https://taieng.co.kr/accident-cases">
```

---

## 페이지 3: 개정법령 (law-updates.html) — 수정

### 현재 상태
- 파일: `nexas/law-updates.html` (이미 존재)
- 현재 작동 중 (95건 정상 출력)
- 수정 최소화: 공통 디자인 톤에 맞추기만 하면 됨

### DB 테이블: `law_revision_board`
```
id (uuid PK), law_name (text), law_type (text),
revision_type (text), revision_date (date), 
enforcement_date (date), summary (text), body (text),
affected_sectors (jsonb), impact_level (text),
source_url (text), status (text='PUBLISHED'),
is_public (boolean=true)
```

### Hero 색상: navy gradient (안전자료와 동일)
```css
background: linear-gradient(160deg, #0d1b2a 0%, #1a3a5c 100%);
```

### 필터
- 섹터: 건물·시설 / 산업·제조 / 건설 / 공통
- 연도: 2026 / 2025 / 전체
- 개정 유형: 일부개정 / 타법개정
- 영향도: 높음 / 보통 / 낮음

### API 호출
```javascript
// 최신 20건
fetch(`${SB}/law_revision_board?is_public=eq.true&status=eq.PUBLISHED&order=revision_date.desc&limit=20&select=law_name,law_type,revision_type,revision_date,enforcement_date,summary,affected_sectors,impact_level,source_url`, {headers: H})
```

### 핵심 수정 사항
- 기존 레이아웃(2칸 스플릿)을 유지하되, 최신 자료 리스트가 우측에 기본 표시되는지 확인
- 날짜 포맷이 일관되게 표시되는지 확인
- 이미 작동 중이므로 큰 변경 불필요

---

## 페이지 4: 판례검색 (precedent-search.html) — 점검

### 현재 상태
- 파일: `nexas/precedent-search.html` (이미 존재)
- 현재 작동 중인지 확인 필요

### DB 테이블: `industrial_accident_precedents`
```
id (uuid PK), case_number (text), case_name (text),
court_name (text), decision_date (text), 
sector (text), hazard_type (text), 
summary (text), source_url (text),
accident_type (text), death_count (int), injury_count (int)
```
- **849건**

### Hero 색상: dark blue-purple gradient
```css
background: linear-gradient(160deg, #0f172a 0%, #312e81 100%);
```

### 필터
- 섹터: 건설 / 제조 / 서비스 / 전체
- 재해유형: 추락 / 끼임 / 충돌 / 감전 / 질식 등

### API 호출
```javascript
// 최신 20건
fetch(`${SB}/industrial_accident_precedents?select=id,case_name,court_name,decision_date,sector,hazard_type,summary,death_count,injury_count&order=created_at.desc&limit=20`, {headers: H})

// 검색
fetch(`${SB}/industrial_accident_precedents?select=...&case_name=ilike.*${q}*&order=decision_date.desc&limit=20&offset=${offset}`, {headers: H})
```

### 카드 디자인 (판례)
```html
<div class="pr-card">
  <div class="pr-court">대법원</div>
  <div class="pr-title">업무상과실치사·산업안전보건법위반</div>
  <div class="pr-meta">
    <span>사망 1명</span>
    <span>추락</span>
    <span>2025-03-15</span>
  </div>
  <div class="pr-summary">요약 텍스트...</div>
</div>
```

### 핵심 수정 사항
- 현재 페이지가 정상 작동하는지 확인
- 최신 판례 리스트가 기본 표시되는지 확인
- 안 되면 safety-news.html과 동일한 구조로 재구성

---

## 메뉴 구조 (이미 header.js에 반영됨)

```
안전정보 >
  ├ 안전자료      (safety-news.html)        ← 10,000건+ 검색 중심
  ├ 재해사례      (accident-cases.html)     ← 2,802+1,039건 ★신규
  ├ 개정법령      (law-updates.html)        ← 95건 기존 유지
  └ 판례검색      (precedent-search.html)   ← 849건 점검
```

## 작업 우선순위

1. **accident-cases.html 신규 생성** (재해사례 페이지 없음)
2. **safety-news.html 수정** (최신 리스트 추가)
3. **precedent-search.html 점검** (작동 확인 후 필요시 수정)
4. **law-updates.html 점검** (대부분 작동 중, 미세 조정)

## 주의사항

- 모든 페이지에서 Supabase anon key는 위의 공통 규칙의 KEY 값을 사용
- 외부 링크로 내보내지 않음 (TAI 원칙) — 단, KOSHA 원문 URL은 '자료 보기' 버튼으로 제공 (향후 내부 Storage로 전환 예정)
- 출처 표시 필수: "출처: 한국산업안전보건공단 (portal.kosha.or.kr)"
- git push origin main → Cloudflare 자동배포
- header.js, footer.js는 수정하지 마세요 (이미 메뉴 반영됨)
