# WO-LIVE-DIAGNOSIS-MVP-001
# has_* 없이 작동하는 첫 진단 MVP

**작성일:** 2026-06-24 | **상태:** 완료 (실제 생성)
**선행:** WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001
**금지 (전부 준수):** has_* 수집/EXISTS 추적/새 Trigger/새 Harvest/Check Engine 수정 없음
**목적:** 현재 운영 입력에 이미 있는 값(sector+numeric)만으로 obligation_instance 생성.

> EXISTS는 입력 UI 따라온 뒤. 지금은 sector/numeric MVP를 먼저 살린다.

---

## 결론 먼저

```
has_* 없이 첫 진단 성공.

factory e9c56af6 (INDUSTRIAL, worker 280, floor 12500):
  → obligation_instance 95건 (0건 아님!)
    UNIVERSAL (sector=INDUSTRIAL): 93
    THRESHOLD (worker_count≥20, ≥50): 2

sector baseline 확보 (모든 sector):
  INDUSTRIAL  94 / CONSTRUCTION 90 / BUILDING 91

→ has_* 단절을 우회. sector+숫자만으로 의무 생성.
→ "0건"에서 "95건"으로. 첫 살아있는 진단.
```

---

## TASK-001: UNIVERSAL CONFIRMED 승격 (조문 직독)

```
UNIVERSAL 310 HARVESTED 직독 분류:
  CLEAN_OWNER (사업주 무조건 의무)    승격 대상
  BUILDING_HOLD (소방·관리주체)       제외 (HOLD)
  FRAGMENT (문장 조각)                제외
  EQUIP_PREMISE (설비 전제)           제외
  보험/파견/주택/예술인 (범위밖)      제외
  별표 위임 (THRESHOLD/APPENDIX)      제외

승격 기준 (보수적):
  - action_text가 '사업주는'으로 시작
  - 명령/금지 종결('하여야 한다'/'아니 된다')
  - 설비명/소방/범위밖/별표 키워드 없음

결과: 95건 CONFIRMED 승격 (310 중)
  → 직독 후 보험 오염 1건 추가 제거 → 최종 UNIVERSAL CONFIRMED 94
  → 215건은 HARVESTED 유지 (FRAGMENT/HOLD/조건부 의심)
```

### 승격 검증 (직독 표본)

```
✅ "사업주는 차량계 건설기계에 전조등을 갖추어야 한다"
✅ "사업주는 목욕시설ㆍ화장실 등을 소독"
✅ "사업주는 사업장 총괄관리자에게 업무 부여"
✅ "산업안전보건위원회 위원에게 불리한 처우 금지"
✅ "휴게시설을 갖추어야 한다"
✅ "방독마스크 보관함을 갖추어야 한다"

제거 (직독으로 발견):
❌ "보험에 가입된 사업에...변경되면" → 보험료징수법 (REJECTED)
```

---

## TASK-002: THRESHOLD 입력 후보 (운영 입력 기준)

```
현재 운영 입력에 존재하는 numeric:
  worker_count / total_workers   ← facility_profiles, 모든 진단 경로
  total_floor_area / floor_area  ← 모든 경로
  electrical_capacity_kw         ← facility_profiles
  gas_capacity                   ← facility_profiles
  construction_amount            ← 건설

→ THRESHOLD 판정 재료는 충분.
→ 단 cmc에 THRESHOLD 매핑이 0건이었음.
```

---

## TASK-003: THRESHOLD MVP 매핑

```
근거 본조 명시 확실한 것만 CONFIRMED (별표 위임 제외):

  worker_count >= 20 → 안전보건관리담당자 1명 선임
    근거: "상시근로자 20명 이상 50명 미만 사업장에
           안전보건관리담당자를 1명 이상 선임해야 한다"
    (본조 직접 명시 ✅)

  worker_count >= 50 → 산업보건의
    근거: "상시근로자 수가 50명 이상인 사업장"
    (본조 직접 명시 ✅)

보류 (별표 위임 — 근거 불명확):
  안전관리자(별표3), 보건관리자(별표5),
  floor_area/electrical_kw 임계값
  → CONFIRMED 금지 원칙 준수. 추후 appendix 입력 후.

적재: THRESHOLD CONFIRMED 2건 (input_operator='>=')
```

---

## TASK-004: generator UNIVERSAL + THRESHOLD 처리

```
규칙 구현 (SQL):

UNIVERSAL:
  WHERE condition_type='NONE' AND review_status='CONFIRMED'
    AND {sector} = ANY(applicable_sectors)
  → sector만 맞으면 생성. input_field=NULL.

THRESHOLD:
  WHERE condition_type='THRESHOLD' AND review_status='CONFIRMED'
    AND {worker_count} >= input_value::numeric
    AND {sector} = ANY(applicable_sectors)
  → 입력값 >= 기준값이면 생성.

상태:
  CONFIRMED만 status='ACTIVE'.
  HARVESTED/PENDING 제외.
```

---

## TASK-005: Live Diagnosis MVP 실행 (실제 factory)

