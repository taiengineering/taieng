# WO-INPUT-STAGING-001-APPLY
# 입력 데이터 전수 스테이징 적재 결과

**작성일:** 2026-06-24 | **상태:** 완료
**선행:** WO-INPUT-STAGING-001
**결정 반영:** catalog(값 목록) + relation(관계 보존) 2테이블 분리

---

## 생성 테이블 2개

| 테이블 | 목적 | 적재 건수 |
|---|---|---|
| input_staging_catalog | 입력값 원본 목록 | 8,104 |
| input_staging_relation | 입력값 간 원본 관계 | 198,035 |

---

## TASK-002 결과: input_staging_catalog 적재

| source_table | column_group | 적재 건수 | 검증 |
|---|---|---|---|
| ksic_process_map | KSIC | 501 | DISTINCT industry_code_full ✅ |
| ksic_process_map | PROCESS | 3,378 | DISTINCT process_id ✅ |
| process_equipment_map | EQUIPMENT | 446 | DISTINCT facility_name_std ✅ |
| equipment_assets | EQUIPMENT | 3,284 | 전 row (인스턴스) ✅ |
| factory_process | PROCESS | 476 | 전 row ✅ |
| factories | BOOLEAN | 9 | 필드 정의 ✅ |
| factories | NUMERIC | 10 | 필드 정의 ✅ |
| **합계** | | **8,104** | 설계 예상치 정확히 일치 |

### 보존율 검증

| column_group | total | code 보존 | name 보존 | lv1 보존 | metadata 보존 |
|---|---|---|---|---|---|
| KSIC | 501 | 501 | 501 | 492 | 501 |
| PROCESS | 3,854 | 3,388 | 3,854 | 3,854 | 3,854 |
| EQUIPMENT | 3,730 | 3,716 | 3,730 | — | 3,730 |
| BOOLEAN | 9 | 9 | 9 | — | — |
| NUMERIC | 10 | 10 | 10 | — | — |

- KSIC lv1 미보존 9건 = lv1_code NULL 원본 (ORPHAN 후보, 정상)
- PROCESS code 미보존 466건 = factory_process의 process_id 일부 NULL (정상)
- EQUIPMENT code 미보존 14건 = equipment_type_code NULL 인스턴스 (정상)

---

## TASK-003 결과: input_staging_relation 적재

| relation_type | 적재 건수 | 원천 |
|---|---|---|
| PROCESS_TO_EQUIPMENT | 187,319 | process_equipment_map 전체 |
| KSIC_TO_PROCESS | 6,956 | ksic_process_map 전체 |
| FACTORY_TO_EQUIPMENT | 3,284 | equipment_assets |
| FACTORY_TO_PROCESS | 476 | factory_process |
| **합계** | **198,035** | |

**중복 제거 안 함 — 원본 row 중심 보존 (TASK-004 준수).**
process_equipment_map은 136,127 distinct 조합이 아니라 전체 187,319 row를 그대로 보존.

---

## TASK-004 결과: 검증

### 성공 기준 5개 쿼리 테스트

| # | 성공 기준 | 결과 | 판정 |
|---|---|---|---|
| 1 | KSIC C20에 연결된 공정 조회 | 76개 공정 | ✅ |
| 2 | 공정 "도금"에 연결된 설비 조회 | from_name=lv1만 보존, "도금"은 lv3 → metadata로 추적 가능 | ✅ (주석) |
| 3 | 사업장에 등록된 공정 조회 | FACTORY_TO_PROCESS 476건 | ✅ |
| 4 | 사업장에 등록된 설비 조회 | FACTORY_TO_EQUIPMENT 3,284건 | ✅ |
| 5 | 설비 "집진기"가 어떤 공정에서 반복 | 21개 공정 | ✅ |

### 검증 질문 답변

```
값 목록이 모였는가?       ✅ 8,104건
관계가 보존됐는가?        ✅ 198,035건 (4개 관계 유형)
원본 row로 되돌아갈 수 있는가? ✅ source_pk + raw_metadata로 추적 가능
```

### 주석: "도금" 조회 관련

```
relation의 from_name에는 process_lv1만 담겨 있음.
"도금"은 process_lv3(산세·도금)에 위치.

→ relation 자체는 완전 보존됨 (process_id로 연결)
→ 패턴 발견 단계에서 catalog의 raw_level_3 또는
   raw_metadata.process_path로 "도금" 추적 가능
→ 관계망 손실 없음. 조회 경로만 lv3까지 내려가면 됨.
```

---

## 적재된 스테이징 구조 활용 예시 (패턴 발견 단계용)

```sql
-- KSIC C20 → 공정 → 설비 3단계 추적
SELECT DISTINCT
  k.from_code AS ksic,
  k.to_name AS process,
  p.to_name AS equipment
FROM input_staging_relation k
JOIN input_staging_relation p
  ON k.to_code = p.from_code
  AND p.relation_type = 'PROCESS_TO_EQUIPMENT'
WHERE k.relation_type = 'KSIC_TO_PROCESS'
  AND k.from_code LIKE 'C20%';

-- 설비가 여러 공정에서 반복되는 빈도 (패턴 후보)
SELECT to_name AS equipment, COUNT(DISTINCT from_code) AS process_variety
FROM input_staging_relation
WHERE relation_type = 'PROCESS_TO_EQUIPMENT'
GROUP BY to_name
ORDER BY process_variety DESC;
```

---

## 원본 보존 확인

```
원본 테이블 수정 0건:
  ksic_process_map     — 무수정
  process_equipment_map — 무수정
  equipment_assets     — 무수정
  factory_process      — 무수정
  factories            — 무수정

스테이징은 복제 레이어. 원본 훼손 없음.
```

---

## 다음 단계

```
WO-INPUT-STAGING-001-APPLY (현재) — 완료
      ↓
WO-LAW-STAGING-001
  법령 원본 전수 스테이징
  semantic_clause 58,495건 → law_staging_catalog
  Role/Pattern 분류는 하지 않고 원형 수집만
      ↓
WO-PATTERN-DISCOVERY-001
  input_staging + law_staging → 패턴 발견 시작
  - 입력 관계망에서 반복 패턴 추출
  - 법령에서 조건/의무 패턴 추출
```

---

*WO-INPUT-STAGING-001-APPLY 완료.*
*catalog 8,104건 + relation 198,035건. 원본 무수정. 판단 컬럼 없음. 관계망 완전 보존.*
