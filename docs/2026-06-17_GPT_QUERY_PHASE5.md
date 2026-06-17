# GPT 질의 — Phase 5 WO 설계 요청

**작성일**: 2026-06-17  
**용도**: Phase 4 관찰 완료 후 GPT에게 전달

---

## 한 문장 요약

> Phase 4에서 INDUSTRIAL 안전관리자 판정이 10/10 정확함을 확인했다.
> Phase 5는 CONSTRUCTION과 BUILDING으로 확장할지, 아니면 다른 방향인지 판단이 필요하다.

---

## Phase 1~4 완료 현황

| Phase | 내용 | 상태 |
|---|---|---|
| Phase 1 | FacilityProfile (TriValue + Provenance) | ✅ |
| Phase 2 | ApplicabilityCondition 파일럿 (7건) | ✅ |
| Phase 3 | Condition Scope Layer (INDUSTRY IN/NOT_IN) | ✅ |
| Phase 4 | Real Facility Validation 관찰 | ✅ INDUSTRIAL 10/10 OK |

---

## Phase 4 관찰 결과

**INDUSTRIAL 10개: 전부 OK**

| 케이스 | 업종 | 인원 | 기대 | 실제 |
|---|---|---|---|---|
| I-01 | C28 | 280명 | REQUIRED 1명 | REQUIRED 1명 |
| I-02 | C10 | 600명 | REQUIRED 2명 | REQUIRED 2명 |
| I-03 | C20 | 150명 | REQUIRED 1명 | REQUIRED 1명 |
| I-04 | H49 | 80명 | REQUIRED 1명 | REQUIRED 1명 |
| I-05 | C24 | 30명 | NOT_REQUIRED | NOT_REQUIRED |
| I-06 | C26 | 50명 | REQUIRED 1명 | REQUIRED 1명 |
| I-07 | D35 | 200명 | REQUIRED 1명 | REQUIRED 1명 |
| I-08 | C11 | 40명 | NOT_REQUIRED | NOT_REQUIRED |
| I-09 | null | 100명 | UNKNOWN | UNKNOWN |
| I-10 | C19 | 1200명 | REQUIRED 2명 | REQUIRED 2명 |

**CONSTRUCTION/BUILDING: NO_RELEVANT_CONDITION (정상)**

---

## Scope Coverage 현황

| scope_type | 소비자 입력 필드 | 현재 지원 |
|---|---|---|
| INDUSTRY | ksic_major | ✅ INDUSTRIAL |
| METRIC:EMPLOYEE_COUNT | worker_count | ✅ |
| ACTIVITY | has_blasting/diving/confined_space | ❌ |
| EQUIP | equipment_list | ❌ |
| BLDG | building_use_type | ❌ |
| METRIC:CONSTRUCTION_AMT | contract_amount_eok | ❌ |

---

## 질문 1. Phase 5 방향

- A: CONSTRUCTION Scope 구현
- B: BUILDING Scope 구현
- C: INDUSTRIAL Obligation 생성 (소비자에게 문장 표시)
- D: Track A vs V4 병렬 비교 관찰
- E: 다른 법령군 확장 (보건관리자 등)

### 질문 2. Obligation 생성 시점

현재 `required_count`만 반환. 소비자에게 문장으로 보여주려면 Obligation 객체 필요한가?

### 질문 3. CONSTRUCTION Scope 설계

공사금액 기준 안전관리자:
```
METRIC:CONSTRUCTION_AMT >= 120억 → 1명
METRIC:CONSTRUCTION_AMT >= 800억 → 2명
```
이 방향이 맞는가? sector 기반 분기는 필요한가?

### 질문 4. BUILDING Scope 설계

BUILDING은 산안법이 아닌 다른 법령(소방시설법, 승강기안전관리법 등)이 적용됨.
Phase 5에서 BUILDING을 다루려면 새로운 법령 Appendix 수집이 선행되어야 하는가?

### 질문 5. Phase 5 완료 정의

- A: CONSTRUCTION 안전관리자 공사금액 기준 판정
- B: INDUSTRIAL + CONSTRUCTION 동시 정확
- C: V4 결과가 소비자에게 문장으로 표시
- D: Track A vs V4 비교

---

## 절대 금지

```
Track A 수정
GPT 전속 테이블 수정
CONSTRUCTION/BUILDING Scope 무단 구현 (기획서 판단 전)
obligation_result 생성 (GPT 판단 전)
pilot_safety_manager_api 삭제
```
