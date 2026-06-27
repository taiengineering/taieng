# WO-FACILITY-DATA-COVERAGE-001 — Applicability 입력 데이터 가용성 진단 (STEP 0)

**작성일:** 2026-06-27 | **성격:** 읽기 전용 전수 집계(샘플링·추정·INSERT/UPDATE 0). **판정: PASS** — 4대 질문 수치 응답.
**데이터 기준:** factories 5,812 (운영 DB, project vwlahtguyggrhvslabax).

---

## 최종 4대 질문 — 숫자 응답
```
Q. 즉시 obligation_instance 생성 가능 시설?   5,400 (92.9%)  ← sector+ksic+employee 완비(A티어)
   (UNIVERSAL 전 시설 가능: sector 100% → 5,812)
Q. 왜 나머지 생성 불가?                        sector·코어는 충분(병목 아님).
                                              EXISTS/상세의무가 막힘 = 건물/설비 상세속성 희소.
Q. 가장 큰 병목 데이터?                        facility_profiles 미생성(2/5,812) +
                                              상세속성(건물용도 95.5%·층수 91.4%·산업 has_* 98% NULL).
Q. P1 안전 시작 범위?                          UNIVERSAL + worker-THRESHOLD = 5,400 시설 즉시.
                                              건설 EXISTS = 건설 5,000+ (건설 has_* 96% 보유).
                                              산업/건물 EXISTS = 제한적(속성 희소).
```

## TASK-001 — 모집단
```
총 시설        5,812
활성(is_active) 5,457
sector 존재율   100.0% (5,812)   ← C티어(평가불가) 0
KSIC 존재율     92.9% (5,401)
섹터 분포: CONSTRUCTION 5,238(90.1%) / BUILDING 291(5.0%) / INDUSTRIAL 282(4.9%) / SPECIAL 1
```

## TASK-002 — 핵심 입력 Coverage (존재율 / NULL율)
```
sector                100.0%  / 0.0%     ★완비
employee_count         99.98% / 0.02%    ★완비
total_worker_count_calc100.0% / 0.0%     ★완비
ksic_code              92.9%  / 7.1%
construction_amount    92.4%  / 7.6%
construction_type      88.0%  / 12.0%
electrical_capacity_kw 12.5%  / 87.5%    ▽희소
building_area          12.2%  / 87.8%    ▽희소
site_type              10.0%  / 90.0%    ▽희소
floor_count             8.6%  / 91.4%    ▽희소
building_use_code       4.5%  / 95.5%    ▽▽희소
contractor_count        0.4%  / 99.6%    ▽▽▽거의 없음
```

## TASK-003 — has_* 계열 전수 (TRUE / FALSE / NULL)
```
[건설계열 — 잘 입력됨, NULL 699(12%)]
has_tower_crane     T1827 F3286 N699
has_confined_space  T1551 F3562 N699
has_asbestos_demo   T1073 F4040 N699
has_blasting        T 764 F4349 N699
has_diving          T 266 F4847 N699
[산업계열 — 거의 미입력, NULL ~98%]
has_safety_manager      T  62 F   1 N5749
has_chemical_substance  T  34 F  81 N5697
has_boiler              T  24 F  90 N5698
has_high_pressure_gas   T  19 F  95 N5698
[기타 boolean — 입력됨]
hazardous_material   T115 F5692 N5
is_hazardous_material T 12 F5800 N0
```

## TASK-004 — facility_profiles 생성 가능성 (A/B/C)
```
A 즉시 가능(sector+ksic+employee 완비)   5,400  92.9%
B 보완 후 가능(sector 有, ksic/emp 일부 부족) 412   7.1%
C 생성 불가(sector 無)                        0   0.0%
```

## TASK-005 — Applicability 실행 가능성 (섹터 × 실제 평가상태, 전수 join)
```
sector        factories  fa보유  fa행      평가가능(MATCH+POSSIBLE)  MISSING_DATA  MISSING%
CONSTRUCTION    5,238    5,108  3,769,704      101,671            3,637,075     96.5%
BUILDING          291      112     82,656       16,034               64,598     78.2%
INDUSTRIAL        282      123     90,774       17,727               71,062     78.3%
SPECIAL             1        1        738          150                  480     65.0%
```
→ 코어 충분에도 평가행의 78~96.5%가 MISSING_DATA. 원인: 평가가 다수 조항파트(건물/설비 상세)를 요구하나 해당 속성이 희소.

