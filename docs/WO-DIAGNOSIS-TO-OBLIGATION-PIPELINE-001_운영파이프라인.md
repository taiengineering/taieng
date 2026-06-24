# WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001
# 진단 입력 → 의무생성기 운영 파이프라인 정의

**작성일:** 2026-06-24 | **상태:** 완료 (데이터 흐름 정의, 읽기 전용)
**선행:** WO-EXISTS-INPUT-TRACE-001
**금지 (전부 준수):** 새 법령분석/Trigger/Harvest/Review 없음. 데이터 흐름만.
**목적:** 진단 입력(has_*)이 obligation_generator까지 도달하는 파이프라인 정의.

> 법령 엔진 문제가 아니라 "입력 시스템 ↔ 의무 생성기" 통합 문제.

---

## 결론 먼저

```
세 진단 경로가 모두 facility_profiles(generator 소스)와 단절.

  경로1 anonymous_diagnosis_results (171건, 주 경로)
    → factory_id 보유(153) 그러나 facility_profiles와 공유 0건
    → has_* 미수집 (sector+숫자만)

  경로2 public_diagnosis_requests (14건)
    → has_* 일부 보유(has_elevator/has_gas/has_hazardous)
    → factory_id 없음 (biz_no만) → facility_profiles 연결 불가

  경로3 factory_diagnosis_results (4건)
    → has_* 미수집

generator가 읽는 facility_profiles ← 어느 경로와도 연결 안 됨.

→ 단절이 1개가 아니라 구조적. 진단 입력과 generator가 분리된 세계.
→ 게다가 EXISTS(has_welding 등 핵심)는 어느 경로도 수집 안 함.
```

---

## TASK-001: 실제 운영 파이프라인 (실측)

```
[진단 UI 입력]
   │
   ├─ 경로1 (주): anonymous_diagnosis_results.input_data
   │    {sector, ksic_code, factory_id, floor_area, worker_count}
   │    has_* 없음. 171건.
   │
   ├─ 경로2: public_diagnosis_requests.facility_data
   │    {has_elevator, has_gas, has_hazardous, floor_area, worker_count}
   │    has_* 일부. 14건. factory_id 없음(biz_no만).
   │
   └─ 경로3: factory_diagnosis_results.input_data
        has_* 없음. 4건.

        ✗✗✗ 단절 ✗✗✗  (어느 경로도 facility_profiles로 안 흐름)

[facility_profiles.profile_snapshot]  ← generator가 읽는 곳
   {sector, ksic, workforce, building, metrics}
   has_* 없음. factory_id가 진단 경로와 다름(공유 0).
   │
[obligation_generator]
   │
[obligation_instance]  → 0건
```

---

## TASK-002: public_diagnosis_requests ↔ generator 동의어 표

```
EXISTS 매핑:
  has_elevator    → has_elevator           (DIRECT_MATCH)
  has_gas         → has_high_pressure_gas  (NEEDS_MAP)
  has_hazardous   → has_hazardous_material (NEEDS_MAP)

NUMERIC 매핑 (THRESHOLD용):
  worker_count       → worker_count (total_workers)
  total_floor_area   → building_area (floor_area)
  floor_area         → building_area
  electric_capacity  → electrical_kw
  electric_kw        → electrical_kw
  subcon_workers     → subcontract_workers
  contract_eok       → construction_amount (억원 단위)
  project_amount     → construction_amount
  basement_count     → (지하층수, cmc 미사용)
  built_year         → (건축년도, cmc 미사용)
  main_structure     → (구조, cmc 미사용)
  building_use       → use_code

★ 핵심 한계:
  public_diagnosis_requests에 실제 있는 EXISTS는 3개뿐.
  has_welding/has_crane/has_excavation 등 핵심 작업·설비는
  이 경로에도 없음 (building/special 섹터 소수 필드만).
```

---

## TASK-003: Generator Input Contract v1 (병합)

```json
{
  "factory_id": "...",
  "sector": "...",          // 우선순위: facility_profiles → 진단입력
  "ksic_code": "...",

  // THRESHOLD (양쪽 다 있음, COALESCE)
  "worker_count": null,     // total_workers_value ?? worker_count
  "building_area": null,    // floor_area_value ?? total_floor_area ?? floor_area
  "electrical_kw": null,    // electrical_kw_value ?? electric_capacity ?? electric_kw
  "gas_capacity": null,     // gas_capacity_value
  "construction_amount": null, // construction_amount_value ?? contract_eok ?? project_amount

  // EXISTS (현재 거의 빈 상태 — 동의어 변환 후)
  "has_elevator": false,    // ← has_elevator
  "has_high_pressure_gas": false, // ← has_gas
  "has_hazardous_material": false // ← has_hazardous
  // has_welding 등 핵심 28개: 어느 경로도 미수집
}
```

```
병합 규칙:
  소스 A facility_profiles (SCOPE + THRESHOLD 풍부)
  소스 B public_diagnosis_requests (EXISTS 일부)
  → 동의어 정규화 후 COALESCE 병합.
  → 단 두 소스가 factory_id 공유 안 함이 근본 문제.
```

---

## TASK-004: facility_profiles 역할 재정의

```
질문: facility_profiles는 영구 마스터인가, 진단 입력 저장소인가?

실측 판정: "영구 마스터(시설 프로필)"이다.

근거:
  - profile_version 컬럼 (버전 관리)
  - *_state/*_value/*_provenance (입력/추론/API 출처 추적)
  - 진단 경로의 factory_id와 공유 0 → 진단이 직접 안 씀

→ facility_profiles = 사업장의 정규화된 영구 프로필.
→ 진단 입력(anonymous 등)은 별도 임시 저장.
→ generator가 마스터를 읽는 건 맞으나,
  진단 입력이 마스터로 흘러들지 않음 = 단절.

함의:
  진단 입력 → facility_profiles 동기화(승격) 단계가 없음.
  또는 generator가 진단 입력을 직접 읽어야 함.
```

