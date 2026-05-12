# TAI Safe — 법령진단 3단계 입력폼 & 결과 기획서
## 프론트엔드 + 백엔드

> v1.0 | 2026-03-29 | TAI Engineering

---

## 1. 전체 구조

| 단계 | 입력 핵심값 | 결과 정밀도 | 과금 |
|------|-----------|-----------|------|
| 1단계 기초진단 | 섹터 + 기초정보 | 주요 법령 카테고리 + 선임 여부 | **무료** |
| 2단계 공정진단 | 1단계 + 공정 선택 | 법령별 의무 목록 + 신고 일정 | 유료 |
| 3단계 설비진단 | 2단계 + 설비 등록 | 설비별 법정검사 일정 + D-day | 유료 |

### 섹터별 핵심 판단 변수

| 섹터 | 1단계 핵심 입력값 | 추가 단계 |
|------|-----------------|----------|
| 🏢 건물·시설 | 건물용도 / 연면적 / 층수 / 수전용량 | 설비종류 (3단계) |
| 🏭 공장·제조업 | KSIC업종 / 근로자수 / 위험물여부 | 공정(2단계) → 설비(3단계) |
| 🏗️ 건설현장 | 공사금액 / 근로자수 / 공사종류 | 공종선택(2단계) |
| 🏥 특수시설 | 시설유형 / 연면적 / 병상수·학생수 | 설비종류(3단계) |

---

## PART 1 — 프론트엔드

### 1-1. 1단계 입력폼 (무료)

**URL:** tadmin.taieng.co.kr/diagnosis/{factory_id}/step1

#### STEP 0 — 섹터 선택 (공통)
- 카드 4개: 🏢 건물·시설 / 🏭 공장·제조업 / 🏗️ 건설현장 / 🏥 특수시설
- 선택 시 해당 섹터 입력폼 슬라이드 표시
- 저장: factories.sector 컬럼

#### 1-A. 건물·시설 입력폼
| 필드명 | 입력 타입 | 비고 |
|-------|---------|------|
| 건물 용도 | Select | 소방법 분류 |
| 연면적 (㎡) | Number | 법령 판단 핵심 |
| 지상 층수 | Number | 스프링클러 기준 |
| 상시 근로자수 | Number | 산안법 선임 |
| 수전용량 (kW) | Number | 전기안전관리자 |
| 고압가스 사용 | Toggle Y/N | 고압가스안전관리법 |
| 위험물 취급 | Toggle Y/N | 위험물안전관리법 |

#### 1-B. 공장·제조업 입력폼
| 필드명 | 입력 타입 | 비고 |
|-------|---------|------|
| KSIC 업종 | 검색+단계별 셀렉트 | 대→중→세 3단계 |
| 상시 근로자수 | Number | 핵심 판단값 |
| 사업장 연면적 | Number | 소방·건축 기준 |
| 위험물 취급 | Toggle Y/N | |
| 고압가스 사용 | Toggle Y/N | |
| 화학물질 취급 | Toggle Y/N | 화관법 |
| 보일러 설치 | Toggle Y/N | 에너지이용합리화법 |
| 수전용량 (kW) | Number | |

#### 1-C. 건설현장 입력폼
| 필드명 | 입력 타입 | 비고 |
|-------|---------|------|
| 공사금액 (원) | Number + 단위 | **핵심값** |
| 공사종류 | Select | 건축/토목/전문 |
| 상시 근로자수 | Number | |
| 터널·교량 포함 | Toggle Y/N | 건설안전판정사 |

#### 1-D. 특수시설 입력폼
| 필드명 | 입력 타입 | 비고 |
|-------|---------|------|
| 시설 유형 | Select | 병원/학교/복지 등 |
| 연면적 (㎡) | Number | |
| 병상수 | Number | 의료법 |
| 학생수 | Number | 학교안전법 |

### 1-2. 2단계 입력폼 (유료)

#### 제조업: 공정 선택
- KSIC 기반 추천 공정 체크박스
- 직접 검색 + 태그 방식
- 위험물 상세 (품명·저장량)

#### 건설: 공종 선택
- 공종 체크박스 (토공/철근/거푸집/콘크리트 등)
- 고소작업 높이 / 굴착 깊이 / 밀폐공간 여부

### 1-3. 3단계 입력폼 (유료)
- 설비 추가 버튼 → 모달
- 설비 선택 (별표22 기반)
- 용량 / 설치일 / 마지막 검사일 입력

### 1-4. 결과 화면

#### 1단계 결과 (무료 공개)
- 적용 법령 카테고리 배지
- 선임 의무 요약
- 주요 신고 의무
- 리스크 레벨 (HIGH/MEDIUM/LOW)
- 2단계 업그레이드 배너

