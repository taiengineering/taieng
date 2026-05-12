# TAI Safe 엔진설정 > 문서 메뉴 기획서

> 작성일: 2026-04-02  
> 작성자: Claude (CTO)  
> 버전: v1.0

---

## 1. 배경 및 목적

### 문제

```
안전관련 법령에는 크게 두 가지 문서 의무가 있음:
  1. 신고·통보 의무 (REPORT/NOTIFY) → 이미 form_templates 구축
  2. 내부 문서보관 의무 (DOCUMENT) → 52건 신규 수집 완료

문서보관 의무 52건 전체 = 자유서식 (100%)
→ 법이 내용만 요구하고 형식은 지정 안 함
→ 각 회사가 제각각 만들어 씀
→ 겸직 안전관리자: "뭔 어떻게 써야 하나요?"
→ 현재 TAI Safe에 해결책 없음
```

### 목적

```
1. 법정서식 / TAI표준서식 / 자유서식 3분류로 전체 서식 통합 관리
2. 서식별 사용 시점·제출처·보관기간 명확화
3. TAI 표준 템플릿 제공 → 겸직 안전관리자 핵심 Pain Point 해소
4. 보관기간 자동 추적 → 감사·실사 대응 기반 구축
5. SaaS 구독 Lock-in 핵심 기능화
```

---

## 2. 서식 3분류 정의

| 유형 | 코드 | 정의 | 예시 | TAI 역할 |
|------|------|------|------|----------|
| 법정서식 | LEGAL | 법령에서 "별지 제N호서식"으로 양식 지정 | 산업재해조사표, 안전관리자선임보고서 | 양식 제공 + 자동작성 + 전자제출 |
| TAI표준서식 | STANDARD | TAI Safe가 제공하는 KOSHA 권장 기반 표준 양식 | 위험성평가 결과서, 안전보건교육 실시기록부 | 양식 제공 + 자동작성 + 보관관리 |
| 자유서식 | FREE | 회사 자체 양식 사용 (TAI는 필수항목 가이드만 제공) | 회의록, 점검일지 | 필수항목 안내 + 업로드 보관 |

---

## 3. 서식별 핵심 메타데이터

```
각 서식마다 저장해야 할 정보:

[기본 정보]
  form_code         코드 (ex: OSHACT-FORM-001, DOC-STD-001)
  form_name         서식명
  form_type         LEGAL / STANDARD / FREE
  form_category     REPORT / DOCUMENT / NOTIFY / APPOINT / INSPECT

[법적 근거]
  law_name          관련 법령명
  law_article       조문
  legal_basis       법적 근거 요약

[사용 시점]
  use_case          언제 이 서식을 써야 하는지 (트리거 이벤트)
  trigger_event     발생 이벤트 (ex: 위험성평가 실시, 교육 완료)

[제출 정보]
  submit_agency     제출처 기관명 (ex: 관할 지방고용노동청장)
  submit_method     ONLINE / FAX / MAIL / VISIT / KEEP(보관용)
  submit_url        전자제출 URL
  submit_timing     제출 기한 (ex: 선임 후 14일 이내)

[보관 정보]
  retention_years   보관 의무 기간 (년)
  retention_start   보관 시작 기준 (WRITE_DATE / EVENT_DATE / LAST_RECORD_DATE)

[과태료]
  penalty_summary   미제출·미보관 시 과태료 요약

[자동작성]
  template_fields   서식 필드 정의 JSON (자동 채움용)
  required_fields   필수 기재항목 배열
```

---

## 4. 화면 구성 — 엔진설정 > 문서

### 4.1 탭 구성 (3개)

```
[법정서식]   [TAI표준서식]   [자유서식가이드]
```

### 4.2 법정서식 탭

```
목적: 법령에서 지정한 서식 목록 + 자동작성 + 전자제출

리스트 컬럼:
  No | 서식코드 | 서식명 | 관련법령 | 제출처 | 제출방법 | 제출기한 | 과태료 | 관리

접수방법 뱃지 색상 규칙:
  [전자제출] 초록
  [팩스]    파랑
  [우편]    주황
  [방문]    빨강
  [보관용]  회색

관리 버튼:
  전자제출 가능한 서식 → [전자제출 바로가기] 버튼
  다운로드 → HWP/PDF
  상세 → 상세 모달
```

### 4.3 TAI표준서식 탭

