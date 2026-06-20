# CONSTRUCTION ACTIVATION — STEP 1~3
# WO-CONSTRUCTION-ACTIVATION-002

**작성일**: 2026-06-20
**목적**: 건설 고유 입력이 결과 문서(compliance_package)까지 도달하는지 확인.
**전제(규칙-004, 재검증 안 함)**: sector filter 완료 / 오매핑 0 / 건설입력→FacilityProfile YES 확정.
**금지 준수**: 신규 법령/draft_slot 생성 없음. 기존 semantic_clause만 조회. sector filter 재작업 없음.
**범위**: STEP-1~3 (연결지도 + 법령 인벤토리 + 연결표). STEP-4~7(VR 5000건/파이프라인/Reading)은 별도 실행.

---

## STEP-1: 건설 입력 현재 도달 연결지도 (실측)

```
건설 sector factory 195개 기준 계층별 도달:
  factory(195) → applicability(6) → task(6) → schedule(6)
  (도달 factory 수는 수량 판단 아님. 입력 종류별 도달이 핵심 — 아래)

건설 factory의 task 법령 출처:
  COMMON 법령 → task        776건  (공통 의무: 근로자/안전관리자 등)
  CONSTRUCTION 법령 → task    29건  (건설 고유 의무)

★ 건설 고유 법령 task 29건이 매칭된 통로(binding_field):
  binding_field = null            16건  (IF_SCOPE 무조건 통과)
  binding_field = monetary_value   4건  (공사금액 통로)
  binding_field = 건설 고유          0건  ← 타워크레인/발파/석면 등 = 0

= 건설 고유 입력(has_tower_crane 등)으로 매칭된 task = 0건.
  현재 건설 고유 의무 29건은 "공사금액" 또는 "무조건 통과"로 들어온 것.
```

### 연결지도 (건설 고유 입력 기준, YES/NO/UNKNOWN)

```
                      입력 저장 FacProfile applicability task schedule penalty package
has_tower_crane       YES  YES   YES        NO          NO   NO       NO      NO
has_confined_space    YES  YES   YES        NO          NO   NO       NO      NO
has_asbestos          YES  YES   YES        NO          NO   NO       NO      NO
has_blasting          YES  YES   YES        NO          NO   NO       NO      NO
has_diving            YES  YES   YES        NO          NO   NO       NO      NO
has_excavation        YES  YES   YES        NO          NO   NO       NO      NO
has_scaffold          YES  YES   YES        NO          NO   NO       NO      NO
has_formwork          YES  YES   YES        NO          NO   NO       NO      NO
construction_process  YES  YES   YES        NO          NO   NO       NO      NO
construction_work     YES  YES   YES        NO          NO   NO       NO      NO

공통 끊김 지점: FacilityProfile → facility_applicability.
  (건설 고유 입력을 받을 binding_field가 거름망에 0종)
construction_amount(참고): monetary_value 통로로 applicability~package 도달 YES.
```

---

## STEP-2: 기존 건설 법령 인벤토리 (semantic_clause, 조회만)

```
CONSTRUCTION sector 법령 = 4,079건. 위험 그룹별 분포:
  기타 건설일반    3,907
  타워크레인/양중     99
  굴착               34
  해체               31
  밀폐공간             5
  비계                2
  잠수/수중            1
  (발파/석면 = CONSTRUCTION sector엔 0, 아래 ★ 참조)

★ 발파/석면 법령은 CONSTRUCTION이 아닌 다른 sector에 존재:
  석면:  COMMON 390 / INDUSTRIAL 104 / BUILDING 9 / CONSTRUCTION 0
  발파:  INDUSTRIAL 4 / COMMON 1 / CONSTRUCTION 0
  화약:  INDUSTRIAL 4 / COMMON 3 / CONSTRUCTION 0

= 건설 현장 입력(석면/발파)이지만 법령은 COMMON/INDUSTRIAL에 분류됨.
  → sector filter상 건설 사업장엔 COMMON 석면/발파는 통과,
    INDUSTRIAL 석면/발파는 차단됨(교차).
  → 입력↔법령 연결이 sector 경계로 끊길 수 있음 (STEP-3 반영).
```

---

## STEP-3: 건설 입력 ↔ 기존 법령 연결표

```
건설 입력            → 참조해야 할 기존 법령(sector)              현재 거름망 통로
─────────────────────────────────────────────────────────────────────────
has_tower_crane     → 타워크레인/양중 99건 (CONSTRUCTION)         없음 (binding 0)
has_excavation      → 굴착 34건 (CONSTRUCTION)                   없음
has_scaffold        → 비계 2건 (CONSTRUCTION)                    없음
has_formwork        → 거푸집 (CONSTRUCTION, 소수)                없음
has_confined_space  → 밀폐공간 5건 (CONSTRUCTION) + COMMON 질식   없음
has_diving          → 잠수/수중 1건 (CONSTRUCTION)               없음
has_asbestos        → 석면 (COMMON 390 / INDUSTRIAL 104)★        없음
has_blasting        → 발파/화약 (INDUSTRIAL 8 / COMMON 4)★       없음
construction_process→ 기타 건설일반 3,907 (CONSTRUCTION)          없음
construction_work   → 기타 건설일반 (CONSTRUCTION)               없음
construction_amount → 공사금액 조건 (참고)                       monetary_value ✅

★ 석면/발파: 건설 입력이나 법령이 COMMON/INDUSTRIAL에 있음.
  COMMON분은 건설 사업장에 통과 가능, INDUSTRIAL분은 sector filter로 차단.

핵심: 법령은 기존에 존재한다(신규 생성 불필요).
  끊긴 것은 "건설 입력 → 이 법령들"을 잇는 거름망 통로(binding_field).
  → 이 연결(binding) 생성이 실제 활성화 작업이나, 그것은 STEP-4~7 결과
    Reading으로 "무엇이 안 나오는지" 확인한 뒤 별도 수정 단계에서 다룸.
```

---

## STEP-1~3 중간 결론 (수정 없음, 확인만)

```
1. 건설 고유 입력 10종은 FacilityProfile까지 YES, 그 다음(거름망)부터 NO.
2. 건설 고유 법령은 기존에 존재(타워크레인99/굴착34/해체31 등).
   단 석면/발파는 COMMON·INDUSTRIAL에 분류됨.
3. 입력↔법령을 잇는 거름망 통로(binding_field)가 0종 → task 미생성.

다음(STEP-4~7): VR 건설 5,000건 흘려 결과 문서를 읽고,
  건설 입력별로 결과 문장이 나오는지/안 나오는지 실제 기록.
  (수정은 그 뒤. 이 WO는 "안 나옴"을 대량 데이터로 확인하는 것까지.)
```
