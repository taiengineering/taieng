# WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001
# obligation_instance 실제 생성 — 첫 구현

**작성일:** 2026-06-24 | **상태:** 완료 (실제 생성, DDL+INSERT)
**선행:** WO-OBLIGATION-GENERATOR-001
**범위:** CONFIRMED 452만 사용. HARVESTED 310 금지. APPENDIX 금지. THRESHOLD 보류.
**목적:** 설계된 obligation_instance를 실제 데이터로 생성. 입력→cmc→obligation_instance 첫 실현.

> 17회차 만에 452 규칙이 실제로 살아 움직이는지 확인.

---

## 결론 먼저

```
첫 obligation_instance 생성 성공.

테스트 factory (INDUSTRIAL, has_welding+has_crane+has_chemical):
  → 75 obligation_instance 생성 (전부 ACTIVE)
    has_chemical_substance → MATERIAL_ACT: 32
    has_crane             → EQUIPMENT_ACT: 25
    has_welding           → WORK_ACT:      18

검증:
  ✅ 75건 전부 CONFIRMED 출처 (non-confirmed 누출 0)
  ✅ HARVESTED/UNIVERSAL 누출 0
  ✅ distinct cmc 75 = distinct clause 75 (1:1, 중복 없음)
  ✅ reason 사람이 읽을 수 있게 생성됨

→ cmc 452 규칙이 입력값에 반응해 의무를 생성한다.
→ 입력 → cmc → obligation_instance 라인 실현.
```

---

## TASK: obligation_instance 테이블 생성 (DDL)

```sql
CREATE TABLE obligation_instance (
  id UUID PK,
  factory_id UUID NOT NULL,
  generation_batch TEXT NOT NULL,
  source_cmc_id UUID NOT NULL,
  source_clause_id UUID NOT NULL,
  trigger_type TEXT NOT NULL,
  trigger_l2 TEXT, detail TEXT,
  fired_by TEXT, input_field TEXT,
  reason TEXT NOT NULL,
  applicable_sectors TEXT[] NOT NULL,
  confidence NUMERIC NOT NULL,
  status TEXT DEFAULT 'ACTIVE',  -- ACTIVE/MISSING_DATA/AMBIGUOUS/HELD
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(factory_id, source_cmc_id)
);
```

```
독립 테이블: facility_applicability(GPT Compiler)와 물리 분리.
→ 기존 Check Engine 안 건드림.
```

---

## 생성 규칙 (실행된 SQL 로직)

```
INSERT INTO obligation_instance
SELECT ... FROM condition_mapping_candidate cmc
WHERE cmc.review_status = 'CONFIRMED'           -- CONFIRMED만
  AND cmc.condition_type IN ('WORK_ACT','EQUIPMENT_ACT',
                             'MATERIAL_ACT','FACILITY_ACT')  -- EXISTS
  AND cmc.input_field IN ({factory의 has_*=true})  -- 입력 매칭
  AND cmc.input_value = 'true'
  AND {factory.sector} = ANY(cmc.applicable_sectors)  -- sector 일치
ON CONFLICT (factory_id, source_cmc_id) DO NOTHING;

변환:
  source_cmc_id     ← cmc.id
  source_clause_id  ← cmc.semantic_clause_id
  trigger_type      ← cmc.condition_type
  trigger_l2        ← condition_code split[2]
  detail            ← condition_code split[3]
  fired_by          ← input_field || '=true'
  reason            ← input_field || ' 있음 → ' || 조문요지
  confidence        ← cmc.confidence (0.90)
  status            ← 'ACTIVE'
```

---

## 검증 결과

| 항목 | 결과 | 판정 |
|---|---|---|
| 생성 건수 | 75 | ✅ |
| 전부 ACTIVE | 75 | ✅ |
| CONFIRMED 출처 | 75 (누출 0) | ✅ |
| HARVESTED/REJECTED 누출 | 0 | ✅ |
| UNIVERSAL(NONE) 누출 | 0 | ✅ |
| distinct cmc / clause | 75 / 75 (1:1) | ✅ |

### 생성된 의무 예시 (reason 직독)

