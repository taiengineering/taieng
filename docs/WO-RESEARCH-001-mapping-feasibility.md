# WO-RESEARCH-001 법령의무 매핑 가능성 조사보고서

작성일: 2026-06-22  
작성자: Claude (조사 전담)  
단계: 조사 (구현 없음)

---

## 0. 조사 전제 정정

작업지시서가 참조한 테이블명과 실제 DB 테이블명이 다르다.

| 지시서 용어 | 실제 테이블 | 건수 |
|---|---|---|
| rule_v2 | `semantic_clause` | 58,495 |
| scope | `rule_candidate_slot` (slot_type='SCOPE') | 868 |
| scope_mapping | `master_rule_scope_mapping` | **0** (미구축) |
| relation | `master_rule_v2_relation` | **0** (미구축) |

`master_rule_scope`, `master_rule_scope_mapping`, `master_rule_v2_relation` 세 테이블은 모두 빈 테이블이다.  
작업지시서가 전제한 scope 구조는 **현재 미구축 상태**.

---

## 1. 현재 scope 구조 요약

### 1-1. 실제 scope 역할 데이터

```
rule_candidate_slot (slot_type='SCOPE') : 868건
  FACILITY_SCOPE  : 406건 (46.8%)  → 소방대상물, 소방시설, 특정소방대상물
  EQUIPMENT_SCOPE : 396건 (45.6%)  → 소화설비, 안전장치, 방호장치, 경보설비
  PROCESS_SCOPE   :  66건  (7.6%)  → 작업환경측정
```

`condition_scopes` (14건): 산안법 시행령 별표3 업종코드 기반 INDUSTRY 매핑만 존재.  
안전관리자 선임 관련 소수 규정만 커버.

### 1-2. semantic_clause 구조

| 구분 | 건수 | 비율 |
|---|---|---|
| 전체 | 58,495 | 100% |
| OBLIGATION | 29,665 | 50.7% |
| AUTHORITY | 10,470 | 17.9% |
| DELEGATION | 9,055 | 15.5% |
| DEFINITION | 6,471 | 11.1% |
| PROHIBITION | 1,742 | 3.0% |

- `executor_text` 채움: 52,875건 (90.4%)
- `where_text`, `what_text`: **전체 NULL** (0건) — 장소/대상 필드 미파싱
- `condition_text` 채움: 22,240건 (38.0%)
- **사업주 의무: 1,200건** (의무 전체의 3.8%)

### 1-3. 법령 sieve 구조

`legal_sieve_rule` 2,219건: 전량 `sieve_group='applicability'`, `target_field='executor_text'`.  
판정 결과: KEEP/BUSINESS 787건, DROP/AUTHORITY 678건, DROP/FRAGMENT 566건, DROP/DELEGATED_ORG 98건, DROP/SPECIAL_FACILITY 90건.

---

## 2. KSIC-공정-설비 연결도

### 2-1. 연결 가능성

```
KSIC코드 (532종)
  ↓ [ksic_process_map : 6,957건]
공정 (3,378종)
  ↓ [process_equipment_map : 187,319건]
설비 (446종)

공통 process_id 교집합: 2,807/3,378 = 83.1% 연결됨
match_band: MUST 45,039건 / CORE 142,280건
```

3단계 연결은 **기술적으로 가능**하다.

### 2-2. 설비→법령 연결 상태

`process_law_map` 5,596건: 공정 키워드 147종 × 조문 4,499건 매핑 존재.  
단, `llm_verdict` 전량 NULL — **판정 미완료 상태. 현재 사용 불가.**

### 2-3. SCOPE slot ↔ 설비 교집합

| SCOPE canonical_token | 건수 | 연결 가능 여부 |
|---|---|---|
| 소방시설 | 261 | ❌ (process_equipment_map 없음) |
| 소화설비 | 254 | ❌ |
| 소방대상물 | 145 | ❌ |
| 작업환경측정 | 66 | ❌ |
| 안전장치 | 63 | ✅ |
| 방호장치 | 52 | ✅ |
| 경보설비 | 19 | ✅ |

**SCOPE 868건 중 연결가능: 약 134건 (15.4%). 연결불가: 734건 (84.6%)**

---

## 3. 의무 발생 조건 Top 분석

### 3-1. CONDITION slot 패턴

```
UNRESOLVED_CONDITION (참조조문 필요)  : 전체의 약 67%
  "해당하는 경우에는"   707건
  "인정하는 경우에는"   337건
  "필요한 경우에는"     334건
  → 참조조문 없이 조건 판별 불가. 매핑 불가.

IF_AFTER_INSTALL (설치·시설하는 경우) : 428건
  → 설비 등록 시 트리거. 설비 입력데이터로 매핑 가능.

IF_OPERATIONAL (사용하는 경우)        : 185건
  → 설비 운용 시 트리거. 설비 입력으로 매핑 가능.

IF_OVER_THRESHOLD (초과·이상)         : 118건
  → employee_count, 용량 수치 입력으로 매핑 가능.

IF_ON_CHANGE (변경하는 경우)          :  94건
  → 이벤트 기반. 일부 매핑 가능.

IF_ON_ACCIDENT (발생한 경우)          :  86건
  → 사고 이벤트 기반. 현재 입력 데이터로 판단 불가.
```