```
목적: 자유서식 의무에 대해 TAI가 제공하는 권장 양식

리스트 컬럼:
  No | 서식코드 | 서식명 | 관련법령 | 보관기간 | 사용시점 | 관리

핵심 서식 10종 (우선순위):
  1.  위험성평가 결과서 (3년 보존)
  2.  안전보건교육 실시기록부 (3년 보존)
  3.  안전보건위원회 회의록 (2년 보존)
  4.  산업재해 발생 원인 기록서 (3년 보존)
  5.  안전관리비 사용명세서 (3년 보존)
  6.  전기설비 점검일지 (4년 보존)
  7.  작업환경측정 결과 보관대장 (5년 보존)
  8.  건강진단 결과 보관대장 (5년 보존)
  9.  소방시설 자체점검 결과서 (2년 보존)
  10. 안전점검 결과서 (2년 보존)

관리 버튼:
  [자동작성] → 회사정보·날짜·담당자 자동 채움 후 PDF 저장
  [다운로드] → PDF/엑셀
  [상세]     → 상세 모달
```

### 4.4 자유서식가이드 탭

```
목적: 완전 자유서식 의무에 대해 필수기재항목만 안내

리스트 컬럼:
  No | 의무명 | 관련법령 | 보관기간 | 필수기재항목 | TAI표준서식 | 관리

기능:
  각 의무별 "최소한 이것만 적으면 됩니다" 가이드
  TAI표준서식이 있으면 연결
  [업로드] → 직접 작성한 서류 보관함에 업로드
```

### 4.5 공통 — 보관현황 대시보드 (상단 요약)

```
┌──────────────────────────────────────────────────────┐
│  전체 보관 의무: 52건    보관 중: 0건    미완료: 52건  │
│  ⚠️ 만료 임박 (D-30): 0건  🔴 만료 초과: 0건          │
└──────────────────────────────────────────────────────┘
```

### 4.6 서식 상세 모달

```
┌──────────────────────────────────────────────────────┐
│  [서식명]                              [유형 뱃지]   │
├──────────────────────────────────────────────────────┤
│  법적 근거    산업안전보건법 시행규칙 제37조제2항      │
│  사용 시점    위험성평가를 실시한 후 결과와 조치사항을 기록할 때 │
│  제출처       내부 보관 (외부 제출 불필요)             │
│  제출방법     [보관용]                                │
│  제출기한     위험성평가 완료 즉시                     │
│  보관기간     3년                                     │
│  과태료       미보존 시 과태료 500만원 이하             │
├──────────────────────────────────────────────────────┤
│  필수 기재항목                                        │
│  ✅ 위험성평가 대상 유해·위험요인                      │
│  ✅ 위험성 결정의 내용                                │
│  ✅ 위험성 결정에 따른 조치 내용                      │
│  ✅ 평가 실시일 및 실시자                             │
│  ✅ 근로자 의견 청취 내용                             │
├──────────────────────────────────────────────────────┤
│  [표준양식 다운로드]  [자동작성]  [보관함 업로드]      │
└──────────────────────────────────────────────────────┘
```

---

## 5. 추가 아이디어 — TAI 고유 기능

### 5.1 보관기간 자동 추적

```
서류 작성/업로드 → 보관 시작일 자동 기록
→ 보관 만료일 자동 계산
→ D-30: 이메일·카카오 알림
→ D-7: 재알림
→ 만료 후: 대시보드 빨간 표시

"위험성평가 결과서 2026-01-15 작성
 만료 예정: 2029-01-15
 만료까지 1,019일 남음"
```

### 5.2 감사·실사 대응 패키지

```
[감사 대응 리포트 출력] 버튼
→ 현재 보관 중인 문서 전체 목록
→ 법적 근거 + 보관기간 + 작성일 포함
→ PDF 1페이지로 출력
→ 고용노동부 점검 시 즉시 제출 가능
```

### 5.3 서식 자동작성 (SaaS 핵심 기능)

```
회사 프로필 데이터 활용:
  회사명, 사업장 주소, 대표자명
  담당 안전관리자명, 연락처
  업종코드, 근로자수

→ 서식 열기 → 기본정보 자동 채움
→ 작성일 자동 입력
→ 작성자 서명란 자동 (로그인 사용자)
→ PDF 저장 → 보관함 자동 등록
```

### 5.4 서식 사용 안내 연결 (엔진 연동)

```
법령 의무 진단 결과에서
"위험성평가 실시 의무" 클릭
→ 관련 서식 자동 연결
→ "이 의무에 필요한 서식: 위험성평가 결과서"
→ [바로 작성하기] 버튼
```

---

## 6. DB 설계

### 6.1 document_form_master (신규 테이블)