## TASK-006 — obligation_instance 생성 가능성 예측 (생성 안 함, 예측만)
```
A 시설(5,400): UNIVERSAL(섹터결정적) + worker-THRESHOLD(employee 100%) → 즉시 생성 가능
B 시설(412)  : ksic/employee 보완 후 가능
C 시설(0)    : 해당 없음
EXISTS 의무(설비/건물 플래그 의존) 추가 가능성:
  - CONSTRUCTION(5,238): 건설 has_* 96% 보유 → 건설 EXISTS 생성 가능
  - INDUSTRIAL(282)   : 산업 has_* ~21%(59건)만 보유 → 산업 EXISTS 제한적
  - BUILDING(291)     : 건물 상세 일부(building_area 98%) 有, has_* 희소 → 부분
```

## TASK-007 — Coverage Dashboard
```
시설 5,812
├─ A 즉시 가능        5,400   92.9%   (UNIVERSAL + worker-THRESHOLD)
├─ B 보완 후 가능       412    7.1%   (주로 ksic 보완)
└─ C 불가                0    0.0%
세부 의무유형 생성 가능 범위:
  UNIVERSAL           5,812  100%   (sector만 필요)
  worker-THRESHOLD    5,811   ~100% (employee_count)
  건설 EXISTS        ~5,000   건설 has_* 96%
  산업 EXISTS           ~60   산업 has_* 21%
```

## TASK-008 — 병목 자동 분석 (missing 순위)
```
1. facility_profiles 미생성        5,810/5,812 (99.97%)  ← 구조적 1차 병목
2. contractor_count                5,789 (99.6%)
3. 산업 has_*(chemical/boiler/gas)  ~5,698 (98%) [산업섹터 한정 영향]
4. building_use_code               5,549 (95.5%)
5. floor_count                     5,311 (91.4%)
6. site_type                       5,234 (90.1%)
7. building_area                   5,105 (87.8%)
8. electrical_capacity_kw          5,087 (87.5%)
9. construction_type                 700 (12.0%)
10. ksic_code                        411 (7.1%)
[병목 아님] sector 0% · employee 0.02% · total_worker_calc 0%
```

---

## 종합 판단 — P1 안전 시작점
```
✓ 좋은 소식: sector 100%·employee 100%·ksic 93% → UNIVERSAL/THRESHOLD 기반 의무는 5,400 시설 즉시 가능.
✓ 다수 섹터(건설 90%)는 건설 has_* 96% 보유 → 건설 EXISTS도 데이터 충분.
△ 제약: 건물/설비 상세속성(용도·층수·면적·산업 has_*)은 희소 → 해당 EXISTS는 제한.
✗ 구조 병목: facility_profiles 미생성(2/5,812) — applicability MISSING_DATA의 직접 원인.

권고 P1 순서:
  1) facility_profiles 생성을 A티어 5,400(또는 섹터 코호트)에 실행(기계: facility_profile_service, 존재).
  2) profiles 생성 후 동일 섹터에서 applicability MISSING% 재측정(개선 확인).
  3) UNIVERSAL+THRESHOLD 우선 의무 생성 → 조문 단위 글읽기 검증 → 점진 확대.
  ※ 상세속성 의존 EXISTS는 속성 보강 전까지 보류(거짓 단정 방지).
```

## Boundary 준수
```
읽기 전용 100%. INSERT/UPDATE/DELETE 0. profiles/obligation_instance 생성 0.
Applicability/Generator 미수정. 샘플링·추정 없음(전수 집계).
```

*WO-FACILITY-DATA-COVERAGE-001 — PASS. 즉시 가능 5,400(92.9%)·보완 412·불가 0. 1차 병목=facility_profiles 미생성. 안전 시작=profiles 배치(A티어)→UNIVERSAL/THRESHOLD 생성·검증→점진 확대.*