```
EQUIPMENT_ACT:CRANE:GENERAL
  "has_crane 있음 → 사업주는 크레인을 사용하여 작업을 하는 경우..."
  "has_crane 있음 → 사업주는 타워크레인을 벽체에 지지하는 경우..."
  "has_crane 있음 → 사업주는 이동식 크레인을 사용하는 경우..."

→ 입력(has_crane) → 조문(크레인 의무) 연결이
  사람이 읽을 수 있는 reason으로 살아남.
```

---

## 핵심 발견

### 발견 1: 452 규칙이 실제로 작동한다

```
17회차 동안 만든 cmc가 처음으로 입력에 반응.
has_welding/has_crane/has_chemical → 75 의무 인스턴스.
→ "매핑 자산"이 "살아있는 엔진"으로 전환.
→ 더 이상 SQL 모사가 아닌 실제 테이블 데이터.
```

### 발견 2: 실제 입력 수집은 아직 sector+숫자 수준

```
facility_profiles.input_fields = "제공된 필드 목록"
  (sector/ksic/workforce/building/metrics)
  → has_welding 같은 EXISTS 신호 없음.

diagnosis_session.input_snapshot 예:
  {sector, employee_count, ksic_code, hazardous_material:false}
  → 일부 boolean만, 세부 has_* 없음.

→ 생성기는 작동하나, 실제 운영 입력에 has_*가 아직 없음.
→ 이번엔 테스트 입력(has_welding 등)으로 실증.
→ 다음 과제: 입력 수집 단계에서 has_* 채우기.
```

### 발견 3: review_status 필터가 정확히 작동

```
CONFIRMED 452만 생성에 사용.
HARVESTED 310(UNIVERSAL 포함) 누출 0.
REJECTED 35 누출 0.

→ 정책(CONFIRMED만 실행)이 데이터로 강제됨.
→ UNIVERSAL baseline은 아직 안 나옴(HARVESTED라서).
```

### 발견 4: obligation_instance가 독립 가동

```
facility_applicability(394만, GPT Compiler) 안 건드림.
obligation_instance는 별도 테이블에 75건 생성.
→ 두 시스템 평행 유지.
→ cmc 경로가 독립적으로 살아남.
```

---

## 성공 기준 답변

```
임의 factory 1개에 대해
facility_profiles → cmc 452 → obligation_instance 생성됐는가?

✅ factory e9c56af6 (INDUSTRIAL)
   has_welding + has_crane + has_chemical_substance
   → 75 obligation_instance (ACTIVE)

라인 실현:
  입력(has_*) → cmc CONFIRMED 452 매칭 → obligation_instance
```

---

## 현재 한계 (정직한 기록)

```
1. UNIVERSAL baseline 없음
   - CONFIRMED UNIVERSAL 0 (전부 HARVESTED)
   - 75건은 EXISTS 특화 의무만
   - 교육·보고·점검 등 공통 의무 누락
   → UNIVERSAL REVIEW 승격 필요

2. 실제 입력에 has_* 없음
   - 운영 입력은 sector+숫자+일부 boolean
   - has_welding 등 세부 EXISTS 입력 미수집
   - 이번엔 테스트 입력으로 실증
   → 입력 수집 UI/플로우에 has_* 추가 필요

3. THRESHOLD/APPENDIX 미구현 (의도된 보류)
   - 50인 안전관리자 등 수치 의무 없음
```

---

## 다음 단계

```
WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001 (현재) — 완료. 첫 생성.
      ↓
선택지 1: UNIVERSAL 310 REVIEW → CONFIRMED 승격
  → baseline 포함 완전 생성 (가장 큰 효과)
선택지 2: 입력 수집 플로우에 has_* 추가
  → 실제 factory가 has_* 입력하게
선택지 3: obligation_instance → Check Engine/6W 인계 구현
  → 의무를 체크항목/일정으로 전개
```

---

*WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001 완료. 첫 obligation_instance 75건 생성.*
*입력→cmc→obligation_instance 라인 실현. CONFIRMED만, 누출 0.*
*핵심: 452 규칙이 살아 움직임. 단 UNIVERSAL baseline·실입력 has_*는 후속 과제.*