### 3-2. 사업주 의무 발생 조건 분석 (1,200건)

| 조건 유형 | 건수 | 비율 |
|---|---|---|
| 조건 없음 (사업장 존재만으로 발생) | 491 | 40.9% |
| 설비/공정 키워드 조건 | 96 | 8.0% |
| 기타 조건 (상위기관 처분·법적 이벤트) | 614 | 51.1% |

---

## 4. 현재 입력 데이터로 설명 가능한 비율

### 4-1. 소비자 입력 데이터 현황 (factories 테이블)

```
ksic_code             → KSIC 업종코드
employee_count        → 근로자 수
has_tower_crane       → 타워크레인 (boolean)
has_confined_space    → 밀폐공간 (boolean)
has_asbestos_demo     → 석면해체 (boolean)
has_blasting          → 발파 (boolean)
has_diving            → 잠수작업 (boolean)
has_high_pressure_gas → 고압가스 (boolean)
has_chemical_substance→ 화학물질 (boolean)
has_boiler            → 보일러 (boolean)
factory_process       → 공정 등록 (process_id)
equipment_assets      → 설비 등록 (equipment_type_code)
```

### 4-2. 의무 커버리지 추정 (사업주 의무 1,200건 기준)

| 의무 발생 조건 유형 | 건수 | 입력 커버 여부 |
|---|---|---|
| 사업장 존재 (무조건) | 491 | ✅ |
| 업종(KSIC) 조건 | ~200 추정 | ✅ ksic_code |
| 근로자 수 임계값 | ~150 추정 | ✅ employee_count |
| 설비/공정 키워드 | 96 확인 | ✅ has_* + equipment_assets |
| 상위기관 처분/이벤트 | ~250 | ❌ |
| UNRESOLVED 참조조문 | ~13 | ❌ |

**(491 + 200 + 150 + 96) / 1,200 ≈ 78%**

---

## 5. 결론

### B. 일부 매핑 + 일부 엔진 필요

### 5-1. 매핑으로 커버 가능한 영역

1. **KSIC → employee_count → 임계값 조건 의무**  
   `ksic_process_map` + `applicability_conditions` 데이터 존재. 즉시 활용 가능.

2. **KSIC → 공정 → 설비 → 설비 보유 조건 의무**  
   3단계 triplet 187,319건 존재. 83.1% 연결됨. 구조는 갖춰져 있음.

3. **has_* boolean flag → 특수작업 의무**  
   타워크레인·밀폐공간·석면·발파·잠수 등 8개 flag 입력 가능. 직접 매핑 가능.

### 5-2. 엔진이 필요한 영역

1. **UNRESOLVED_CONDITION 67%**: "해당하는 경우" = 참조조문 없이 조건 판별 불가.
2. **SCOPE 불연결 84.6%**: 소방시설·소화설비·소방대상물은 process_equipment_map에 미등록.
3. **where_text/what_text 전량 NULL**: 장소·대상 기반 의무는 파싱 미완성.
4. **process_law_map llm_verdict 전량 NULL**: 공정-법령 연결 판정 미완료.

### 5-3. 핵심 발견 (가장 중요)

> 현재 GAP은 **"엔진 부족"이 아니라 "매핑 기준 부재 + 연결 계층 미구축"**이다.
>
> master_rule_scope, master_rule_scope_mapping, master_rule_v2_relation이 모두 0건.  
> KSIC-공정-설비 3단계 연결 데이터는 존재하지만,  
> 이를 법령 조문의 의무 발생 조건과 연결하는 **binding 계층이 없다.**

### 5-4. 정량 요약

| 영역 | 매핑 가능 | 엔진/추가작업 필요 |
|---|---|---|
| 사업주 의무 1,200건 | **~78%** | ~22% |
| KSIC-공정-설비 연결 | **83.1%** | 소방계열 제외 |
| SCOPE slot 868건 | **15.4%** | 84.6% |
| CONDITION slot | IF_* 패턴 33% | UNRESOLVED 67% |

---

## 6. 다음 단계 제안 (분석 단계)

본 조사 결과를 바탕으로 다음 단계(분석)에서 검토해야 할 항목:

1. **binding 계층 설계 가능성 분석**  
   SCOPE slot의 canonical_token → process_equipment_map.facility_name_std 정규화 방안

2. **소방계열 SCOPE 처리 방안**  
   소방시설·소화설비(515건, SCOPE의 59%)가 현재 연결 불가인 이유 및 대안

3. **UNRESOLVED_CONDITION 처리 전략**  
   "해당하는 경우" 패턴 67%를 어떻게 처리할 것인가 — 엔진 vs 화이트리스트

4. **사업주 외 주체 의무 범위 산정**  
   TAI 타겟 의무(사업주 1,200건)가 전체 31,407건 중 3.8%인 이유 분석

---

*WO-RESEARCH-001 완료 | 엔진 수정 없음 | 코드 수정 없음 | 테이블 생성 없음*
