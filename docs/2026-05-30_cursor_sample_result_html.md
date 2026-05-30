# TAI 법령진단 결과 페이지 검증 및 고객 공개용 샘플 생성 — Cursor 작업지시서 v2

> 작성일: 2026-05-30 (v2: paid-diagnosis-result.html 기반으로 전면 교체)
> 대상: taiengineering/taieng (nexas/), taiengineering/tai-api (routers/)
> 기준 파일: **`nexas/paid-diagnosis-result.html`** (41KB, 유료 결과 7섹션 대시보드)
> 목적: 기존 결과 페이지 검증 → 목업 데이터 적용 → 고객 공개용 정적 HTML 3개 생성

**본 작업은 신규 기능 개발이 아니다. 기존 결과 페이지 검증 및 활용이 목적이다.**
**고객에게 보여줄 결과 수준은 무료 결과가 아니라 유료 결과 수준이다.**

---

## 1단계. 기존 결과 페이지 점검

### 대상 파일

| 파일 | 위치 | API | 역할 |
|---|---|---|---|
| `free-diagnosis-result.html` | nexas/ | `GET /diagnosis/result/{token}` | 무료 결과 (5건 미리보기) |
| `paid-diagnosis-result.html` | nexas/ | `GET /diagnosis/paid-result/{token}` | 유료 결과 (전체, 7섹션) |
| `diagnosis_result_web.py` | tai-api/routers/ | — | 백엔드 JSON API |

### 점검 방법

Supabase에서 ACTIVE 토큰 조회:
```sql
SELECT public_token, tier_code, status
FROM anonymous_diagnosis_results
WHERE status = 'ACTIVE'
ORDER BY created_at DESC
LIMIT 5;
```

URL 접속:
```
https://taieng.co.kr/free-diagnosis-result?token={public_token}
https://taieng.co.kr/paid-diagnosis-result?token={public_token}
```

### 점검 체크리스트

| # | 항목 | free | paid | 상태(정상/오류/수정필요) |
|---|---|---|---|---|
| 1 | API 호출 정상 | | | |
| 2 | 데이터 바인딩 정상 | | | |
| 3 | 위험도 헤더 | | | |
| 4 | 요약 KPI | | | |
| 5 | 법령 배지/목록 | | | |
| 6 | 법령 상세 | | | |
| 7 | 긴급 조치 섹션 | | | |
| 8 | 과태료 분석 | | | |
| 9 | 점검 타임라인 | | | |
| 10 | 체크리스트 | | | |
| 11 | PDF 다운로드 | | | |
| 12 | 법령 원문 링크 | | | |
| 13 | CTA 링크 | | | |
| 14 | 모바일 반응형 | | | |
| 15 | JS 콘솔 에러 | | | |

---

## 2단계. 목업 데이터

paid-diagnosis-result.html의 `init()` 함수는 API 응답 JSON `d`를 받아 렌더링한다.
정적 샘플에서는 이 JSON을 `SAMPLE_DATA`로 직접 임베딩.

### 건설업 SAMPLE_DATA

아래 참조. **실제 법령·조문·과태료 기준으로 작성.**

건설업 특징: 산안법+중대재해법+건설기술진흥법 3법 중심, 고소작업·중장비·전기작업 포함, 150명.

