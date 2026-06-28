# WO-APPLICABILITY-IMPACT-001 — facility_profiles 생성 효과 검증

**작성일:** 2026-06-28 | **성격:** 읽기 전용 분석. **판정: 현 엔진 기준 효과 0 — "profiles → Applicability 개선" 가설 불성립.**

> 핵심(코드 증명): Applicability 엔진은 `facility_profiles`를 읽지 않고 `factories`를 직접 읽는다. 따라서 profiles 100개 생성은 Applicability MISSING_DATA를 바꾸지 못한다(before = after). 500 확대는 Applicability 개선 목적이라면 무의미.

---

## TASK-001/002 — Applicability 실행 전 코드 확인 (실행 불가·불요 판명)
`scripts/run_facility_applicability.py` 직독 결과, 엔진의 입력은 `factories` 컬럼이다:
```sql
SELECT id, employee_count, electrical_capacity_kw, transformer_capacity_kva,
       building_area, gas_capacity_m3, gas_capacity_kg, construction_amount,
       site_type, ksic_code, name
FROM factories WHERE is_active = true
```
- `facility_profiles` 참조 **없음**. `evaluate_draft_for_facility(fac, …)`의 `fac`는 factories row.
- 실행 방식: `railway run python3 scripts/run_facility_applicability.py` (Railway 환경, DATABASE_URL 필요) → Claude 실행 불가.
- 동작: `TRUNCATE facility_applicability …` 후 **전 active 시설 전수 재평가**(코호트 단위 불가).

## TASK-003 — MISSING_DATA 감소량
```
Before(현재)  facility_applicability MISSING_DATA 비율: 섹터별 78~96.5% (WO-FACILITY-DATA-COVERAGE-001)
After(profiles 100 생성 후)  엔진이 profiles 미참조 → 재평가해도 동일 입력(factories) → 동일 결과
개선률  0% (구조적으로 변화 없음)
```
profiles는 factories 값을 미러링(복사)할 뿐이라, 엔진이 factories를 읽는 한 새 정보가 없다.

## TASK-004 — 새 APPLICABLE 조항 수
```
추가 APPLICABLE: 0 (엔진 입력 불변)
```

## TASK-005 — 글 읽기 검증
해당 없음(증가분 0). 대신 인과 검증: 엔진 SELECT 문에 `facility_profiles` 부재를 코드로 확인 = profiles가 평가에 진입하지 못함.

## MISSING_DATA의 실제 원인 (factories 컬럼 결측)
엔진이 읽는 factories 컬럼의 결측률(WO-FACILITY-DATA-COVERAGE-001):
```
building_area            87.8% 결측
electrical_capacity_kw   87.5% 결측
site_type                90.0% 결측
gas_capacity_m3/kg       대부분 결측
transformer_capacity_kva 대부분 결측
(반면 employee/ksic/construction_amount/sector 는 양호)
→ MISSING_DATA의 원인은 이들 factories 컬럼이 비어 있기 때문. profiles 생성과 무관.
```

## TASK-006 — P1 확대 여부 판정
```
조건: MISSING_DATA 충분히 감소 → ✗ (감소 0)
∴ "Applicability 개선" 목적의 500 확대: 보류/불승인 (현 엔진 기준 효과 없음).
※ profiles 확대는 "장차 엔진이 profiles를 입력으로 채택할 때"를 대비한 입력계층 준비 목적일 때만 의미.
```

## 의사결정 재정렬 (정직 보고)
```
- WO-FACILITY-PROFILE-BATCH-001(profiles 100)은 생성·검증 자체는 PASS였으나,
  현 Applicability 엔진은 profiles를 소비하지 않으므로 상위 엔진 품질에 영향 0.
- "500개 더 만들까?"의 답: 지금은 아님. 먼저 둘 중 하나를 결정해야 함:
   (A) factories 희소 컬럼(building_area·electrical·gas·transformer·site_type) 데이터 확보
       → MISSING_DATA를 실제로 줄이는 유일한 본질적 레버(데이터 취득 문제).
   (B) 엔진이 facility_profiles를 입력으로 읽도록 변경(GPT/엔진 영역)
       → 단 profiles는 factories 미러링이라 새 데이터가 생기지 않음. 결국 (A)가 본질.
- 따라서 다음 우선순위 권고: profiles 확대가 아니라 "factories 속성 데이터 확보 경로" 설계.
  (예: 건축물대장/공공데이터 연계로 building_area·floor·use 등 보강 — 별도 WO)
```

## Boundary 준수
```
읽기 전용. INSERT/UPDATE/DELETE 0. Applicability/Check/Diagnosis/Engine 미수정·미실행.
엔진 실행은 railway 전용+전수 TRUNCATE 재평가라 코호트 측정 부적합 → 코드 인과 분석으로 대체.
```

*WO-APPLICABILITY-IMPACT-001 — 현 엔진은 factories만 읽고 facility_profiles 미참조 → profiles 생성은 Applicability에 효과 0. 500 확대 보류. 본질 레버 = factories 희소 컬럼 데이터 확보(별도 WO 권고).*
