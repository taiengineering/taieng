# WO-GAP-001
Check Engine / Check Layer 적합성 분석보고서

작성일: 2026-06-22
작성자: Claude (조사 전담)
단계: 분석 (구현 없음)

---

## 0. 조사 목적

기존 Check Engine과 Check Layer가 새로운 Trigger 기반 구조에
그대로 사용 가능한지 확인한다.

새 구조:
```
입력 → Trigger → 의무후보 → Check Engine → Check Layer → 정제 → 출력
```

기존 구조 전제:
```
Semantic → Sieve → executable_draft → facility_applicability → task_candidate
```

---

## 1. 현재 Check Engine 입력

### 확인된 실제 입력 경로

```
[기존 입력 경로]
rule_candidate (34,456건)
  ↓ part_id 연결
executable_draft (10,725건, 전량 CANDIDATE)
  ↓
draft_slot (binding_field 포함)
  ↓
facility_applicability 판정
```

### executable_draft의 핵심 필드

```
rule_candidate_id  → rule_candidate 참조
part_id            → semantic_clause.source_part_id 참조
article_id         → law_article 참조
pass_count         → slot 통과 수
ambiguous_count    → 애매한 slot 수
unresolved_count   → 미해결 slot 수
slot_count         → 전체 slot 수
status             → 전량 'CANDIDATE'
```

### draft_slot의 binding_field (체크엔진이 검증하는 필드)

실제 존재하는 binding_field 분포:

| binding_field | family_name | 건수 |
|---|---|---|
| equipment_type | EQUIPMENT_SCOPE | 260건 |
| facility_type | FACILITY_SCOPE | 220건 |
| distance_value | DISTANCE_THRESHOLD_FAMILY | 415건 |
| voltage_level | VOLTAGE_THRESHOLD_FAMILY | 142건 |
| concentration_level | CONCENTRATION_THRESHOLD_FAMILY | 110건 |
| employee_count | EMPLOYEE_THRESHOLD_FAMILY 등 | 44건 |
| process_type | PROCESS_SCOPE | 33건 |
| has_tower_crane | UNRESOLVED_CONDITION | 1건 |
| has_blasting | IF_AFTER_INSTALL | 1건 |
| has_asbestos_demo | UNRESOLVED_CONDITION | 1건 |

**핵심 발견**: draft_slot의 binding_field에 이미 `employee_count`, `equipment_type`,
`has_tower_crane`, `has_blasting`, `has_asbestos_demo` 등 소비자 입력 필드가 존재한다.
체크엔진은 이미 소비자 입력값과 연결되는 구조를 갖고 있다.

---

## 2. 현재 Check Engine 출력

### 확인된 실제 출력

```
facility_applicability (3,943,872건)
  applicability_status 분포:
    MISSING_DATA      : 3,773,215건 (95.7%) ← 핵심 문제
    POSSIBLE_CANDIDATE:   128,606건  (3.3%)
    AMBIGUOUS         :    33,038건  (0.8%)
    MATCH_CANDIDATE   :     6,976건  (0.2%)
    NOT_MATCHED       :     2,037건  (0.1%)
```

### 출력 상태 정의

| 상태 | 의미 |
|---|---|
| MISSING_DATA | 판정에 필요한 데이터(binding_field 값)가 없음 |
| POSSIBLE_CANDIDATE | 조건 충족 가능성 있음 (데이터 불완전) |
| AMBIGUOUS | 조건 명확히 판정 불가 |
| MATCH_CANDIDATE | 조건 충족 확인 (의무 발생) |
| NOT_MATCHED | 조건 불충족 (의무 미발생) |

### 출력 구조 (task_candidate)

```
task_candidate (93,326건, 전량 POSSIBLE_OPERATION_TASK 또는 CANDIDATE)
  task_type 분포:
    REPORT_TASK_CANDIDATE       : 42,700건
    INSTALL_TASK_CANDIDATE      : 17,382건 + 324건
    MANAGE_TASK_CANDIDATE       :  9,240건
    INSPECTION_TASK_CANDIDATE   :  8,588건
    MEASURE_TASK_CANDIDATE      :  5,343건 + 123건
    VERIFY_TASK_CANDIDATE       :  3,260건
    APPOINTMENT_TASK_CANDIDATE  :  3,260건
    NOTIFY_TASK_CANDIDATE       :  2,934건
    RECORD_TASK_CANDIDATE       :    326건
    TRAINING_TASK_CANDIDATE     :    123건
    PRESERVE_TASK_CANDIDATE     :    123건
```

### runtime_metadata_resolution (6W 보강 출력)

