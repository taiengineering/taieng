# WO-INPUT-STAGING-002
# 미수집 입력원천 추가 적재 결과

**작성일:** 2026-06-24 | **상태:** 완료
**선행:** WO-INPUT-COVERAGE-AUDIT-001
**핵심:** Layer A(선택지 풀) / Layer B(입력 필드 마스터) 분리 적재

---

## 산출물 A: 추가 적재 대상 목록

| 원천 테이블 | source_column_group | Layer | 적재 건수 |
|---|---|---|---|
| diagnosis_input_fields | FIELD_MASTER | **B** | 128 |
| master_dangerous_goods | MATERIAL_POOL | A | 49 |
| master_highpressure_gas | MATERIAL_POOL | A | 25 |
| master_products_elec | EQUIPMENT_POOL | A | 122 |
| master_safety_certification | CERT_POOL | A | 50 |
| kcsc_work_master | CONSTRUCTION_WORK | A | 243 |
| kcsc_process_master | CONSTRUCTION_PROCESS | A | 161 |
| **신규 합계** | | | **778** |

---

## 산출물 B: Layer A / Layer B 구분

```
Layer B: 입력 필드 마스터 (FIELD_MASTER) — 128건
  diagnosis_input_fields
  = 사용자가 실제 진단 시 입력하는 질문/필드
  = 법령 매핑의 실제 단위
  raw_metadata.source_layer = 'FIELD_MASTER'

Layer A: 선택지 풀 (OPTION_POOL) — 650건 신규 + 기존 8,104
  위험물·고압가스·전기설비·인증·건설작업·건설공정
  = 입력 필드가 참조하는 선택지/코드 풀
  raw_metadata.source_layer = 'OPTION_POOL'

구분 방식:
  raw_metadata->>'source_layer' 로 조회 가능
  기존 8,104건(STAGING-001)은 source_layer NULL → 추후 보정 가능
```

### catalog 전체 구성 (8,882건)

| source_column_group | layer | 건수 |
|---|---|---|
| PROCESS | (기존) | 3,854 |
| EQUIPMENT | (기존) | 3,730 |
| KSIC | (기존) | 501 |
| NUMERIC | (기존) | 10 |
| BOOLEAN | (기존) | 9 |
| **FIELD_MASTER** | **B** | **128** |
| CONSTRUCTION_WORK | A | 243 |
| CONSTRUCTION_PROCESS | A | 161 |
| EQUIPMENT_POOL | A | 122 |
| MATERIAL_POOL | A | 74 |
| CERT_POOL | A | 50 |
| **합계** | | **8,882** |

---

## 산출물 C: catalog 추가 적재 결과

```
적재 전: 8,104건
적재 후: 8,882건
신규:    778건

배치 구분:
  STAGING-2026-06-24-B: FIELD_MASTER 128건 (Layer B)
  STAGING-2026-06-24-A: OPTION_POOL 650건 (Layer A)
```

### 원문 컬럼 보존 (해석 없이 raw_metadata)

```
위험물:    hazard_class, designated_qty, designated_unit, storage_standard, legal_basis
고압가스:  storage_limit, processing_limit, manager_required, legal_basis
전기설비:  rated_voltage, rated_current, rated_kva, rated_kw, phase_type
인증:      cert_type, issuing_agency, inspection_cycle, legal_basis
건설작업:  hazard_type, is_hazardous, safety_standard, equipment_type_codes
건설공정:  work_type_code, risk_level, full_code
```

---

## 산출물 D: relation 추가 적재 결과

| relation_type | 건수 | 원본 근거 |
|---|---|---|
| CONSTRUCTION_WORK_TO_PROCESS | 243 | kcsc_work_master.process_id (전부 채워짐) |

```
relation 적재 전: 198,035건
relation 적재 후: 198,278건
신규: 243건

추론 관계 생성 안 함 — process_id 원본이 명확한 것만 적재.
```

**미적재 관계 (원본 불명확 — 추론 금지 원칙):**
```
FIELD_TO_OPTION_POOL       → field와 option 연결이 코드로 명시 안 됨. 보류.
DANGEROUS_GOODS_TO_THRESHOLD → 단일 테이블 내부 속성. 관계 아님. 보류.
ELECTRIC_PRODUCT_TO_CAPACITY → 단일 테이블 내부 속성. 관계 아님. 보류.
```

---

## 산출물 E: 남은 미수집 원천 목록

| 원천 | row | 상태 | 사유 |
|---|---|---|---|
| master_safety_manager_criteria | 19 | 보류 | THRESHOLD 원천 — 법령측 성격, 입력 아닐 수 있음 |
| master_fields | 118 | 보류 | diagnosis_input_fields와 중복 가능 — 대조 필요 |
| industry_master | 501 | 보류 | KSIC와 중복 가능 — 대조 필요 |
| master_legal_inspection_target | 13 | 보류 | 법정점검 대상 — 법령측 |
| buildings / sites | 1/4 | 데이터 없음 | 거의 빔 |
| equipment_model_master | 0 | 데이터 없음 | 빈 테이블 |

---

## 산출물 F: 다음 작업 제안

```
WO-INPUT-STAGING-002 (현재) — 완료
      ↓
WO-INPUT-LANDSCAPE-002
  Layer A(선택지 풀) vs Layer B(입력 양식) 관계 지형도
  - 128개 입력필드가 각각 어느 OPTION_POOL을 참조하는가
  - sector별 입력필드 분포 (BUILDING 37 / CONSTRUCTION 15 / INDUSTRIAL 17)
  - 제조공정(KSIC) vs 건설공정(KCSC) 분리 확인
      ↓
WO-INPUT-PATTERN-DISCOVERY-001
  레이어 B(128 field) 기준 패턴 발견
```

---

## 완료 기준 답변 (TASK-007 검증)

| 검증 질문 | 결과 |
|---|---|
| 진단 입력필드 128개 모두 들어갔는가? | ✅ FIELD_MASTER 128 |
| 위험물 선택지 49개 들어갔는가? | ✅ master_dangerous_goods 49 |
| 고압가스 선택지 25개 들어갔는가? | ✅ master_highpressure_gas 25 |
| 전기설비 선택지 122개 들어갔는가? | ✅ master_products_elec 122 |
| 건설표준 작업/공정 들어갔는가? | ✅ WORK 243 + PROCESS 161 |
| Layer A/B 구분 가능한가? | ✅ raw_metadata.source_layer |
| 제조공정 vs 건설공정 source_table 구분? | ✅ ksic_process_map vs kcsc_* |

---

## 핵심 성과

```
이제 입력세계가 두 레이어로 정리됨:

Layer B (입력 양식, 128개):
  사용자가 실제 입력하는 필드
  → 다음 패턴 발견의 시작점

Layer A (선택지 풀, 8,754개):
  KSIC 501 + 제조공정 3,378 + 설비 446+3,284
  + 위험물 49 + 고압가스 25 + 전기 122 + 인증 50
  + 건설작업 243 + 건설공정 161
  → Layer B 필드의 참조 풀

건설(KCSC)과 제조(KSIC)가 source_table로 완전 분리됨.
위험물·고압가스·전기·인증 입력축 전부 확보됨.
```

---

*WO-INPUT-STAGING-002 완료.*
*catalog 8,882건 (신규 778) / relation 198,278건 (신규 243).*
*Layer A/B 분리. 건설·위험물·전기·인증 입력축 확보. 입력세계 수집 완료에 근접.*