---

## TASK-005: 최종 연결 전략 비교

```
CASE-1: public_diagnosis_requests 직접 읽기
  장점: has_* 일부 즉시 도달.
  단점: 14건뿐, factory_id 없음(biz_no), 주 경로 아님.
  → 부분 해결. EXISTS 3개만.

CASE-2: facility_profiles 동기화
  장점: generator 소스 그대로, 마스터 일원화.
  단점: 진단 입력 → facility_profiles 승격 로직 신규 필요.
       has_* 컬럼이 profile_snapshot에 없음 → 구조 확장 필요.
  → 정석이나 작업량 큼.

CASE-3: Input Contract Builder 계층 추가  ★권장
  장점: 여러 소스(facility_profiles + 진단입력) 병합.
       generator는 Contract만 받음 (소스 무관).
       동의어 변환을 Builder가 흡수.
  단점: Builder 계층 신규 구현.
  → 가장 유연. 소스 단절을 Builder가 다리 놓음.

비교 결론:
  근본 문제 = 진단입력과 마스터의 factory_id 단절 + has_* 미수집.
  CASE-3가 단절을 우회하나, has_* 미수집은 별도 문제.
```

---

## 가장 중요한 발견: 두 개의 독립된 문제

```
문제 A: 저장소 단절 (파이프라인)
  진단 입력 ↔ facility_profiles factory_id 공유 0.
  → Input Contract Builder(CASE-3)로 다리 놓을 수 있음.

문제 B: EXISTS 미수집 (입력 설계)
  has_welding/has_crane 등 핵심 28개를
  어느 진단 경로도 수집 안 함.
  → Builder를 만들어도 채울 has_* 자체가 없음.
  → 진단 UI/입력 플로우가 작업·설비를 물어야 함.

→ A를 풀어도 B가 남음.
→ 현재 generator로 의미있는 출력을 내려면:
  (1) UNIVERSAL(sector만) — has_* 불필요
  (2) THRESHOLD(숫자) — 양쪽 경로 다 있음
  이 둘이 has_* 없이 작동하는 유일한 경로.
```

---

## TASK-006: 구현 우선순위 (Cursor/GPT 최소 수정)

```
즉시 (has_* 없이 작동, 데이터 이미 있음):
  P1. UNIVERSAL 310 CONFIRMED 승격 (REVIEW)
      → sector만으로 baseline 생성. 진단 입력에 sector는 항상 있음.
  P2. THRESHOLD 매핑 보강
      → worker_count/floor_area는 모든 경로에 있음.
      → cmc에 THRESHOLD 규칙 추가 (worker≥50 등).

파이프라인 (Cursor/GPT 영역):
  P3. Input Contract Builder 구현 (CASE-3)
      → 소스 병합 + 동의어 변환.
      → 최소 수정: services/에 builder 1개 추가.
      → generator가 facility_profiles 대신 Builder 호출.

입력 설계 (별도 트랙):
  P4. 진단 UI에 EXISTS(has_*) 수집 추가
      → 작업·설비 질문을 진단 플로우에 포함.
      → diagnosis_input_fields 59 boolean이 실제 입력되게.
```

---

## 성공 기준 답변

```
has_welding=true → generator.has_welding=true → obligation_instance
까지의 데이터 경로를 100% 설명할 수 있는가?

✅ 설명 가능 (단, 현재는 단절 상태):

이상적 경로 (CASE-3 구현 후):
  진단 UI (has_welding 입력)
    → [수집 저장소] (현재 미수집 — P4 필요)
    → Input Contract Builder (소스 병합 + 동의어)
    → generator.has_welding=true
    → cmc CONFIRMED 매칭 (WORK_ACT:WELDING 18개)
    → obligation_instance 18건

현재 단절 지점 2개:
  (A) 진단입력 ↔ facility_profiles 미연결 → Builder로 해결
  (B) has_welding 자체 미수집 → 진단 UI 확장 필요
```

---

## 현재 위치 (수정)

```
매핑 완료 / 생성기 완료 / 바인딩 규격 완료 / 입력추적 완료
  ↓
파이프라인 정의 완료 ← 지금 (단절 2개 + 우회로 확인)
  ↓
분기:
  트랙1 (즉시): UNIVERSAL+THRESHOLD로 has_* 없이 진단
  트랙2 (파이프): Input Contract Builder (Cursor/GPT)
  트랙3 (입력): 진단 UI에 EXISTS 수집
```

---

## 권고

```
지금 가장 빠른 "살아있는 진단":
  has_* 단절을 우회 → UNIVERSAL + THRESHOLD 경로.

  P1 UNIVERSAL 승격 → sector baseline (즉시, 데이터 있음)
  P2 THRESHOLD 보강 → 숫자 기반 의무 (즉시, 데이터 있음)

  → has_* 파이프(Builder)와 입력(UI)은 그 다음.
  → 이렇게 하면 "0건"이 아닌 실제 의무가 즉시 나옴.
  → EXISTS는 입력 수집 갖춰진 후 추가.
```

---

*WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001 완료. 데이터 흐름 정의.*
*핵심: 단절 2개 — (A)진단입력↔마스터 factory_id 공유 0, (B)has_* 미수집.*
*facility_profiles=영구마스터. Input Contract Builder(CASE-3) 권장.*
*즉시 우회: UNIVERSAL+THRESHOLD는 has_* 없이 작동(데이터 이미 존재).*