```
factory: e9c56af6-5de7-487d-bd2e-0d452291a562
  sector: INDUSTRIAL (실제)
  worker_count: 280 (실제, facility_profiles)
  floor_area: 12500 (실제)

생성 결과:
  UNIVERSAL: 93 (sector=INDUSTRIAL baseline)
  THRESHOLD: 2 (worker 280 ≥ 20 + ≥ 50)
  ─────────────
  합계: 95 obligation_instance (status=ACTIVE)

THRESHOLD 직독 검증:
  "상시근로자 280명 ≥20 → 안전보건관리담당자 선임" ✅
  "상시근로자 280명 ≥50 → 산업보건의" ✅
```

---

## 검증 결과

| 항목 | 결과 | 판정 |
|---|---|---|
| has_* 없이 생성 | 95건 | ✅ (0건 아님) |
| UNIVERSAL baseline | 93 | ✅ |
| THRESHOLD | 2 | ✅ |
| 전부 CONFIRMED 출처 | 95 | ✅ |
| 보험 오염 제거 | 1 → 0 | ✅ |
| 모든 sector baseline | 공통90/건설90/건물91 | ✅ |

---

## 핵심 발견

### 발견 1: has_* 없이도 진단이 산다

```
sector(항상 존재) + worker_count(항상 존재)만으로 95건.
→ EXISTS 단절과 무관하게 의미있는 진단 가능.
→ 17회차 "0건"의 벽을 sector/numeric로 우회.
→ 첫 실제 운영 입력 기반 진단.
```

### 발견 2: UNIVERSAL 승격은 직독이 필수였다

```
정규식 1차: 310건 전부 "CLEAN" (오판).
직독 정밀: CLEAN 95 / HOLD 67 / FRAGMENT 52 / 기타.
→ "그 밖에 필요한 조치", "타인에게 열람하게 하거나" 등
  문장 조각이 UNIVERSAL로 위장.
→ 소방·관리주체(HOLD)가 67건 섞임.
→ 숫자가 아닌 글 읽기로만 걸러짐 (VALIDATION-001 재확인).
```

### 발견 3: THRESHOLD는 본조 명시만 안전

```
안전관리자/보건관리자 임계값 = 대부분 별표 위임.
본조 직접 명시 = 안전보건관리담당자(20), 산업보건의(50)뿐.
→ "근거 불명확 시 CONFIRMED 금지" 원칙 준수.
→ 2건만 보수적 적재.
→ 나머지는 appendix_condition 입력 후 (병목).
```

### 발견 4: 보험 오염은 직독으로만 잡힘

```
"보험에 가입된 사업에...변경되면"이 UNIVERSAL로 승격됐다가
직독 검증에서 발견 → REJECTED.
→ SCOPE 필터(보험료징수법)가 UNIVERSAL에도 필요.
→ obligation_instance 정합성까지 연쇄 정리.
```

---

## 성공 기준 답변

```
실제 운영 입력만으로 obligation_instance가 생성되는가?
has_*가 없어도 첫 진단 결과가 나오는가?

✅ 나온다. 95건.
  sector=INDUSTRIAL → UNIVERSAL 93
  worker_count=280 → THRESHOLD 2

→ has_* 단절을 우회한 첫 Live Diagnosis MVP 완성.
```

---

## 현재 cmc 상태 (갱신)

```
condition_mapping_candidate:
  CONFIRMED: EXISTS 375 + UNIVERSAL 94 + THRESHOLD 2 = 약 471
  HARVESTED: UNIVERSAL 215
  REJECTED: 36 (보험 1건 추가)

obligation_instance:
  factory e9c56af6: 95건 (UNIVERSAL 93 + THRESHOLD 2)
```

---

## 다음 단계

```
WO-LIVE-DIAGNOSIS-MVP-001 (현재) — 완료. 첫 진단 95건.
      ↓
선택지 1: 다른 sector factory로 검증 (건설/건물)
  → CONSTRUCTION 90 / BUILDING 91 baseline 실증
선택지 2: obligation_instance → 진단 결과 페이지 연결
  → 95건을 사용자에게 보여주는 출력 (6W/체크엔진)
선택지 3: THRESHOLD 확장 (appendix_condition 입력)
  → 안전관리자 등 별표 임계값 활성화
선택지 4: UNIVERSAL 215 HARVESTED 추가 정제
  → FRAGMENT/HOLD 분리해 baseline 더 확보
```

---

## 한계 (정직한 기록)

```
1. EXISTS 의무 0건 (has_* 미수집 — 의도된 보류)
2. THRESHOLD 2건뿐 (별표 위임 대부분 보류)
3. UNIVERSAL 94건은 보수적 승격 (215건 미정제 잔존)
4. 단일 factory 검증 (다른 sector 미실행)

→ 그러나 "살아있는 진단"의 첫 증명으로 충분.
→ sector+numeric만으로 95건 = MVP 성공.
```

---

*WO-LIVE-DIAGNOSIS-MVP-001 완료. has_* 없이 첫 진단 95건.*
*UNIVERSAL 93(직독 승격) + THRESHOLD 2(본조명시). 보험 오염 직독 제거.*
*핵심: sector+worker_count만으로 0건→95건. EXISTS는 입력 UI 후.*
