# 법령진단 결과 고객용 샘플 HTML 생성

## 작업 내용

paid-diagnosis-result.html을 복사하여 정적 HTML 3개를 만든다.
API 호출을 제거하고 SAMPLE_DATA로 교체한다.
기존 파일은 수정하지 않는다.

## 생성 파일

- `nexas/sample-construction.html`
- `nexas/sample-manufacturing.html`
- `nexas/sample-facility.html`

## 구현 방식

```javascript
// 변경 전 (paid-diagnosis-result.html의 init)
const res = await fetch(`${API}/diagnosis/paid-result/${token}`);
const d = (await res.json()).data;

// 변경 후 (sample-*.html)
const d = SAMPLE_DATA;
```

나머지 렌더링 로직은 그대로 둔다.

## SAMPLE_DATA

각 파일 상단에 `const SAMPLE_DATA = { ... };` 삽입.
구조는 `/diagnosis/paid-result/{token}` API 응답의 `data` 필드와 동일.

### 건설업

```json
{
  "sector": "CONSTRUCTION",
  "sector_label": "건설",
  "company_name": "한국건설산업(주) 강남 현장",
  "risk_level": "HIGH",
  "risk_reason": "적용 법령 14개, 긴급 항목 6건, 중대재해법 적용 대상",
  "applicable_count": 156,
  "engine_version": "v3.0-runtime-compiler",
  "is_free": false,
  "tier_code": "CONSTRUCTION",
  "summary": {
    "total": 156, "inspection": 38, "appointment": 12,
    "action": 78, "report": 28, "form_linked": 89,
    "law_count": 14, "worker_count": 150, "csia_applicable": true
  },
  "obligation_counts": { "선임":12, "점검":38, "조치":78, "보고":18, "신고":10 },
  "warnings": ["중대재해처벌법 적용 대상 사업장입니다."],
  "law_badges": ["산업안전보건법","중대재해처벌법","건설기술진흥법","건설산업기본법","전기사업법","소방시설법","화학물질관리법","위험물안전관리법","고압가스안전관리법","화재예방법","근로기준법","건설폐기물법","석면안전관리법","환경영향평가법"],
  "rules_table": [
    {"rule_id":"c-01","law_name":"산업안전보건법","law_article":"제15조","obligation_type":"APPOINT","category":"선임","obligation_summary":"안전보건관리책임자 선임","penalty_summary":"5억원 이하 벌금","submit_org_label":"고용노동부","executor_type_label":"사업주","due_days":3},
    {"rule_id":"c-02","law_name":"산업안전보건법","law_article":"제17조","obligation_type":"APPOINT","category":"선임","obligation_summary":"안전관리자 선임 (건설 120명 이상)","penalty_summary":"500만원 이하 과태료","submit_org_label":"고용노동부","executor_type_label":"사업주","due_days":5},
    {"rule_id":"c-03","law_name":"산업안전보건법","law_article":"제29조","obligation_type":"ACTION","category":"조치","obligation_summary":"신규 채용 시 안전보건교육 (8시간)","inspection_cycle":"채용 시","penalty_summary":"500만원 이하 과태료","submit_org_label":"자체보관","executor_type_label":"안전관리자","due_days":7},
    {"rule_id":"c-04","law_name":"산업안전보건법","law_article":"제29조","obligation_type":"ACTION","category":"조치","obligation_summary":"특별안전보건교육 (고소작업 16시간)","inspection_cycle":"작업 전","penalty_summary":"500만원 이하 과태료","submit_org_label":"자체보관","executor_type_label":"안전관리자","due_days":3},
    {"rule_id":"c-05","law_name":"산업안전보건법","law_article":"제36조","obligation_type":"INSPECT","category":"점검","obligation_summary":"위험성평가 실시","inspection_cycle":"수시","penalty_summary":"3,000만원 이하 과태료","submit_org_label":"자체보관","executor_type_label":"안전관리자","due_days":14},
    {"rule_id":"c-06","law_name":"산업안전보건법","law_article":"제57조","obligation_type":"REPORT","category":"보고","obligation_summary":"산업재해 발생 보고","penalty_summary":"1,000만원 이하 과태료","submit_org_label":"고용노동부","executor_type_label":"사업주"},
    {"rule_id":"c-07","law_name":"중대재해처벌법","law_article":"제4조","obligation_type":"ACTION","category":"조치","obligation_summary":"안전보건관리체계 구축 및 이행","inspection_cycle":"연 1회","penalty_summary":"징역 1년 또는 10억원 이하 벌금","submit_org_label":"자체보관","executor_type_label":"경영책임자","due_days":30},
    {"rule_id":"c-08","law_name":"건설기술진흥법","law_article":"제62조","obligation_type":"INSPECT","category":"점검","obligation_summary":"건설현장 정기안전점검","inspection_cycle":"월 1회","penalty_summary":"1,000만원 이하 과태료","submit_org_label":"국토교통부","executor_type_label":"안전관리자"},
    {"rule_id":"c-09","law_name":"건설기술진흥법","law_article":"제48조","obligation_type":"REPORT","category":"보고","obligation_summary":"안전관리계획서 제출","penalty_summary":"1,000만원 이하 과태료","submit_org_label":"발주처","executor_type_label":"현장소장"},
    {"rule_id":"c-10","law_name":"소방시설법","law_article":"제26조","obligation_type":"APPOINT","category":"선임","obligation_summary":"소방안전관리자 선임","penalty_summary":"200만원 이하 과태료","submit_org_label":"소방청","executor_type_label":"사업주"},
    {"rule_id":"c-11","law_name":"소방시설법","law_article":"제25조","obligation_type":"INSPECT","category":"점검","obligation_summary":"소방시설 자체점검","inspection_cycle":"6개월마다","penalty_summary":"1,500만원 이하 과태료","submit_org_label":"소방청","executor_type_label":"소방안전관리자"},
    {"rule_id":"c-12","law_name":"전기사업법","law_article":"제63조","obligation_type":"INSPECT","category":"점검","obligation_summary":"전기설비 정기검사","inspection_cycle":"3년마다","penalty_summary":"300만원 이하 과태료","submit_org_label":"한국전기안전공사","executor_type_label":"전기안전관리자"},
    {"rule_id":"c-13","law_name":"화학물질관리법","law_article":"제33조","obligation_type":"ACTION","category":"조치","obligation_summary":"화학물질 취급자 교육","inspection_cycle":"연 2회","penalty_summary":"5,000만원 이하 과태료","submit_org_label":"환경부","executor_type_label":"안전관리자"},
    {"rule_id":"c-14","law_name":"위험물안전관리법","law_article":"제18조","obligation_type":"INSPECT","category":"점검","obligation_summary":"위험물 정기점검","inspection_cycle":"연 1회","penalty_summary":"300만원 이하 과태료","submit_org_label":"소방청","executor_type_label":"해당 자격자"},
    {"rule_id":"c-15","law_name":"화재예방법","law_article":"제21조","obligation_type":"NOTIFY","category":"신고","obligation_summary":"화재 발생 신고","penalty_summary":"","submit_org_label":"119","executor_type_label":"발견자"}
  ],
  "key_obligations": [
    {"type":"APPOINT","title":"안전보건관리책임자 선임","law":"산업안전보건법","law_article":"제15조","penalty":"5억원 이하 벌금"},
    {"type":"ACTION","title":"안전보건관리체계 구축","law":"중대재해처벌법","law_article":"제4조","penalty":"징역 1년 또는 10억원 이하 벌금"},
    {"type":"INSPECT","title":"위험성평가 실시","law":"산업안전보건법","law_article":"제36조","penalty":"3,000만원 이하 과태료"},
    {"type":"ACTION","title":"특별안전보건교육","law":"산업안전보건법","law_article":"제29조","penalty":"500만원 이하 과태료"}
  ],
  "inspection_schedule": {
    "periodic":[
      {"obligation_summary":"건설현장 정기안전점검","inspection_cycle":"monthly","executor_type_label":"안전관리자"},
      {"obligation_summary":"소방시설 자체점검","inspection_cycle":"6month","executor_type_label":"소방안전관리자"},
      {"obligation_summary":"전기설비 정기검사","inspection_cycle":"yearly","executor_type_label":"전기안전관리자"},
      {"obligation_summary":"위험물 정기점검","inspection_cycle":"yearly","executor_type_label":"해당 자격자"}
    ]
  },
  "law_groups": [
    {"law_name":"산업안전보건법","count":6},
    {"law_name":"건설기술진흥법","count":2},
    {"law_name":"소방시설법","count":2},
    {"law_name":"중대재해처벌법","count":1},
    {"law_name":"전기사업법","count":1},
    {"law_name":"화학물질관리법","count":1},
    {"law_name":"위험물안전관리법","count":1},
    {"law_name":"화재예방법","count":1}
  ],
  "input_data": {
    "company_name":"한국건설산업(주) 강남 현장","business_no":"123-45-67890",
    "ceo_name":"홍길동","address":"서울특별시 강남구 삼성동 123-4",
    "worker_count":150,"floor_area":""
  },
  "recommended_plan":{"name":"건설 STANDARD","price":"월 145,000원~"},
  "pdf_url":"#"
}
```

### 제조업

sector=INDUSTRY, company_name="한국정밀제조(주) 안산 제2공장", risk_level=HIGH, applicable_count=203, worker_count=300.
rules_table에 작업환경측정(§125), 특수건강검진(§130), 유해위험방지계획서(§42), 화관법 취급시설(§24), 진폐예방법(§9) 포함. 건설업 JSON과 동일 구조로 작성.
recommended_plan: 산업 BUSINESS 149,000원~.

### 시설관리업

sector=BUILDING, company_name="서울타워빌딩 관리사무소", risk_level=MEDIUM, applicable_count=118, worker_count=50.
rules_table에 건축물관리법(§12), 승강기안전관리법(§28,§32), 전기안전관리법(§22,§23), 도시가스사업법(§17). 건설업 JSON과 동일 구조로 작성.
recommended_plan: 건물 소형 59,000원~.

## 추가 처리

- 상단에 "예시 결과 화면" 배지 1줄 추가
- PDF/Excel 버튼은 그대로 두되 href="#"으로 비활성화
- 법령 원문 보기(loadLawDetail)는 안내 문구로 대체
- API 상수 `const API=""` 처리

## 금지사항

- 기존 파일 수정 금지
- 정책 변경 금지
- 새 기능 개발 금지
