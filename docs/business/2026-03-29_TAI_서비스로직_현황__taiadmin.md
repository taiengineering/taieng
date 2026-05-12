# TAI Safe — 서비스 로직 및 개발 현황

> 작성일: 2026-03-29 | 작성: 회의실 창

---

## 1. 서비스 개요

TAI Safe는 사업장(건물·공장·건설현장·특수시설)의 기본 정보를 입력하면
적용되는 법령, 선임 의무, 점검 의무, 신고 의무, 벌칙을 자동으로 판정하는
**산업안전 법령 진단 SaaS 플랫폼**입니다.

**핵심 가치:** 안전관리 담당자나 전문가 없이도 내 사업장에 어떤 법이 적용되는지
즉시 확인할 수 있습니다.

---

## 2. 서비스 구조

### 2-1. 섹터 (진단 대상 유형)

| 섹터 코드 | 명칭 | 핵심 판단 변수 | 대상 |
|----------|------|--------------|------|
| BUILDING | 건물·시설 | 건물용도 / 연면적 / 층수 / 수전용량 | 사무실, 판매점, 공장, 창고 등 |
| MANUFACTURING | 공장·제조업 | KSIC 업종코드 / 근로자수 / 위험물 여부 | 제조업 사업장 |
| CONSTRUCTION | 건설현장 | 공사금액 / 근로자수 / 공사종류 | 건설공사 현장 |
| SPECIAL_FACILITY | 특수시설 | 시설유형 / 병상수 / 학생수 | 병원, 학교, 복지시설, 다중이용업소 |

> **건설업 핵심:** 공사금액(도급금액)이 가장 중요한 판단 변수
> **제조업 핵심:** KSIC 업종코드가 가장 중요한 판단 변수

### 2-2. 진단 단계

```
1단계 (무료) — 기초 정보 입력
  └─ 섹터 선택 + 면적·근로자수·업종 등 기본값
  └─ 결과: 주요 법령 카테고리 + 선임 의무 여부 + 리스크 레벨

2단계 (유료) — 공정 선택
  └─ 제조업: KSIC 세분류 + 공정 선택 (용접/도장/연삭 등)
  └─ 건설: 공종 선택 (토공/철근/콘크리트 등)
  └─ 결과: 법령별 의무 목록 + 신고 D-day + PPE 요건

3단계 (유료) — 설비 등록
  └─ 유해위험기계기구 등록 (크레인/리프트/보일러 등)
  └─ 결과: 설비별 법정검사 D-day + 검사기관
```

---

## 3. 법령 판정 엔진 로직

### 3-1. 판정 흐름

```
입력값 (factory_id + sector + input 객체)
       ↓
master_building_legal_rules 에서 해당 sector + stage 룰 조회
       ↓
각 룰의 condition_code / operator / value 와 입력값 비교
       ↓
매칭된 룰 → 선임/점검/신고/조치 4가지로 분류
       ↓
factory_diagnosis_results 에 결과 저장
       ↓
신고 의무 룰 → report_events 자동 생성 (D-day 계산)
```

### 3-2. 조건 평가 연산자

| 연산자 | 의미 | 예시 |
|--------|------|------|
| gte / >= | 이상 | worker_count >= 50 |
| lte / <= | 이하 | gross_floor_area <= 1000 |
| eq / == | 같음 | sector == 'MANUFACTURING' |
| in | 포함 | ksic_lv1_code IN 'C24,C25' |
| not_in | 미포함 | ksic_lv1_code NOT_IN 'C10,C11' |

### 3-3. 리스크 레벨 산정

| 적용 룰 수 | 리스크 레벨 |
|-----------|----------|
| 10개 이상 | HIGH (빨강) |
| 5~9개 | MEDIUM (주황) |
| 4개 이하 | LOW (초록) |

---

## 4. 데이터 현황 (2026-03-29 기준)

### 4-1. 법령 수집 현황

| 구분 | 수량 |
|------|------|
| 수집된 법률 (본법) | 37개 |
| 수집된 법령 전체 (시행령·규칙 포함) | 436개 |
| 조문 수 | 31,431개 |
| 항 수 | 49,844개 |

**주요 수집 법령:**

