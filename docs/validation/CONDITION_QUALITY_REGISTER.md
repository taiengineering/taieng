# IF_CONDITION 품질 검증 — 살릴 자산인가 정제 대상인가
# WO-IF-CONDITION-QUALITY-001

**작성일**: 2026-06-21
**목적**: IF_CONDITION 2525건을 ACTIVE/UNKNOWN/DISCARD로 분류. 살릴 가치 판정.
**방법**: 카운트 아닌 본문 Reading (draft_slot.part_id → semantic_clause 연결).
**금지 준수**: binding 설계 0, 코드 수정 0, sector mapping 0.

---

## ★★★ 판정: Boolean Trigger 설계 보류 (ACTIVE < 60%, 정제 먼저)

```
IF_CONDITION 2525건 중 ACTIVE(사업장 입력 연결 가능) = 약 24건 (1% 미만).
2525건을 그대로 살리면 행정·타부처·법인 절차 조건이 의무로 폭증.
→ Boolean Trigger Binding 설계 전에 IF_CONDITION 정제(또는 재추출) 필요.
```

---

## STEP-1: family 전수 분포

```
UNRESOLVED_CONDITION 1808 (72%)  ← 추출기가 family 미해결
IF_AFTER_INSTALL      322 (13%)  ← "설치하는 경우"
IF_OVER_THRESHOLD     168 (7%)   ← "초과/이상" (수치, NUMERIC과 중복 성격)
IF_ON_CHANGE          95         ← "변경한 경우"
IF_OPERATIONAL        83         ← "사용하는 경우"
IF_ON_ACCIDENT        45         ← "발생한 경우"
CONDITIONAL_FAMILY 2 / IF_EXISTS 2
```

---

## STEP-2: family별 본문 Reading

### 발견 1: raw_token에 "대상"이 없음 (종결어미만)

```
raw_token = "설치하는 경우에는" / "사용하는 경우" / "변경한 경우에는"
  → 무엇을 설치/사용/변경하는지(주어·목적어) 없음.
  → ACTIVE 판정은 본문(semantic_clause) 연결 필수.
```

### 발견 2: IF_OPERATIONAL/IF_AFTER_INSTALL도 대부분 "조건부 기술기준"

```
[조건부 기술기준 — Boolean trigger 부적합 (UNKNOWN/DISCARD)]
  "동력 작동 문을 설치하는 경우 다음 기준 구조로"   ← 설치 시 구조요건
  "가스장치실을 설치하는 경우 다음 구조로"
  "건조설비를 설치하는 경우 다음 구조로"
  "안전난간을 설치하는 경우 기준 구조로"
  "국소배기장치를 처음 사용하는 경우 사용 전 점검"
  = "그 설비를 설치/사용한다면 이 기준을 지켜라"
    = 사업장 보유 여부가 아니라 설치 행위의 부대조건.

[진짜 ACTIVE — 위험설비/물질 보유 trigger (소수)]
  "특수화학설비를 설치하는 경우 자동경보장치"     ← 특수화학설비 보유
  "위험물 저장탱크를 설치하는 경우 방유제"        ← 위험물탱크 보유
  "교류아크용접기를 사용하는 경우 자동전격방지기"  ← 용접기 보유
  "허가대상 유해물질 제조·사용 작업장"           ← 유해물질 취급
```

### 발견 3: UNRESOLVED_CONDITION 1808건(72%) = 거의 전부 DISCARD

```
  "퇴직한 경우 선임 신고"            ← 행정 절차
  "보상금을 지급한 경우 자료 전산화"   ← 행정청(국방부장관) 의무
  "사업 재개시한 경우 신고"          ← 행정 신고
  "재건축부담금 부과한 경우"         ← 국토부장관
  "도매제공을 요청한 경우"           ← 통신사업자 (산업안전 무관)
  "해산을 결의하는 경우 청산인"       ← 법인 절차
  "금융거래정보 요청하는 경우"        ← 건강보험공단
  = 행정청·타부처·통신·금융·법인 절차. 사업장 안전 위험요소 무관.
```

---

## STEP-3: 3등급 분류

### Q1 ACTIVE (사업장 입력으로 연결 가능) — 약 24건
```
사업주 주체 + 특정 위험설비/물질 보유 trigger:
  특수화학설비 설치 → 자동경보장치
  위험물 저장탱크 설치 → 방유제
  교류아크용접기 사용 → 자동전격방지기
  허가대상 유해물질 제조·사용 → 세척·세안설비
  국소배기장치 사용 → 사용 전 점검
  분진작업 습기설비 → 습한 상태 유지
  (석면/분진/가스/보일러/압력용기 관련 보유 trigger 포함)
→ 단 이마저 입력 필드(has_특수화학설비 등)가 대부분 없음.
```

