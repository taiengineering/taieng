# WO-CONDITION-SEED-001-APPLY
# condition_mapping_candidate 초기 적재 결과

**작성일:** 2026-06-23 | **상태:** 완료

---

## 성공 기준 체크

| 항목 | 기대 | 실제 | 판정 |
|---|---|---|---|
| CONFIRMED만 적재 | 전체 = CONFIRMED | non_confirmed = 0 | PASS |
| COMMON 사용 | 0 | 0 | PASS |
| condition_code 중복 | 0 | 0 | PASS |
| applicable_sectors NULL | 0 | 0 | PASS |
| DDL-004 제약 위반 | 0 | 0 | PASS |

---

## 산출물 A: 적재 결과표

**총 적재: 77건** (전원 review_status = 'CONFIRMED')

| input_field | 적재건수 | applicable_sectors |
|---|---|---|
| has_chemical_substance | 24 | ['INDUSTRIAL'] |
| has_confined_space | 16 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] |
| has_diving | 14 | ['CONSTRUCTION'] |
| has_asbestos_demo | 7 | ['CONSTRUCTION','BUILDING'] |
| has_high_pressure_gas | 5 | ['INDUSTRIAL','CONSTRUCTION'] 또는 ['CONSTRUCTION'] |
| has_tower_crane | 5 | ['CONSTRUCTION'] |
| has_boiler | 4 | ['INDUSTRIAL','BUILDING'] |
| has_blasting | 2 | ['CONSTRUCTION'] |
| **합계** | **77** | |

---

## 산출물 B: condition_type 분포

| condition_type | 건수 | 비율 |
|---|---|---|
| WORK_ACT | 37 | 48% |
| MATERIAL_ACT | 24 | 31% |
| EQUIPMENT_ACT | 14 | 18% |
| FACILITY_ACT | 2 | 3% |

---

## 산출물 C: Sector 분포

| applicable_sectors | 건수 |
|---|---|
| {INDUSTRIAL} | 24 |
| {CONSTRUCTION} | 24 |
| {INDUSTRIAL,CONSTRUCTION,BUILDING} | 16 |
| {CONSTRUCTION,BUILDING} | 7 |
| {INDUSTRIAL,BUILDING} | 4 |
| {INDUSTRIAL,CONSTRUCTION} | 2 |

**해석:**
- CONSTRUCTION 연관(단독+복합): 24+16+7+2 = 49건 (64%)
- INDUSTRIAL 연관: 24+16+4+2 = 46건 (60%)
- BUILDING 연관: 16+7+4 = 27건 (35%)

---

## 산출물 D: 제외 목록 (28건)

제외 사유 3가지 패턴:
1. **action_text 단편조각** — "착용하도록 하여야 한다"/"포장하여야 한다" 등 도입문 없는 단편
2. **condition_text 단편조각** — "그 장소"/"이 경우"/"이를 사용하는 경우" 등 선행 조문 의존
3. **타겟 불일치** — 채석장특수/잠함굴착 전담/석면·베릴륨 제외 허가대상 등

전체 목록은 WO-CONDITION-SEED-001-REVIEW 참조.

---

## 산출물 E: COMPOUND 후보 (TASK-005)

**WO-CONDITION-COMPOUND-001로 이관. 현재 INSERT 금지.**

| semantic_clause_id | 조번호 | 조문 요약 | 연관 input_field |
|---|---|---|---|
| 80135fef | 532 | 기압조절실 잠수작업자에게 가압 속도 제한 | has_diving OR has_high_pressure_gas |
| 3cba36fb | 535 | 기압조절실 감압 조치 | has_diving OR has_high_pressure_gas |
| 6edd3dd8 | 535 | 기압조절실 감압 시간 고지 | has_diving OR has_high_pressure_gas |

조문 특성: condition_text에 "고압작업자 또는 잠수작업자"로 두 조건 명시.
설계 방향: compound_operator = 'OR', input_field별 독립 condition_code 2개 생성.

---

## 산출물 F: VCF-02 재실행 권고

**즉시 실행 권장.**

### 검증 핵심 질문

> "77건이 적재된 상태에서 VCF-02 사업장별 의무후보 수가 어떻게 바뀌는가?"

### 예상 시나리오

| 그룹 | 예상 변화 | 확인 포인트 |
|---|---|---|
| Golden Pair (has_*=true) | 해당 has_*별 의무 발생 | has_confined_space → 16건, has_tower_crane → 5건 등 |
| Process Only (has_* 없음) | 0건 유지 | condition_mapping 없으므로 미발생 = 정상 |
| Work Only (has_* 있음) | has_*별 의무 발생 | Golden Pair와 동일 경로 확인 |
| Equipment Ambiguity | has_* 보유 시 발생 | 설비코드 단독으로는 미발생 확인 |

### 성공 지표

- has_confined_space=true 사업장 → 16건 의무 발생
- has_tower_crane=true 사업장 → 5건 의무 발생
- has_* 전부 false 사업장 → condition_mapping 경로 의무 0건

---

## 다음 단계 순서

1. **VCF-02 재실행** — 77건 적재 후 의무발생량 비교
2. **WO-CONDITION-COMPOUND-001** — COMPOUND 3건 설계
3. **WO-CONDITION-SEED-002** — THRESHOLD / appendix_condition 매핑 설계
4. **WO-CONDITION-VERIFY-001** — VCF-02 조회 결과 분석
5. **WO-CONDITION-VERIFY-002** — VCF-01 현실사업장 결과 분석

---

*WO-CONDITION-SEED-001-APPLY 완료. 77건 CONFIRMED 적재 성공. 실패/경고 0.*