- **건물·전기·소방:** 산업안전보건법, 전기안전관리법, 화재예방법, 소방시설법, 위험물안전관리법, 고압가스안전관리법
- **제조업:** 산업안전보건기준에 관한 규칙, 화학물질관리법, 에너지이용합리화법
- **건설업:** 건설산업기본법, 건설기술진흥법, 건설기계관리법, 중대재해처벌법
- **특수시설:** 의료법, 다중이용업소법, 사회복지사업법, 노인복지법, 어린이놀이시설 안전관리법, 학교안전사고 예방법

**미수집 (법제처 API 미등록):**
- 한국전기설비규정 (KEC) — 민간 기술기준
- 화재안전기술기준 (NFTC) — 소방청 고시
- 화재안전성능기준 (NFPC) — 소방청 고시

### 4-2. 판정 룰 현황

| 섹터 | 1단계 | 2단계 | 3단계 | 합계 |
|------|-------|-------|-------|------|
| BUILDING | 398 | 1 | 1 | 400 |
| MANUFACTURING | 13 | 1 | 1 | 15 |
| CONSTRUCTION | 10 | 1 | 1 | 12 |
| SPECIAL_FACILITY | 6 | 0 | 0 | 6 |
| **합계** | **427** | **3** | **3** | **433** |

> ⚠️ MANUFACTURING·CONSTRUCTION·SPECIAL_FACILITY 룰이 부족합니다.
> 법령 원문 수집은 완료됐으나 GPT 변환(OpenAI 할당량 초과)으로 룰 적재가 지연 중입니다.

---

## 5. API 구조

### 5-1. 법령 진단 API

| 엔드포인트 | 설명 | 과금 |
|-----------|------|------|
| POST /legal-engine/diagnose/step1 | 1단계 기초 진단 | 무료 |
| POST /legal-engine/diagnose/step2 | 2단계 공정 진단 | 유료 |
| POST /legal-engine/diagnose/step3 | 3단계 설비 진단 | 유료 |
| GET /legal-engine/diagnose/{id}/latest | 최신 진단 결과 조회 | - |
| GET /legal-engine/diagnose/{id}/history | 진단 이력 | - |

**step1 요청 예시:**
```json
{
  "factory_id": "uuid",
  "sector": "MANUFACTURING",
  "input": {
    "ksic_lv1_code": "C25",
    "worker_count": 80,
    "has_hazardous_material": true,
    "electric_capacity_kw": 200
  }
}
```

**step1 응답 예시:**
```json
{
  "status": "success",
  "diagnosis_id": "uuid",
  "stage": 1,
  "sector": "MANUFACTURING",
  "rule_count": 8,
  "summary": {
    "applicable_law_categories": ["산업안전보건법", "전기안전관리법", "위험물안전관리법"],
    "appointment_required": true,
    "key_obligations": ["안전관리자 1명 선임 (50명 이상)"],
    "risk_level": "HIGH"
  },
  "rules": [...]
}
```

### 5-2. 법령 수집 API (서버 로컬 실행용)

| 엔드포인트 | 설명 |
|-----------|------|
| POST /law-collector/collect/all | 전체 법령 수집 (백그라운드) |
| POST /law-collector/collect/{법령명} | 단건 수집 |
| POST /law-collector/recollect/{법령명} | 강제 재수집 (항·호목 재삽입) |
| GET /law-collector/status | 수집 상태 확인 |

---

## 6. 프론트엔드 화면 구조

### 6-1. tadmin (파트너 어드민)

| 페이지 | 파일 | 상태 |
|--------|------|------|
| 대시보드 | index.html | ✅ 완성 |
| 시설 관리 | factory-list.html | ✅ 완성 (법령진단 탭 추가 중) |
| 법령진단 1단계 | diagnosis-step1.html | ✅ 신규 완성 |
| 계약 내역 | my-contract.html | ✅ 완성 |
| 교육 관리 | education-list.html | ✅ 완성 |
| 공정 관리 | process-select.html | ✅ 완성 |

### 6-2. admin (백오피스)

| 페이지 | 파일 | 상태 |
|--------|------|------|
| 회사 관리 | company-list.html | ✅ 완성 |
| 시설 관리 | factory-list.html | ✅ 완성 |
| 견적 관리 | quote-list.html | ✅ 완성 |
| 계약 관리 | contract-list.html | ✅ 완성 |
| 권한 관리 | permission.html | ✅ 완성 |
| 교육 관리 | education-list.html | ✅ 완성 |

