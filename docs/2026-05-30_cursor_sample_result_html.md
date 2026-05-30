# 법령진단 결과 페이지 점검 + 고객용 정적 샘플 HTML 생성 — Cursor 작업지시서

> 작성일: 2026-05-30
> 대상 레포: taiengineering/taieng (nexas/)
> 목적: 기존 결과 페이지를 복사하여 기능 없는 정적 HTML 샘플 3개 생성

---

## 기준 파일

`nexas/free-diagnosis-result.html` (39KB)

이 파일은 이미 MOCK_DATA 폴백이 있어서 token 없이도 독립 동작함.
이 파일을 복사하여 샘플 3개를 만든다.

---

## 생성할 파일

1. `nexas/sample-result-construction.html`
2. `nexas/sample-result-manufacturing.html`
3. `nexas/sample-result-facility.html`

---

## 작업 순서

### STEP 1: free-diagnosis-result.html 복사

각 샘플 파일은 `free-diagnosis-result.html`의 전체 복사본이다.
HTML 구조, CSS, 렌더링 로직을 그대로 유지한다.

### STEP 2: MOCK_DATA 교체

각 파일의 `const MOCK_DATA = { ... }` 블록을 아래 데이터로 교체한다.

#### 건설업 (sample-result-construction.html)

```javascript
const MOCK_DATA = {
  sector: 'CONSTRUCTION',
  risk_level: 'HIGH',
  applicable_count: 156,
  risk_reason: '적용 법령 14개, 긴급 항목 6건, 중대재해법 적용 대상',
  summary: {
    total: 156, appointment: 12, inspection: 38,
    action: 78, report: 18, notify: 10, form_linked: 89
  },
  law_badges: [
    '산업안전보건법','중대재해처벌법','건설기술진흥법','건설산업기본법',
    '전기사업법','소방시설법','화학물질관리법','위험물안전관리법',
    '고압가스안전관리법','화재예방법','근로기준법','건설폐기물법',
    '석면안전관리법','환경영향평가법'
  ],
  rules_table: [
    { law_name:'산업안전보건법', law_article:'제15조', obligation_type:'APPOINT',
      obligation_summary:'안전보건관리책임자 선임', inspection_cycle:'',
      penalty_summary:'5억원 이하 볌금', submit_org_label:'고용노동부',
      due_info:{urgency:'URGENT',due_days:3} },
    { law_name:'산업안전보건법', law_article:'제17조', obligation_type:'APPOINT',
      obligation_summary:'안전관리자 선임 (건설 120명 이상)', inspection_cycle:'',
      penalty_summary:'500만원 이하 과태료', submit_org_label:'고용노동부',
      due_info:{urgency:'URGENT',due_days:5} },
    { law_name:'산업안전보건법', law_article:'제29조', obligation_type:'ACTION',
      obligation_summary:'신규 채용 시 안전보건교육 실시 (8시간)', inspection_cycle:'채용 시',
      penalty_summary:'500만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:7} },
    { law_name:'산업안전보건법', law_article:'제29조', obligation_type:'ACTION',
      obligation_summary:'특별안전보건교육 (고소작업 16시간)', inspection_cycle:'작업 전',
      penalty_summary:'500만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:3} },
    { law_name:'산업안전보건법', law_article:'제36조', obligation_type:'INSPECT',
      obligation_summary:'위험성평가 실시', inspection_cycle:'수시',
      penalty_summary:'3,000만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:14} },
    { law_name:'산업안전보건법', law_article:'제57조', obligation_type:'REPORT',
      obligation_summary:'산업재해 발생 보고', inspection_cycle:'',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'고용노동부', due_info:{} },
    { law_name:'중대재해처벌법', law_article:'제4조', obligation_type:'ACTION',
      obligation_summary:'안전보건관리체계 구축 및 이행', inspection_cycle:'연 1회',
      penalty_summary:'징역 1년 또는 10억원 이하 볌금', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:30} },
    { law_name:'건설기술진흥법', law_article:'제62조', obligation_type:'INSPECT',
      obligation_summary:'건설현장 정기안전점검', inspection_cycle:'월 1회',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'국토교통부',
      due_info:{} },
    { law_name:'건설기술진흥법', law_article:'제48조', obligation_type:'REPORT',
      obligation_summary:'안전관리계획서 제출', inspection_cycle:'',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'발주처',
      due_info:{urgency:'NORMAL'} },
    { law_name:'전기사업법', law_article:'제63조', obligation_type:'INSPECT',
      obligation_summary:'전기설비 정기검사', inspection_cycle:'3년마다',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'한국전기안전공사', due_info:{} },
    { law_name:'소방시설법', law_article:'제25조', obligation_type:'INSPECT',
      obligation_summary:'소방시설 자체점검', inspection_cycle:'6개월마다',
      penalty_summary:'1,500만원 이하 과태료', submit_org_label:'소방청',
      due_info:{} },
    { law_name:'소방시설법', law_article:'제26조', obligation_type:'APPOINT',
      obligation_summary:'소방안전관리자 선임', inspection_cycle:'',
      penalty_summary:'200만원 이하 과태료', submit_org_label:'소방청',
      due_info:{} },
    { law_name:'화학물질관리법', law_article:'제33조', obligation_type:'ACTION',
      obligation_summary:'화학물질 취급자 교육', inspection_cycle:'연 2회',
      penalty_summary:'5,000만원 이하 과태료', submit_org_label:'환경부', due_info:{} },
    { law_name:'위험물안전관리법', law_article:'제18조', obligation_type:'INSPECT',
      obligation_summary:'위험물 정기점검', inspection_cycle:'연 1회',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'소방청', due_info:{} },
    { law_name:'화재예방법', law_article:'제21조', obligation_type:'NOTIFY',
      obligation_summary:'화재 발생 신고', inspection_cycle:'',
      penalty_summary:'', submit_org_label:'119', due_info:{} }
  ]
};
```