```sql
CREATE TABLE document_form_master (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  form_code         varchar(50) UNIQUE NOT NULL,
  form_name         varchar(200) NOT NULL,
  form_name_short   varchar(100),
  form_type         varchar(20) NOT NULL DEFAULT 'STANDARD',
  -- LEGAL / STANDARD / FREE
  form_category     varchar(30),
  -- REPORT / DOCUMENT / NOTIFY / APPOINT / INSPECT
  obligation_type   varchar(20),
  law_name          varchar(200),
  law_article       varchar(100),
  legal_basis       text,
  use_case          text,
  trigger_event     text,
  submit_agency     varchar(100),
  submit_method     varchar(50) DEFAULT 'KEEP',
  -- ONLINE / FAX / MAIL / VISIT / KEEP
  submit_url        text,
  submit_timing     varchar(100),
  retention_years   integer,
  retention_start   varchar(50) DEFAULT 'WRITE_DATE',
  -- WRITE_DATE / EVENT_DATE / LAST_RECORD_DATE
  penalty_summary   text,
  required_fields   jsonb,
  -- 필수 기재항목 배열
  template_fields   jsonb,
  -- 자동작성 필드 정의
  hwp_url           text,
  pdf_url           text,
  excel_url         text,
  sector            varchar(20) DEFAULT 'BUILDING',
  sort_order        integer DEFAULT 0,
  is_active         boolean DEFAULT true,
  created_at        timestamptz DEFAULT now(),
  updated_at        timestamptz DEFAULT now()
);
```

### 6.2 form_templates 기존 테이블 확장

```sql
ALTER TABLE form_templates
  ADD COLUMN IF NOT EXISTS form_type        varchar(20) DEFAULT 'LEGAL',
  ADD COLUMN IF NOT EXISTS use_case         text,
  ADD COLUMN IF NOT EXISTS submit_agency    varchar(100),
  ADD COLUMN IF NOT EXISTS submit_method    varchar(50) DEFAULT 'KEEP',
  ADD COLUMN IF NOT EXISTS submit_url       text,
  ADD COLUMN IF NOT EXISTS retention_years  integer,
  ADD COLUMN IF NOT EXISTS penalty_summary  text,
  ADD COLUMN IF NOT EXISTS required_fields  jsonb,
  ADD COLUMN IF NOT EXISTS template_fields  jsonb,
  ADD COLUMN IF NOT EXISTS sector           varchar(20) DEFAULT 'BUILDING',
  ADD COLUMN IF NOT EXISTS sort_order       integer DEFAULT 0,
  ADD COLUMN IF NOT EXISTS updated_at       timestamptz DEFAULT now();
```

### 6.3 document_storage (보관함)

```sql
CREATE TABLE document_storage (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id        uuid NOT NULL,
  form_code         varchar(50),
  document_name     varchar(200) NOT NULL,
  form_type         varchar(20),
  obligation_type   varchar(20),
  law_name          varchar(200),
  retention_years   integer,
  write_date        date NOT NULL,
  expire_date       date,
  -- write_date + retention_years 자동 계산
  file_url          text,
  file_type         varchar(20),
  -- PDF / HWP / EXCEL / IMAGE / OTHER
  status            varchar(20) DEFAULT 'ACTIVE',
  -- ACTIVE / EXPIRING(D-30) / EXPIRED
  memo              text,
  created_by        uuid,
  created_at        timestamptz DEFAULT now(),
  updated_at        timestamptz DEFAULT now()
);
```

---

## 7. 구현 단계

### Phase 1 — 기본 목록 관리 (즉시)

```
엔진설정 > 문서 페이지 생성
탭 3개 (법정서식 / TAI표준서식 / 자유서식가이드)
각 탭별 리스트
document_form_master 테이블 + 초기 데이터
```

### Phase 2 — 표준서식 템플릿 (다음 단계)

```
TAI표준서식 10종 PDF/엑셀 제작
자동작성 기능 (회사정보 자동 채움)
```

### Phase 3 — 보관함 및 알림 (SaaS 연동)

```
document_storage 테이블
보관기간 자동 추적
D-30 / D-7 알림 발송
감사대응 리포트 출력
```

---

## 8. 사이트맵 위치

```
엔진설정
  ├── 전역변수(system-codes.html)
  ├── 시설(engine-factory.html)
  ├── 설비(engine-equipment.html)
  ├── 모델(engine-model.html)
  ├── 법규(engine-legal.html)
  ├── 사고(engine-accident.html)
  ├── 엔진(engine-run.html)
  ├── TBM(engine-tbm.html)
  ├── 교육(engine-education.html)
  └── 문서  ← 신규 추가
        ├── 법정서식
        ├── TAI표준서식
        └── 자유서식가이드
```