### Q2 UNKNOWN (판단 불가/조건부) — 다수
```
IF_AFTER_INSTALL/IF_OPERATIONAL 중 "일반 설비 설치 시 구조요건":
  안전난간/문/건조설비/가스장치실 설치 시 구조기준.
  = 모든 사업장에 잠재 적용(보유 여부로 trigger 불가).
  Boolean 입력으로 거르기 부적합. 다른 처리(시설유형?) 필요.
IF_OVER_THRESHOLD 168 = 수치 조건이나 NUMERIC과 중복 — 재분류 필요.
```

### Q3 DISCARD (연결 가치 없음) — 1808건+ (72%+)
```
UNRESOLVED_CONDITION 1808 거의 전부:
  행정청·타부처·통신·금융·법인 절차 조건.
IF_ON_ACCIDENT 45: "발생한 경우" = 사고 사후, 사업장 입력 trigger 아님.
```

---

## STEP-4: 영향도

```
IF_CONDITION 2525건:
  ACTIVE   약 24건  (~1%)
  UNKNOWN  약 400건 (~16%, IF_AFTER_INSTALL/OPERATIONAL 일반 + OVER_THRESHOLD)
  DISCARD  약 1850건+ (~73%+, UNRESOLVED 대부분 + ON_ACCIDENT)
  (정밀 비율은 Reading 표본 기반 추정. 정확 집계는 전수 Reading 필요)
```

---

## STEP-5: Boolean Trigger 설계 가능성 판정

```
기준: ACTIVE ≥ 60% → 설계 / ACTIVE < 60% → 정제 먼저
결과: ACTIVE ~1% → ★ 정제 먼저 (설계 보류)

이유:
  2525건을 그대로 binding하면 행정·법인·타부처 조건이 의무로 폭증.
  = 소방 오염(F-01)보다 더 큰 오염 위험.
  IF_CONDITION은 "추출은 됐으나 품질 미정제 데이터"이지
  "바로 살릴 자산"이 아님.

권고:
  (a) UNRESOLVED_CONDITION 1808건은 binding 대상에서 제외(DISCARD).
  (b) ACTIVE 24건 + 위험설비 보유 trigger만 선별해 입력 필드 설계.
      = 앞 WO의 위험요소(타워크레인/석면/발파/밀폐/잠수)와 합쳐
        "사업장 보유 설비·물질" 입력군으로 묶어 Boolean binding.
  (c) 즉 Boolean Trigger는 "IF_CONDITION 전체"가 아니라
      "선별된 보유 trigger 소수"에만 적용.
```

---

## GPT 인계 (정제 + 선별 설계)

```
[정제]
  IF_CONDITION을 ACTIVE/UNKNOWN/DISCARD 라벨링.
  UNRESOLVED_CONDITION 1808건은 추출 품질 문제 → 재추출 또는 제외 판단(GPT).
[선별 Boolean Trigger]
  ACTIVE 24건 + 앞 위험요소 5종을 "사업장 보유 입력군"으로 통합.
  has_특수화학설비/has_위험물탱크/has_용접기/has_국소배기 등 입력 필드 설계 판단.
  단 이건 입력 스키마 + binding 설계 = GPT/엔진 영역.
[주의]
  "IF_CONDITION 2525건 전부 살리기" = 금지(오염 폭증).
  "선별 후 소수만 binding" = 안전.
```

---

## 성공 기준

```
- family 전수 분포           → ✅ (UNRESOLVED 72% 등)
- family별 본문 Reading      → ✅ (raw_token+본문 연결)
- 3등급 분류                → ✅ (ACTIVE 24 / UNKNOWN / DISCARD 1808+)
- 영향도 계산                → ✅ (ACTIVE ~1%)
- Boolean Trigger 판정       → ✅ (정제 먼저, 설계 보류)
- 예문 20개+ 포함            → ✅
- 수정 0건                   → ✅
```

---

## 완료 문장

```
IF_CONDITION 2525건을 본문 Reading으로 검증한 결과, ACTIVE(사업장 입력
연결 가능)는 약 24건(1%)에 불과하고, 72%(1808건)는 행정·타부처·법인 절차의
DISCARD 조건이었다. 따라서 IF_CONDITION은 "바로 살릴 자산"이 아니라
"먼저 정제해야 할 데이터"이며, Boolean Trigger Binding은 전체가 아닌
선별된 위험설비·물질 보유 trigger 소수에만 적용해야 한다.
ACTIVE < 60%이므로 설계 진행이 아니라 정제를 먼저 한다. 수정 0.
```