#### 제조업 (sample-result-manufacturing.html)

```javascript
const MOCK_DATA = {
  sector: 'INDUSTRY',
  risk_level: 'HIGH',
  applicable_count: 203,
  risk_reason: '적용 법령 11개, 긴급 항목 5건, 유해물질 취급 사업장',
  summary: {
    total: 203, appointment: 10, inspection: 42,
    action: 112, report: 22, notify: 17, form_linked: 128
  },
  law_badges: [
    '산업안전보건법','중대재해처벌법','화학물질관리법','위험물안전관리법',
    '전기사업법','소방시설법','고압가스안전관리법','근로기준법',
    '산업재해보상보험법','환경영향평가법','진폐예방법'
  ],
  rules_table: [
    { law_name:'산업안전보건법', law_article:'제15조', obligation_type:'APPOINT',
      obligation_summary:'안전보건관리책임자 선임', inspection_cycle:'',
      penalty_summary:'5억원 이하 볌금', submit_org_label:'고용노동부',
      due_info:{urgency:'URGENT',due_days:3} },
    { law_name:'산업안전보건법', law_article:'제125조', obligation_type:'INSPECT',
      obligation_summary:'작업환경측정 실시', inspection_cycle:'반기 1회',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:10} },
    { law_name:'산업안전보건법', law_article:'제130조', obligation_type:'INSPECT',
      obligation_summary:'유해인자 노출 근로자 특수건강검진', inspection_cycle:'연 1회',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:8} },
    { law_name:'산업안전보건법', law_article:'제29조', obligation_type:'ACTION',
      obligation_summary:'근로자 정기 안전보건교육 (6시간/분기)', inspection_cycle:'분기마다',
      penalty_summary:'500만원 이하 과태료', submit_org_label:'자체보관', due_info:{} },
    { law_name:'산업안전보건법', law_article:'제36조', obligation_type:'INSPECT',
      obligation_summary:'위험성평가 실시', inspection_cycle:'수시',
      penalty_summary:'3,000만원 이하 과태료', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:14} },
    { law_name:'중대재해처벌법', law_article:'제4조', obligation_type:'ACTION',
      obligation_summary:'안전보건관리체계 구축 및 이행', inspection_cycle:'연 1회',
      penalty_summary:'징역 1년 또는 10억원 이하 볌금', submit_org_label:'자체보관',
      due_info:{urgency:'URGENT',due_days:30} },
    { law_name:'화학물질관리법', law_article:'제33조', obligation_type:'ACTION',
      obligation_summary:'화학물질 취급자 교육', inspection_cycle:'연 2회',
      penalty_summary:'5,000만원 이하 과태료', submit_org_label:'환경부', due_info:{} },
    { law_name:'화학물질관리법', law_article:'제24조', obligation_type:'REPORT',
      obligation_summary:'유해화학물질 취급시설 설치확인', inspection_cycle:'',
      penalty_summary:'3,000만원 이하 과태료', submit_org_label:'화학물질안전원', due_info:{} },
    { law_name:'위험물안전관리법', law_article:'제18조', obligation_type:'INSPECT',
      obligation_summary:'위험물 정기점검', inspection_cycle:'연 1회',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'소방청', due_info:{} },
    { law_name:'전기사업법', law_article:'제22조', obligation_type:'APPOINT',
      obligation_summary:'전기안전관리자 선임', inspection_cycle:'',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'한국전기안전공사', due_info:{} },
    { law_name:'소방시설법', law_article:'제25조', obligation_type:'INSPECT',
      obligation_summary:'소방시설 자체점검', inspection_cycle:'6개월마다',
      penalty_summary:'1,500만원 이하 과태료', submit_org_label:'소방청', due_info:{} },
    { law_name:'진폐예방법', law_article:'제9조', obligation_type:'INSPECT',
      obligation_summary:'진동 작업장 정기측정', inspection_cycle:'연 1회',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'자체보관', due_info:{} }
  ]
};
```