```javascript
const SAMPLE_DATA = {
  public_token: "SAMPLE-CONSTRUCTION",
  tier_code: "CONSTRUCTION",
  is_free: false,
  sector: "CONSTRUCTION",
  sector_label: "건설",
  company_name: "한국건설산업(주) 강남 현장",
  risk_level: "HIGH",
  risk_reason: "적용 법령 14개, 긴급 항목 6건, 중대재해법 적용 대상",
  applicable_count: 156,
  engine_version: "v3.0-runtime-compiler",
  summary: {
    total: 156, inspection: 38, appointment: 12,
    action: 78, report: 28, form_linked: 89,
    law_count: 14, worker_count: 150, csia_applicable: true
  },
  obligation_counts: { "선임":12, "점검":38, "조치":78, "보고":18, "신고":10 },
  warnings: ["중대재해처벌법 적용 대상 사업장입니다. 안전보건관리체계를 즉시 구축하십시오."],
  rules_table: [
    { rule_id:"c-01", law_name:"산업안전보건법", law_article:"제15조", obligation_type:"APPOINT", category:"선임",
      obligation_summary:"안전보건관리책임자 선임", penalty_summary:"5억원 이하 벌금",
      submit_org_label:"고용노동부", executor_type_label:"사업주", due_days:3 },
    { rule_id:"c-02", law_name:"산업안전보건법", law_article:"제17조", obligation_type:"APPOINT", category:"선임",
      obligation_summary:"안전관리자 선임 (건설 120명 이상)", penalty_summary:"500만원 이하 과태료",
      submit_org_label:"고용노동부", executor_type_label:"사업주", due_days:5 },
    { rule_id:"c-03", law_name:"산업안전보건법", law_article:"제29조", obligation_type:"ACTION", category:"조치",
      obligation_summary:"신규 채용 시 안전보건교육 (8시간)", inspection_cycle:"채용 시",
      penalty_summary:"500만원 이하 과태료", submit_org_label:"자체보관", executor_type_label:"안전관리자", due_days:7 },
    { rule_id:"c-04", law_name:"산업안전보건법", law_article:"제29조", obligation_type:"ACTION", category:"조치",
      obligation_summary:"특별안전보건교육 (고소작업 16시간)", inspection_cycle:"작업 전",
      penalty_summary:"500만원 이하 과태료", submit_org_label:"자체보관", executor_type_label:"안전관리자", due_days:3 },
    { rule_id:"c-05", law_name:"산업안전보건법", law_article:"제36조", obligation_type:"INSPECT", category:"점검",
      obligation_summary:"위험성평가 실시", inspection_cycle:"수시",
      penalty_summary:"3,000만원 이하 과태료", submit_org_label:"자체보관", executor_type_label:"안전관리자", due_days:14 },
    { rule_id:"c-06", law_name:"산업안전보건법", law_article:"제57조", obligation_type:"REPORT", category:"보고",
      obligation_summary:"산업재해 발생 보고", penalty_summary:"1,000만원 이하 과태료",
      submit_org_label:"고용노동부", executor_type_label:"사업주" },
    { rule_id:"c-07", law_name:"중대재해처벌법", law_article:"제4조", obligation_type:"ACTION", category:"조치",
      obligation_summary:"안전보건관리체계 구축 및 이행", inspection_cycle:"연 1회",
      penalty_summary:"징역 1년 또는 10억원 이하 벌금", submit_org_label:"자체보관", executor_type_label:"경영책임자", due_days:30 },
    { rule_id:"c-08", law_name:"건설기술진흥법", law_article:"제62조", obligation_type:"INSPECT", category:"점검",
      obligation_summary:"건설현장 정기안전점검", inspection_cycle:"월 1회",
      penalty_summary:"1,000만원 이하 과태료", submit_org_label:"국토교통부", executor_type_label:"안전관리자" },
    { rule_id:"c-09", law_name:"건설기술진흥법", law_article:"제48조", obligation_type:"REPORT", category:"보고",
      obligation_summary:"안전관리계획서 제출", penalty_summary:"1,000만원 이하 과태료",
      submit_org_label:"발주처", executor_type_label:"현장소장" },
    { rule_id:"c-10", law_name:"소방시설법", law_article:"제26조", obligation_type:"APPOINT", category:"선임",
      obligation_summary:"소방안전관리자 선임", penalty_summary:"200만원 이하 과태료",
      submit_org_label:"소방청", executor_type_label:"사업주" },
    { rule_id:"c-11", law_name:"소방시설법", law_article:"제25조", obligation_type:"INSPECT", category:"점검",
      obligation_summary:"소방시설 자체점검", inspection_cycle:"6개월마다",
      penalty_summary:"1,500만원 이하 과태료", submit_org_label:"소방청", executor_type_label:"소방안전관리자" },
    { rule_id:"c-12", law_name:"전기사업법", law_article:"제63조", obligation_type:"INSPECT", category:"점검",
      obligation_summary:"전기설비 정기검사", inspection_cycle:"3년마다",
      penalty_summary:"300만원 이하 과태료", submit_org_label:"한국전기안전공사", executor_type_label:"전기안전관리자" },
    { rule_id:"c-13", law_name:"화학물질관리법", law_article:"제33조", obligation_type:"ACTION", category:"조치",
      obligation_summary:"화학물질 취급자 교육", inspection_cycle:"연 2회",
      penalty_summary:"5,000만원 이하 과태료", submit_org_label:"환경부", executor_type_label:"안전관리자" },
    { rule_id:"c-14", law_name:"위험물안전관리법", law_article:"제18조", obligation_type:"INSPECT", category:"점검",
      obligation_summary:"위험물 정기점검", inspection_cycle:"연 1회",
      penalty_summary:"300만원 이하 과태료", submit_org_label:"소방청", executor_type_label:"해당 자격자" },
    { rule_id:"c-15", law_name:"화재예방법", law_article:"제21조", obligation_type:"NOTIFY", category:"신고",
      obligation_summary:"화재 발생 신고", penalty_summary:"", submit_org_label:"119", executor_type_label:"발견자" }
  ],
  law_badges: ["산업안전보건법","중대재해처벌법","건설기술진흥법","건설산업기본법","전기사업법","소방시설법","화학물질관리법","위험물안전관리법","고압가스안전관리법","화재예방법","근로기준법","건설폐기물법","석면안전관리법","환경영향평가법"],
  key_obligations: [
    { type:"APPOINT", title:"안전보건관리책임자 선임", law:"산업안전보건법", law_article:"제15조", penalty:"5억원 이하 벌금", obligation_summary:"안전보건관리책임자 선임" },
    { type:"APPOINT", title:"안전관리자 선임", law:"산업안전보건법", law_article:"제17조", penalty:"500만원 이하 과태료", obligation_summary:"안전관리자 선임" },
    { type:"ACTION", title:"안전보건관리체계 구축", law:"중대재해처벌법", law_article:"제4조", penalty:"징역 1년 또는 10억원 이하 벌금", obligation_summary:"안전보건관리체계 구축" },
    { type:"INSPECT", title:"위험성평가 실시", law:"산업안전보건법", law_article:"제36조", penalty:"3,000만원 이하 과태료", obligation_summary:"위험성평가 실시" },
    { type:"ACTION", title:"특별안전보건교육", law:"산업안전보건법", law_article:"제29조", penalty:"500만원 이하 과태료", obligation_summary:"고소작업 특별교육" }
  ],
  inspection_schedule: {
    periodic: [
      { obligation_summary:"건설현장 정기안전점검", inspection_cycle:"monthly", executor_type_label:"안전관리자" },
      { obligation_summary:"소방시설 자체점검", inspection_cycle:"6month", executor_type_label:"소방안전관리자" },
      { obligation_summary:"전기설비 정기검사", inspection_cycle:"yearly", executor_type_label:"전기안전관리자" },
      { obligation_summary:"위험물 정기점검", inspection_cycle:"yearly", executor_type_label:"해당 자격자" },
      { obligation_summary:"위험성평가 갱신", inspection_cycle:"yearly", executor_type_label:"안전관리자" }
    ],
    before_work: [
      { obligation_summary:"특별안전보건교육 (고소작업)", executor_type_label:"안전관리자" },
      { obligation_summary:"작업 전 위험성평가", executor_type_label:"관리감독자" }
    ]
  },
  law_groups: [
    { law_name:"산업안전보건법", count:6, rules:[] },
    { law_name:"건설기술진흥법", count:2, rules:[] },
    { law_name:"소방시설법", count:2, rules:[] },
    { law_name:"중대재해처벌법", count:1, rules:[] },
    { law_name:"전기사업법", count:1, rules:[] },
    { law_name:"화학물질관리법", count:1, rules:[] },
    { law_name:"위험물안전관리법", count:1, rules:[] },
    { law_name:"화재예방법", count:1, rules:[] }
  ],
  input_data: {
    company_name:"한국건설산업(주) 강남 현장", business_no:"123-45-67890",
    ceo_name:"홍길동", address:"서울특별시 강남구 삼성동 123-4",
    worker_count:150, floor_area:""
  },
  recommended_plan: { name:"건설 STANDARD", price:"월 145,000원~" },
  pdf_url: "#"
};
```