### 6-3. taieng.co.kr (홈페이지)

| 페이지 | 상태 |
|--------|------|
| 메인 홈페이지 | ✅ 완성 (슬롯머신 지표 바, 5개 역할 카드) |
| 법적진단 설문 | survey.html ✅ (크몽 연동, 17건 접수) |
| 서비스 소개 | tai-safe.html ✅ |

---

## 7. DB 핵심 테이블

| 테이블 | 역할 | 건수 |
|--------|------|------|
| law_master | 법령 마스터 | 436개 |
| law_article | 법령 조문 | 31,431개 |
| law_paragraph | 조문 항(項) | 49,844개 |
| master_building_legal_rules | 판정 룰 | 433개 |
| factory_diagnosis_results | 진단 결과 이력 | 0개 (미사용) |
| factories | 시설 | 9개 |
| legal_obligations | 신고 의무 정의 | 11개 |
| form_templates | 서식 템플릿 | 11개 |
| report_events | 신고 D-day 이벤트 | - |

---

## 8. 개발 이슈 현황

### 🔴 긴급 이슈

| 이슈 | 원인 | 해결 방법 |
|------|------|----------|
| 판정 룰 부족 (MANUFACTURING 13개, CONSTRUCTION 10개) | OpenAI 429 할당량 초과로 GPT 변환 중단 | OpenAI 할당량 복구 후 law_collector → GPT 변환 → DB 적재 |
| 산안법 항·호목 수집 오류 수정 후 재수집 필요 | 최초 수집 시 항 저장 중 오류, is_new_version=false로 재수집 건너뜀 | recollect 엔드포인트 추가로 해결 완료 |

### 🟡 진행 중

| 이슈 | 상태 |
|------|------|
| 건설·특수시설 시행령·규칙 11개 수집 | 진행 중 (Claude Code 실행 중) |
| factory-list.html 법령진단 탭 추가 | Cursor 작업 중 |
| PDF 생성 (xhtml2pdf v2.0.2) 배포 확인 | Railway 배포 후 테스트 필요 |
| Navbar/Footer 18개 파일 개편 | Cursor 작업 예정 |

### 🟢 완료

| 항목 | 내용 |
|------|------|
| 법령 수집 파이프라인 | 법제처 API → law_master/article/paragraph 적재 완료 |
| 법령 진단 엔진 v4.2.0 | step1/2/3 API 완성, 4개 섹터 판정 가능 |
| diagnosis-step1.html | 4개 섹터 입력폼 + 결과 화면 완성 |
| DB 섹터 분리 | sector / diagnosis_stage 컬럼 추가 완료 |
| BUILDING 룰 398개 | 기존 데이터 마이그레이션 완료 |

---

## 9. 수익 모델

| 단계 | 내용 | 과금 |
|------|------|------|
| 1단계 진단 | 기초 법령 판정 | **무료** |
| 2단계 진단 | 공정별 의무 목록 | 유료 (SaaS 구독) |
| 3단계 진단 | 설비 법정검사 D-day | 유료 (SaaS 구독) |
| 컨설팅 연결 | 진단 결과 → 전문가 연결 | 중개 수수료 |
| 신고서식 자동화 | 법령 신고서류 자동 생성·PDF | 유료 |

**현재 단계:** 오프라인 서비스(크몽/숨고) 수익 먼저 → SaaS 전환

---

## 10. 다음 우선 작업

| 순서 | 작업 | 담당 |
|------|------|------|
| 1 | OpenAI 할당량 복구 후 MANUFACTURING 룰 수집 | GPT 창 |
| 2 | 시행령·규칙 11개 수집 완료 확인 | 백엔드 창 |
| 3 | factory-list.html 법령진단 탭 + 연동 | Cursor |
| 4 | step1 API 실 시설 테스트 (4개 섹터) | 백엔드 창 |
| 5 | Navbar/Footer 18개 파일 개편 | Cursor |
| 6 | PDF v2.0.2 preview-pdf 테스트 | 백엔드 창 |
