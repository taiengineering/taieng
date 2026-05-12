# 외부 API 모니터 개편 작업지시서
## 작성일: 2026-03-31 | 담당: 프론트엔드 창

---

## 배경

현재 `api-monitor-external.html`은 두 가지 문제가 있습니다.

1. **API 미구현** → fallback 5개(자동신고용)만 표시됨. 현재 사용 중인 API(JUSO, 건축물대장, 법제처, KCSC)가 보이지 않음
2. **카드형 UI** → 정보가 많아 한눈에 파악 어려움. 리스트(테이블)형으로 변경 요청

---

## 현재 DB 상태 (report_api_registry — 9개)

### 그룹1: 현재 사용 중 (api_purpose = 'USED') — 4개
| system_name | env_var_name | api_key_expires | apply_status |
|---|---|---|---|
| 도로명주소 API (JUSO) | JUSO_API_KEY | - | APPROVED |
| 건축물대장 API | BUILDING_API_KEY | - | APPROVED |
| 법제처 법령정보 API | - | - | APPROVED |
| KCSC 건설공정표준코드 API | KCSC_API_KEY | 2027-03-29 | APPROVED |

### 그룹2: 자동신고 연동 대상 (api_purpose = 'REPORT') — 5개
| system_name | apply_status |
|---|---|
| 고용24 OPEN-API | PENDING |
| 화관법 민원24 | PENDING |
| 올바로시스템 | PENDING |
| 한국전기안전공사 전기안전 API | PENDING |
| 세움터 | PENDING |

---

## 작업 내용

### 1. 데이터 로드 방식 변경

기존 코드는 API 실패 시 5개 하드코딩 fallback만 사용합니다.  
**변경 요구사항**: API 실패 여부와 관계없이 아래 9개를 **항상 fallback으로 포함**합니다.

```javascript
// ── fallback 데이터 (API 미구현 상태에서도 9개 전부 표시) ──
var FALLBACK_APIS = [
  // 사용 중
  { id:'used-1', system_name:'도로명주소 API (JUSO)',         operator:'행정안전부',                 api_purpose:'USED',   official_api:'Y',              apply_status:'APPROVED', api_key_issued:true,  env_var_name:'JUSO_API_KEY',    api_key_expires:null,         api_apply_url:'https://business.juso.go.kr/addrlink/openApi/apiReqst.do',  notes:'주소 검색·자동완성. Railway 환경변수 JUSO_API_KEY로 운영 중.' },
  { id:'used-2', system_name:'건축물대장 API',                operator:'국토교통부 / 세움터',          api_purpose:'USED',   official_api:'Y',              apply_status:'APPROVED', api_key_issued:true,  env_var_name:'BUILDING_API_KEY',api_key_expires:null,         api_apply_url:'https://www.data.go.kr/data/15044713/openapi.do',           notes:'시설 등록 시 건물 기본정보·용도·면적 자동 조회.' },
  { id:'used-3', system_name:'법제처 법령정보 API',            operator:'법제처 / data.go.kr',         api_purpose:'USED',   official_api:'Y',              apply_status:'APPROVED', api_key_issued:true,  env_var_name:null,              api_key_expires:null,         api_apply_url:'https://www.data.go.kr/data/15000115/openapi.do',           notes:'법령 자동 수집. data.go.kr serviceKey 방식(IP 제한 없음).' },
  { id:'used-4', system_name:'KCSC 건설공정표준코드 API',      operator:'한국건설기술연구원 (KCSC)',    api_purpose:'USED',   official_api:'Y',              apply_status:'APPROVED', api_key_issued:true,  env_var_name:'KCSC_API_KEY',    api_key_expires:'2027-03-29', api_apply_url:'https://kcsc.re.kr/OpenApi/CodeList',                       notes:'건설공정 표준코드(KCS). 건축 75·토목 50·공통 36=161개 완료. 키 만료: 2027-03-29.' },
  // 자동신고용
  { id:'rep-1',  system_name:'고용24 OPEN-API',               operator:'고용노동부 / 한국고용정보원',  api_purpose:'REPORT', official_api:'Y',              apply_status:'PENDING',  api_key_issued:false, env_var_name:null,              api_key_expires:null,         api_apply_url:'https://www.work24.go.kr',                                  notes:'산재조사표·중대재해 보고 자동화 목적.' },
  { id:'rep-2',  system_name:'화관법 민원24 (화학물질종합)',    operator:'환경부 / 화학물질안전원',      api_purpose:'REPORT', official_api:'PARTIAL',        apply_status:'PENDING',  api_key_issued:false, env_var_name:null,              api_key_expires:null,         api_apply_url:'https://icis.me.go.kr/siteInfo/siteInfo.do',                notes:'화관법 민원24 온라인 신청·Open API 연계. 화학물질 취급시설 신고 자동화.' },
  { id:'rep-3',  system_name:'올바로시스템',                   operator:'환경부 / 한국환경공단',        api_purpose:'REPORT', official_api:'PARTIAL',        apply_status:'PENDING',  api_key_issued:false, env_var_name:null,              api_key_expires:null,         api_apply_url:'https://www.data.go.kr/data/15125000/openapi.do',           notes:'폐기물·대기·물환경 신고. 조회 API 공식, 제출 API 확인 필요.' },
  { id:'rep-4',  system_name:'한국전기안전공사 전기안전 API',  operator:'한국전기안전공사',             api_purpose:'REPORT', official_api:'Y',              apply_status:'PENDING',  api_key_issued:false, env_var_name:null,              api_key_expires:null,         api_apply_url:'https://www.data.go.kr/data/15146770/openapi.do',           notes:'검사·점검 데이터 조회·검증. 전기안전관리자 선임신고 검증 목적.' },
  { id:'rep-5',  system_name:'세움터',                        operator:'국토교통부',                  api_purpose:'REPORT', official_api:'PUBLIC-UNCLEAR', apply_status:'PENDING',  api_key_issued:false, env_var_name:null,              api_key_expires:null,         api_apply_url:'https://open.eais.go.kr',                                   notes:'건축 착공신고 전자처리. 외부 API 공개 범위 별도 협의 필요.' },
];

async function loadApis() {
  try {
    const res = await apiCall('GET', '/report-api-registry');
    const items = (res && res.data && Array.isArray(res.data)) ? res.data
                : (res && res.data && res.data.items) ? res.data.items : [];
    if (items.length > 0) {
      ALL_APIS = items; // DB 데이터 우선
    } else {
      ALL_APIS = FALLBACK_APIS; // fallback
    }
  } catch(e) {
    ALL_APIS = FALLBACK_APIS; // fallback
  }
}
```