#### 시설관리업 (sample-result-facility.html)

```javascript
const MOCK_DATA = {
  sector: 'BUILDING',
  risk_level: 'MEDIUM',
  applicable_count: 118,
  risk_reason: '적용 법령 10개, 긴급 항목 3건, 승강기·전기·소방 복합 관리',
  summary: {
    total: 118, appointment: 6, inspection: 28,
    action: 58, report: 14, notify: 12, form_linked: 72
  },
  law_badges: [
    '건축물관리법','소방시설법','승강기안전관리법','전기안전관리법',
    '산업안전보건법','도시가스사업법','고압가스안전관리법',
    '화재예방법','근로기준법','중대재해처벌법'
  ],
  rules_table: [
    { law_name:'건축물관리법', law_article:'제12조', obligation_type:'INSPECT',
      obligation_summary:'건축물 정기점검', inspection_cycle:'2년마다',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'국토교통부',
      due_info:{urgency:'URGENT',due_days:14} },
    { law_name:'소방시설법', law_article:'제26조', obligation_type:'APPOINT',
      obligation_summary:'소방안전관리자 선임', inspection_cycle:'',
      penalty_summary:'200만원 이하 과태료', submit_org_label:'소방청',
      due_info:{urgency:'URGENT',due_days:7} },
    { law_name:'소방시설법', law_article:'제25조', obligation_type:'INSPECT',
      obligation_summary:'소방시설 종합정밀점검', inspection_cycle:'연 1회',
      penalty_summary:'1,500만원 이하 과태료', submit_org_label:'소방청', due_info:{} },
    { law_name:'승강기안전관리법', law_article:'제32조', obligation_type:'APPOINT',
      obligation_summary:'승강기 안전관리자 선임', inspection_cycle:'',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'한국승강기안전공단', due_info:{} },
    { law_name:'승강기안전관리법', law_article:'제28조', obligation_type:'INSPECT',
      obligation_summary:'승강기 정기검사', inspection_cycle:'1년마다',
      penalty_summary:'1,000만원 이하 과태료', submit_org_label:'한국승강기안전공단', due_info:{} },
    { law_name:'전기안전관리법', law_article:'제22조', obligation_type:'APPOINT',
      obligation_summary:'전기안전관리자 선임', inspection_cycle:'',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'한국전기안전공사',
      due_info:{urgency:'URGENT',due_days:10} },
    { law_name:'전기안전관리법', law_article:'제23조', obligation_type:'INSPECT',
      obligation_summary:'전기설비 정기점검', inspection_cycle:'3년마다',
      penalty_summary:'300만원 이하 과태료', submit_org_label:'한국전기안전공사', due_info:{} },
    { law_name:'도시가스사업법', law_article:'제17조', obligation_type:'INSPECT',
      obligation_summary:'가스시설 정기검사', inspection_cycle:'2년마다',
      penalty_summary:'200만원 이하 과태료', submit_org_label:'한국가스안전공사', due_info:{} },
    { law_name:'산업안전보건법', law_article:'제29조', obligation_type:'ACTION',
      obligation_summary:'근로자 정기 안전보건교육', inspection_cycle:'분기마다',
      penalty_summary:'500만원 이하 과태료', submit_org_label:'자체보관', due_info:{} },
    { law_name:'화재예방법', law_article:'제17조', obligation_type:'INSPECT',
      obligation_summary:'화재예방 안전점검', inspection_cycle:'6개월마다',
      penalty_summary:'200만원 이하 과태료', submit_org_label:'소방청', due_info:{} },
    { law_name:'중대재해처벌법', law_article:'제4조', obligation_type:'ACTION',
      obligation_summary:'안전보건관리체계 구축', inspection_cycle:'연 1회',
      penalty_summary:'징역 1년 또는 10억원 이하 볌금', submit_org_label:'자체보관', due_info:{} }
  ]
};
```

### STEP 3: 기능 제거 (각 샘플 HTML에서)

#### 3-1. `init()` IIFE 교체

변경 전:
```javascript
(function init() {
  const params = new URLSearchParams(location.search);
  const token  = params.get('token');
  if (token) {
    fetchResult(token);
  } else {
    render(MOCK_DATA);
  }
})();
```

