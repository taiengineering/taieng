# COVERAGE GAP REPORT V1
# WO-COVERAGE-GAP-PRIORITY-001

**작성일**: 2026-06-18  
**성격**: 측정 전용. 구현 없음.  
**목적**: CONSTRUCTION vs BUILDING 중 다음 확장 대상을 수치로 결정

---

## 핵심 질문

```
V4 미커버 영역 = CONSTRUCTION, BUILDING
둘 중 어느 것이 먼저인가?
```

---

## Step 3. 법령 모집단 (law_sector_mapping, sector 포함 기준)

| sector | 법령 수 | 전체 대비 |
|---|---|---|
| BUILDING | 175 | 48.7% |
| INDUSTRIAL | 158 | 44.0% |
| CONSTRUCTION | 130 | 36.2% |
| SPECIAL_FACILITY | 113 | 31.5% |
| 전체 매핑됨 | 359 | — |

(복수 sector 곹침 허용 → 합계 100% 초과)

---

## Step 4. 실제 facility_applicability 발생량 (사업장당 정규화)

| sector | 총 applicability | 사업장 수 | 사업장당 평균 |
|---|---|---|---|
| CONSTRUCTION | 1,393 | 6 | **232.2** |
| INDUSTRIAL | 2,581 | 15 | 172.1 |
| BUILDING | 1,357 | 10 | 135.7 |

(MATCH_CANDIDATE + POSSIBLE_CANDIDATE 기준, 테스트 사업장)

---

## Step 5. Coverage Gap 산출

| sector | V4 Coverage | 법령 모집단 | 사업장당 발생 | 입력 존재 여부 |
|---|---|---|---|---|
| INDUSTRIAL | ✅ 100% | 158 | 172.1 | ksic_code ✅ |
| CONSTRUCTION | ❌ 0% | 130 | **232.2** | construction_amount ✅ |
| BUILDING | ❌ 0% | **175** | 135.7 | building_use_code ✅ |

---

## 두 지표의 상반된 신호

```
법령 모집단 기준 (법령이 몇 개인가):
  BUILDING 175 > CONSTRUCTION 130
  → BUILDING이 더 많은 법령 보유

사업장당 발생량 기준 (한 사업장이 몇 개 맞는가):
  CONSTRUCTION 232.2 > BUILDING 135.7
  → CONSTRUCTION이 사업장당 더 많은 의무
```

주의: 둘 다 Distribution/발생량이지 Impact(verdict 정확도)가 아니다.  
하지만 Coverage Gap 판단에는 충분한 지표.

---

## 우선순위 판단 (수치 근거)

```
1순위: CONSTRUCTION

근거:
  (1) 사업장당 발생량 232.2 — 3개 sector 중 최고
  (2) 입력 이미 존재 (construction_amount, sector)
      → 새 입력체계 불필요
  (3) 조건 구조 단순 (공사금액 구간 = METRIC 하나)
      → GPT 이전 판정과 일치 (Phase 5 = CONSTRUCTION)

2순위: BUILDING

근거:
  (1) 법령 모집단 175로 가장 크지만
  (2) 소방시설법·승강기법·에너지법 등
      산안법 외 별도 법령군 → 새 Appendix 수집 필요
  (3) 구현 난이도 높음 (여러 법령체계)
```

---

## 완료 조건 답변

```
Q: Phase 5는 CONSTRUCTION 먼저인가 BUILDING 먼저인가?
A: CONSTRUCTION 먼저.

이유:
  사업장당 발생량 최고 (232.2)
  입력 이미 존재 (구현 난이도 낮음)
  단일 METRIC 구조 (공사금액)

BUILDING은 법령 수는 더 많으나
별도 법령군 Appendix 수집이 선행되어야 하므로 2순위.
```

---

## 한계

```
- facility_count가 테스트 사업장 기준 (소표본)
- 사업장당 발생량은 Track A 기준 (93% 오염 포함된 수치)
  → 정확한 수치는 아니지만 sector 간 상대 비교에는 유효
- 법령 모집단은 law_sector_mapping 기준 (359건 매핑)
```

---

## 결론

```
Phase 5 = CONSTRUCTION 안전관리자 (공사금액 기반)

Coverage 데이터가 GPT 이전 판정을 독립적으로 재확인함.
감이 아니라 수치로 CONSTRUCTION 1순위 결정.
```