### 제조업 / 시설관리업

위 건설업과 동일한 JSON 구조. 아래 값 변경:

**제조업:** sector=INDUSTRY, company_name="한국정밀제조(주) 안산 제2공장", risk_level=HIGH, applicable_count=203, worker_count=300. rules_table에 작업환경측정(§125), 특수건강검진(§130), MSDS(§110), 유해위험방지계획서(§42), 화관법 취급시설(§24), 진폐예방법(§9) 포함. recommended_plan: 산업 BUSINESS 149,000원~.

**시설관리업:** sector=BUILDING, company_name="서울타워빌딩 관리사무소", risk_level=MEDIUM, applicable_count=118, worker_count=50. rules_table에 건축물관리법 정기점검(§12), 소방 선임/점검, 승강기 선임/검사, 전기 선임/점검, 도시가스 검사, 화재예방 점검. recommended_plan: 건물 소형 59,000원~.

**Cursor는 각 업종의 rules_table을 15건 이상, 실제 법령 기준으로 완성한다.**

---

## 3단계. 정적 HTML 생성

### 기준: `paid-diagnosis-result.html` 전체 복사

생성 파일:
- `nexas/sample-construction.html`
- `nexas/sample-manufacturing.html`
- `nexas/sample-facility.html`

### 수정 사항

#### 3-1. init() 함수 교체

```javascript
// 변경 전
async function init(){
  const params=new URLSearchParams(location.search);
  const token=params.get("token")||params.get("public_token")||"";
  if(!token){alert("...");return}
  const res=await fetch(`${API}/diagnosis/paid-result/...`);
  ...
  const d=(await res.json()).data||{};
  // 이하 렌더링

// 변경 후
async function init(){
  const d = SAMPLE_DATA;
  // 이하 렌더링 (fetch 부분만 제거, 나머지 그대로)
```