변경 후:
```javascript
// 샘플 페이지: API 호출 없이 MOCK_DATA로만 렌더링
(function init() {
  render(MOCK_DATA);
})();
```

#### 3-2. `fetchResult()` 함수 삭제

전체 삭제:
```javascript
async function fetchResult(token) {
  ...
}
```

#### 3-3. `downloadPdf()` 제거

변경 전:
```javascript
function downloadPdf() {
  alert('...');
}
```

변경 후: 함수 삭제

#### 3-4. PDF 버튼 제거

아래 HTML 블록 전체 삭제:
```html
<div class="pdf-cta">...전체...</div>
```

#### 3-5. `revealPrice()`, `startPaid()` 함수 삭제

두 함수 전체 삭제.

#### 3-6. 유료 CTA 교체

변경 전:
```html
<div class="paid-cta">...전체...</div>
```

변경 후:
```html
<div class="paid-cta" style="border-color:var(--blue);">
  <h3>우리 사업장도 진단해보세요</h3>
  <div class="necessity">
    이 화면은 <strong>예시 결과</strong>입니다.<br>
    실제 사업장 정보를 입력하면 귀 사업장에 적용되는 법적 의무를 확인할 수 있습니다.
  </div>
  <a class="btn-paid-start" href="free-diagnosis.html" style="display:block;text-decoration:none;text-align:center;">
    우리 사업장 무료 법령진단 시작 →
  </a>
</div>
```

#### 3-7. 상단 "예시 결과 화면" 배지 추가

`<body>` 직후, `.risk-header` 직전에 추가:

```html
<div style="background:#1e40af;color:#fff;text-align:center;padding:10px 16px;font-size:.82rem;font-weight:700;letter-spacing:.05em;">
  📊 예시 결과 화면 — 실제 진단 결과가 아닙니다
</div>
```

#### 3-8. `renderPaidCta()` 함수 제거 + `render()` 함수에서 `renderPaidCta(d)` 호출 제거

#### 3-9. Google Analytics 제거 (gtag)

`<head>` 내 Google Tag 스크립트 전체 삭제:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JRP9SHHC5M"></script>
<script>window.dataLayer...gtag('config'...);</script>
```

#### 3-10. `<title>` 변경

각 파일별:
- construction: `<title>법령진단 결과 예시 (건설업) | TAI 엔지니어링</title>`
- manufacturing: `<title>법령진단 결과 예시 (제조업) | TAI 엔지니어링</title>`
- facility: `<title>법령진단 결과 예시 (시설관리업) | TAI 엔지니어링</title>`

---

## 작업 5: 마케팅 사이트 연결

`nexas/free-diagnosis.html` 또는 `nexas/for-safety-manager.html`에 아래 버튼 추가.

기존 CTA 영역 근처 (예: 무료진단 버튼 아래)에:

```html
<div style="margin-top:16px;text-align:center;">
  <p style="font-size:.85rem;color:#64748b;margin-bottom:10px;">진단 결과가 궁금하세요? 예시를 확인해보세요.</p>
  <a href="sample-result-construction.html" style="color:#1A5FD4;font-weight:700;font-size:.82rem;margin-right:16px;">건설업 예시</a>
  <a href="sample-result-manufacturing.html" style="color:#1A5FD4;font-weight:700;font-size:.82rem;margin-right:16px;">제조업 예시</a>
  <a href="sample-result-facility.html" style="color:#1A5FD4;font-weight:700;font-size:.82rem;">시설관리업 예시</a>
</div>
```

---

## 주의사항

- taieng 레포 `main` 직접 커밋 (Cloudflare Pages 자동배포)
- SaaS 전환 섹션 (`saas-section`):는 그대로 유지 (보여줘도 됨)
- 법적 면책 문구 그대로 유지
- alert() 호출 전부 제거
- 샘플 페이지에서 사용자가 클릭해도 실행되는 기능이 없어야 함
- "목업" 대신 "예시 결과 화면" 톤 사용

## 검증 체크리스트

- [ ] 3개 샘플 HTML 정상 렌더링 (PC)
- [ ] 3개 샘플 HTML 정상 렌더링 (모바일)
- [ ] "예시 결과 화면" 배지 표시
- [ ] PDF/Excel 버튼 없음
- [ ] alert() 없음
- [ ] API 호출 없음
- [ ] CTA → "우리 사업장 무료 법령진단 시작" 링크 정상
- [ ] SaaS 전환 섹션 유지
- [ ] 법적 면책 문구 유지
- [ ] 마케팅 사이트에 예시 보기 링크 추가