```
3,395건 존재. overall_completeness 분포:
  100%+ : 546건 (16.1%)
  80~99%: 1,242건 (36.6%)
  50~79%: 1,360건 (40.1%)
  20~49%: 247건 (7.3%)

6W 필드 (who/when/how/condition/schedule/evidence) 모두 RESOLVED인 경우 존재.
실제로 이미 동작했음을 의미.
```

### runtime_candidate (체크엔진 → SaaS 전달 구조)

```
7건 (테스트 데이터)
  candidate_type: inspection, appointment, report
  source_engine: 'legal'
  source_ref_id: 'test-binding-001' 등
  payload: { article, law_name, rule_kind }
  confidence: 1.0
  status: 'projected'
```

---

## 3. 현재 Check Engine이 수행하는 검증

### 확인된 검증 규칙

```
draft_slot의 binding_field 기반 비교:
  operator + value vs 소비자 입력값
  예: employee_count >= 50 → 사업주 employee_count와 비교

family_name 기반 분류:
  EQUIPMENT_SCOPE    → equipment_type 일치 여부
  FACILITY_SCOPE     → facility_type 일치 여부
  EMPLOYEE_THRESHOLD → employee_count 임계값 비교
  DISTANCE_THRESHOLD → 거리 값 비교
  CONCENTRATION_THRESHOLD → 농도 값 비교
  UNRESOLVED_CONDITION → 판정 불가 (AMBIGUOUS 출력)
```

### facility_applicability_detail (세부 검증 항목)

구조:
```
check_type    → 어떤 종류의 검증인가
binding_field → 소비자 입력의 어떤 필드와 비교하는가
facility_column → 실제 비교 대상 컬럼
operator      → 비교 연산자
draft_value   → 법령에서 추출한 기준값
facility_value → 실제 소비자 입력값
result        → PASS / FAIL / MISSING / AMBIGUOUS
reason        → 판정 근거
```

현재 데이터: 0건 (미실행 상태)

---

## 4. Trigger 기반 구조 적합성 분류

### 결론: B. 일부 수정 필요

### 분류 근거

**그대로 사용 가능한 부분:**

1. **runtime_candidate 구조** — Trigger 기반 의무후보를 그대로 담을 수 있다.
   - candidate_type (inspection/appointment/report 등) = task_type과 대응
   - source_engine = 'trigger_based'로 설정
   - source_ref_id = semantic_clause_id로 설정
   - payload = { trigger_codes, law_name, article_no, ... }
   - confidence = HIGH/MEDIUM/LOW 대응

2. **facility_applicability 판정 구조** — 출력 상태 체계가 완전히 적합하다.
   - MATCH_CANDIDATE → 의무 발생 확정
   - POSSIBLE_CANDIDATE → 조건 충족 가능 (추가 확인 필요)
   - NOT_MATCHED → 의무 미발생
   이 3종 구분이 Trigger 기반 구조에서도 그대로 필요하다.

3. **task_candidate 유형 분류** — 그대로 사용 가능.
   - REPORT/INSTALL/MANAGE/INSPECTION/APPOINTMENT 등 유형이 WO-ARCH-001 출력 유형과 일치

4. **runtime_metadata_resolution (6W)** — 구조 그대로 사용 가능.
   - who/when/how/condition/schedule/evidence 6개 필드 구조가 WO-ARCH-001 설계와 동일

5. **draft_slot binding_field** — Trigger와 매핑이 이미 존재한다.
   - employee_count, equipment_type, has_tower_crane 등 이미 정의됨
   - WORK:CONFINED_SPACE와 같은 새 Trigger에 대한 binding_field만 추가 필요

**수정이 필요한 부분:**

1. **입력 경로** — 핵심 변경 필요.
   ```
   기존: rule_candidate → executable_draft → draft_slot
   신규: semantic_clause_id (Trigger 매칭 결과) → 의무후보
   ```
   executable_draft는 Deterministic Compiler가 생성하는 것.
   신규 구조는 Trigger 기반으로 semantic_clause를 직접 조회.
   두 경로를 `facility_applicability`에서 합쳐야 한다.

2. **MISSING_DATA 95.7% 문제** — 근본 원인 확인 필요.
   기존 구조: binding_field에 필요한 소비자 데이터가 없어서 MISSING_DATA.
   신규 구조: Trigger 기반이면 입력 데이터가 충분하므로 MISSING_DATA 비율이 급감할 것.

3. **binding_field 확장** — 일부 필요.
   현재 has_tower_crane (1건), has_blasting (1건), has_asbestos_demo (1건)만 존재.
   WORK Trigger 10종에 대한 binding_field 매핑 확장 필요.

---

## 5. Gap 목록

### Gap 1: 입력 경로 불일치 (핵심)