#### 3-2. PDF 버튼 — 제거하지 않음 (비활성화)

```javascript
document.getElementById("pdfTopBtn").href = "#";
document.getElementById("pdfTopBtn").onclick = function(e){
  e.preventDefault();
  // 간단한 안내 또는 무반응
};
document.getElementById("pdfTopBtn").textContent = "PDF 다운로드 (예시)";
// pdfBottomBtn도 동일 처리
```

#### 3-3. 법령 원문 보기 — API 호출 제거

```javascript
async function loadLawDetail(btn){
  const box = document.getElementById(btn.dataset.targetId);
  if(!box) return;
  box.innerHTML = '<div class="small text-muted">실제 진단 시 법령 원문이 표시됩니다.</div>';
  btn.dataset.loaded = "1";
}
```

#### 3-4. 상단 배지 추가

`<body>` 직후, `.topbar` 직전:
```html
<div style="background:#1e40af;color:#fff;text-align:center;padding:10px 16px;font-size:.82rem;font-weight:700;letter-spacing:.05em;">
  📊 예시 결과 화면 — 실제 진단 결과가 아닙니다 · Sample Report
</div>
```

#### 3-5. SaaS CTA에 무료진단 링크 추가

기존 "14일 무료 체험" 유지. 추가로:
```html
<div style="text-align:center;margin-top:16px;">
  <a href="free-diagnosis.html" class="btn btn-primary btn-lg"
     style="font-weight:800;padding:14px 32px;border-radius:10px;">
    우리 사업장 무료 법령진단 시작 →
  </a>
</div>
```

#### 3-6. title 변경

- construction: `법령진단 결과 예시 (건설업) | TAI Safe`
- manufacturing: `법령진단 결과 예시 (제조업) | TAI Safe`
- facility: `법령진단 결과 예시 (시설관리업) | TAI Safe`

#### 3-7. API 상수

```javascript
const API=""; // 사용하지 않음
```

#### 3-8. Google Analytics 유지 (고객 행동 추적 필요)

---

## 4단계. 마케팅 사이트 연결

`nexas/free-diagnosis.html` 또는 `nexas/for-safety-manager.html`에 추가:

```html
<div style="margin-top:24px;text-align:center;border-top:1px solid #e2e8f0;padding-top:20px;">
  <p style="font-size:.88rem;color:#64748b;margin-bottom:12px;font-weight:600;">
    진단 결과가 궁금하세요? 예시를 확인해보세요.
  </p>
  <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
    <a href="sample-construction.html" style="padding:8px 16px;border-radius:8px;border:1.5px solid #1A5FD4;color:#1A5FD4;font-size:.82rem;font-weight:700;text-decoration:none;">건설업 예시</a>
    <a href="sample-manufacturing.html" style="padding:8px 16px;border-radius:8px;border:1.5px solid #1A5FD4;color:#1A5FD4;font-size:.82rem;font-weight:700;text-decoration:none;">제조업 예시</a>
    <a href="sample-facility.html" style="padding:8px 16px;border-radius:8px;border:1.5px solid #1A5FD4;color:#1A5FD4;font-size:.82rem;font-weight:700;text-decoration:none;">시설관리업 예시</a>
  </div>
</div>
```

---

## 5단계. 최종 검수 체크리스트

- [ ] 3개 샘플 정상 렌더링 (PC / 모바일 / 태블릿)
- [ ] "예시 결과 화면" 배지 표시
- [ ] 위험도 게이지 (HIGH/MEDIUM 색상)
- [ ] 요약 KPI 4칸 + 도넛 차트
- [ ] 법령 bar chart
- [ ] 법령 상세 테이블
- [ ] 의무유형별 카드 (선임/점검/조치/보고/신고)
- [ ] 과태료 bar chart + 총액
- [ ] 점검 타임라인 (매월/분기/반기/연간/수시)
- [ ] 체크리스트 (출력용)
- [ ] PDF 버튼 표시 (비활성)
- [ ] SaaS CTA + "무료 법령진단 시작" 링크
- [ ] JS 콘솔 에러 없음
- [ ] Network 탭: API 호출 0건
- [ ] 마케팅 사이트 예시 링크 정상

---

## 주의사항

- taieng 레포 `main` 직접 커밋 (Cloudflare Pages 자동배포)
- `paid-diagnosis-result.html` 원본은 절대 수정하지 않음 → 복사만
- 목업 데이터의 법령명·조문·과태료는 실제 법령 기준 (허위 법률 금지)
- "목업" 용어 금지 → "예시 결과 화면" 사용
- Excel 다운로드 기능이 현재 없으면 버튼도 없음 (있는 것만 유지)