#### 2단계 결과
- 법령별 의무 목록 전체 테이블
- 공정별 PPE 요건
- 특별안전교육 대상
- 신고서식 연결 → D-day

#### 3단계 결과
- 설비별 법정검사 일정 (D-day)
- 초과 설비 경고
- 전체 PDF 다운로드
- 이메일 발송

### 1-5. URL 구조

| URL | 설명 |
|-----|------|
| tadmin.taieng.co.kr/diagnosis | 진단 메인 |
| tadmin.taieng.co.kr/diagnosis/{id}/step1 | 1단계 입력 |
| tadmin.taieng.co.kr/diagnosis/{id}/step2 | 2단계 입력 |
| tadmin.taieng.co.kr/diagnosis/{id}/step3 | 3단계 입력 |
| tadmin.taieng.co.kr/diagnosis/{id}/result | 결과 화면 |
| taieng.co.kr/survey | 1단계 무료 (외부) |

---

## PART 2 — 백엔드

### 2-1. DB 스키마 변경

```sql
-- 기존 테이블 컬럼 추가
ALTER TABLE master_building_legal_rules
  ADD COLUMN IF NOT EXISTS sector           VARCHAR(30),
  ADD COLUMN IF NOT EXISTS diagnosis_stage  SMALLINT DEFAULT 1,
  ADD COLUMN IF NOT EXISTS obligation_summary TEXT,
  ADD COLUMN IF NOT EXISTS penalty_summary    TEXT,
  ADD COLUMN IF NOT EXISTS source_api         VARCHAR(100);

-- 신규: 진단 결과 이력
CREATE TABLE factory_diagnosis_results (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  factory_id      UUID REFERENCES factories(id),
  sector          VARCHAR(30) NOT NULL,
  diagnosis_stage SMALLINT NOT NULL,
  input_data      JSONB,
  result_data     JSONB,
  rule_count      INTEGER,
  is_latest       BOOLEAN DEFAULT true,
  created_by      UUID,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 신규: 룰별 적용 결과
CREATE TABLE diagnosis_rule_results (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  diagnosis_id  UUID REFERENCES factory_diagnosis_results(id),
  rule_code     VARCHAR(50),
  rule_name     TEXT,
  law_name      TEXT,
  law_article   TEXT,
  obligation    TEXT,
  due_date      DATE,
  status        VARCHAR(20) DEFAULT 'PENDING',
  form_code     VARCHAR(30),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### 2-2. API 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| POST /legal-engine/diagnose/step1 | 1단계 판정 + 결과 저장 |
| POST /legal-engine/diagnose/step2 | 2단계 추가 판정 |
| POST /legal-engine/diagnose/step3 | 설비 검사 일정 생성 |
| GET /legal-engine/diagnose/{id}/latest | 최신 결과 조회 |
| GET /legal-engine/diagnose/{id}/history | 진단 이력 |
| GET /legal-engine/diagnose/{id}/pdf | 결과 PDF |
| POST /legal-engine/diagnose/{id}/email | 결과 이메일 |

### 2-3. 엔진 판정 로직

```python
def run_diagnosis(factory_id, sector, stage, input_data):
    # 1. 섹터 + 단계에 맞는 룰 조회
    rules = supabase.table('master_building_legal_rules')
              .select('*')
              .eq('sector', sector)
              .lte('diagnosis_stage', stage)
              .eq('is_active', True).execute()

    # 2. 각 룰별 조건 평가
    matched = []
    for rule in rules.data:
        if evaluate_condition(rule, input_data):
            matched.append(rule)

    # 3. 결과 저장 + report_events 생성
    diagnosis = save_diagnosis_result(factory_id, stage, input_data, matched)
    create_report_events(factory_id, matched)
    return build_response(diagnosis, matched)
```

### 2-4. 기존 룰 마이그레이션

```sql
-- 기존 396개 룰 → BUILDING / stage 1 일괄 업데이트
UPDATE master_building_legal_rules
SET sector = 'BUILDING', diagnosis_stage = 1
WHERE sector IS NULL;
```

### 2-5. 개발 순서

| 우선순위 | 작업 | 담당 |
|---------|------|------|
| 🔴 D+1 | DB 컬럼 추가 + 신규 테이블 생성 | 백엔드 창 |
| 🔴 D+2 | 기존 396개 룰 마이그레이션 | 백엔드 창 |
| 🔴 D+3 | step1 API 구현 | 백엔드 창 |
| 🟡 D+4 | step2 / step3 API | 백엔드 창 |
| 🟡 D+5 | 1단계 입력폼 HTML | 프론트 창 |
| 🟡 D+6 | 결과 화면 HTML | 프론트 창 |
| 🟢 D+7 | PDF + 이메일 | 백엔드 창 |
| 🟢 이후 | GPT 룰 수집 → DB 적재 | 데이터 창 |