```
현재 구조:
  rule_candidate (34,456건, 전량 CANDIDATE)
    → executable_draft (10,725건)
      → draft_slot (binding_field)
        → facility_applicability

신규 구조:
  소비자 입력 → Trigger Code Set → semantic_clause 직접 조회
    → 의무후보 풀 (300~600건)
      → 체크엔진 (기존 facility_applicability 구조 활용)

Gap: executable_draft와 draft_slot이 Trigger 기반 의무후보와 연결되지 않음.
     두 경로를 연결하는 어댑터(adapter) 계층 필요.
     또는: 신규 경로가 facility_applicability를 직접 생성하는 방식으로 통합.
```

### Gap 2: MISSING_DATA 95.7% (구조적)

```
현재: facility_applicability 3.9M건 중 95.7%가 MISSING_DATA
원인: draft_slot의 binding_field 값을 소비자 입력(factories 테이블)에서
      매핑할 수 없어서 판정 불가 상태
      - distance_value, voltage_level, concentration_level 등은
        현재 소비자 입력 구조에 없는 필드

신규 구조에서 해결 방법:
  Trigger 기반 의무후보는 이미 입력값이 충족된 것만 생성
  → MISSING_DATA 없이 모두 MATCH_CANDIDATE 또는 POSSIBLE_CANDIDATE로 판정 가능
```

### Gap 3: runtime_candidate source_ref_id 형식

```
현재: source_ref_id = 'test-binding-001', 'bridge-001' 등 임시 형식
신규 필요: source_ref_id = semantic_clause.id (UUID)
           + trigger_code 배열을 payload에 추가
Gap: source_ref_id 형식 변경 필요. 구조는 동일.
```

### Gap 4: task_candidate의 applicability_id 연결

```
현재: task_candidate.applicability_id → facility_applicability.id
      (POSSIBLE_CANDIDATE 또는 MATCH_CANDIDATE인 것만 task_candidate 생성)

신규: 의무후보 → 체크엔진 통과 → task_candidate 생성 흐름은 동일
     단, applicability_id가 신규 의무후보 ID를 참조하도록 변경 필요
```

### Gap 5: 6W (runtime_metadata_resolution) 미연결

```
현재: 3,395건 runtime_metadata_resolution 존재하지만
      task_candidate와의 직접 연결 확인 불가
신규: semantic_clause → 6W 보강 → runtime_metadata_resolution 저장 흐름
     source_article_no가 semantic_clause.source_article_id와 연결되어야 함
Gap: 연결 키 정합성 확인 필요
```

---

## 6. 활용 가능한 기존 자산 목록

| 자산 | 건수/상태 | 활용 방법 |
|---|---|---|
| facility_applicability 판정 상태 체계 | 구조 완비 | 그대로 사용 |
| task_candidate 유형 분류 | 11종 정의됨 | 그대로 사용 |
| runtime_candidate 구조 | 7건 테스트 | 구조 그대로, source_ref_id 변경 |
| runtime_metadata_resolution (6W) | 3,395건 | 구조 그대로, 연결 키 확인 |
| draft_slot binding_field | employee_count 등 존재 | 확장 필요 (3종 → 10종) |
| task_candidate 93,326건 | POSSIBLE_OPERATION_TASK | 기존 데이터는 재평가 필요 |
| runtime_obligation_registry | 0건 (빈 테이블) | 신규 구조 출력 저장에 활용 |

---

## 7. 다음 단계 제안 (WO-CHECK-001 전달 항목)

기존 자산을 최대한 살리는 방향으로 체크엔진 상세설계 시 확정할 것:

```
확정 1. 의무후보 → facility_applicability 변환 어댑터 설계
  - semantic_clause_id를 draft_id 대신 사용하는 방법
  - 또는 신규 obligation_candidate 테이블 생성 후 facility_applicability 연결

확정 2. draft_slot binding_field 확장 범위
  - WORK Trigger 10종 → binding_field 매핑 추가 필요 항목 목록화
  - has_confined_space, has_diving, has_welding 등

확정 3. runtime_candidate payload 표준
  - trigger_codes 배열
  - semantic_clause_id
  - match_source (condition_text / action_text)
  - confidence (HIGH/MEDIUM/LOW)

확정 4. task_candidate 생성 조건
  - facility_applicability.MATCH_CANDIDATE → 즉시 task_candidate 생성
  - POSSIBLE_CANDIDATE → 사용자 확인 후 task_candidate 생성 (requires_activation=true)

확정 5. MISSING_DATA 93,326건 처리 방침
  - 기존 facility_applicability MISSING_DATA는 그대로 두고
  - 신규 Trigger 기반 결과를 별도 factory_id별로 생성
```

---

*WO-GAP-001 완료 | 코드 수정 없음 | 리팩토링 없음 | 구현 없음*