---

### 2. UI 변경: 카드형 → 테이블(리스트)형

#### 요약 카드 (상단 4개 — 유지)
| 카드 | 내용 |
|------|------|
| 현재 사용 중 | api_purpose='USED' 건수 |
| 접속 정상 | 핑 성공 건수 |
| 신청 대기 | PENDING 건수 |
| 전체 API | 총 건수 |

#### 탭 필터 (테이블 위)
- [전체] [사용 중] [자동신고용]
- 우측: 신청 상태 `<select>` 필터

#### 테이블 컬럼 (11열)
| 순번 | 컬럼 | 내용 |
|------|------|------|
| 1 | 체크박스 | toggleAll |
| 2 | No. | 순번 |
| 3 | 시스템명 | 링크(api_apply_url), 접속 상태 점 |
| 4 | 용도 | USED=초록배지 / REPORT=파랑배지 |
| 5 | 운영기관 | |
| 6 | 환경변수 | `<code>` 태그 또는 '-' |
| 7 | API 키 | ✓발급 / 미발급 배지 |
| 8 | 신청 상태 | PENDING/APPLIED/APPROVED/REJECTED 배지 |
| 9 | 만료일 | 없으면 '-', 60일 이내면 주황 경고 배지 |
| 10 | 접속 | 핑 응답시간(ms) 또는 실패 |
| 11 | 액션 | [접속확인 🔄] [수정 ✏️] |

#### 행 클릭 시 비고 표시 (테이블 하단)
- 선택한 행의 `notes` 필드를 테이블 아래 info 카드에 표시
- 다른 행 클릭 시 교체

---

### 3. 접속 확인 로직 (기존 유지)

```javascript
async function checkOne(id, url) {
  // HEAD no-cors 방식 — 기존 로직 동일
  // 도메인 접속 가능 여부만 확인 (API 키 유효성 X)
}
```

---

### 4. 상태 수정 모달 (기존 유지 + 만료일 추가)

```
기존 필드: 신청 상태 / 신청일 / 승인일 / API 키 발급 여부
추가 필드: API 키 만료일 (date input)
```

PATCH 요청: `PATCH /report-api-registry/{id}`  
body: `{ apply_status, apply_date, approved_date, api_key_issued, api_key_expires }`

---

### 5. 신규 추가 모달 (기존 유지 + 용도/환경변수/만료일 추가)

```
기존: 시스템명 / 운영기관 / 공식API / URL / 활용도 / 신청방법 / 권고 / 로그인 / 비고
추가: 용도 select (USED/REPORT/BOTH) / 환경변수명 / API 키 만료일
```

---

### 6. 페이지 제목 및 설명 변경

```
제목: 외부 API 모니터
설명: 외부 기관으로부터 API 키를 발급받아 사용하는 외부 API 관리
```

---

## 파일 위치

`admin/full-version/html/horizontal-menu-template/api-monitor-external.html`

## 참고 파일

- `member-list.html` — 테이블 구조 참고
- `assets/js/tai/globals.js` — apiCall() 사용
- `assets/js/tai/toast.js` — showToast() 사용

## 완료 기준

- [ ] 페이지 로드 시 9개 API 전부 표시
- [ ] 사용중/자동신고용 탭 필터 동작
- [ ] 전체 접속 확인 버튼 동작
- [ ] 상태 수정 모달 저장 동작
- [ ] 행 클릭 시 비고 표시
- [ ] 만료일 60일 이내 경고 배지 표시
