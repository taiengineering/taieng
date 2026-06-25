# WO-UNIVERSAL-QUALITY-001
# UNIVERSAL HARVESTED 215 정제

**작성일:** 2026-06-25 | **상태:** 완료 (품질 개발 — ① Applicability 내부)
**헌법:** WO-ARCHITECTURE-FREEZE-001 발효 후 첫 품질 WO

## Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?    YES  (① UNIVERSAL 정제)
Boundary 변경 필요한가?         NO
Data Contract 변경 필요한가?    NO
Breaking Change인가?            NO
→ 전부 통과. Architecture Review 불필요.
```

---

## 결론 먼저 (정직한 실측)

```
UNIVERSAL baseline 건수는 늘지 않았다 (94건 유지).
대신 품질이 올라갔다 — 오염 후보 89건을 HARVESTED 풀에서 제거.

핵심 발견:
  직전 MVP(WO-LIVE-DIAGNOSIS-MVP-001)가 이미 진짜 CLEAN을
  최적 추출(94건)했고, 남은 215건은 정제 결과
  추가 승격 가능분이 0건이었다.

→ "baseline 증가"는 없었으나, 이게 정확한 결과.
→ 무리한 승격을 하지 않은 것이 헌법(품질=정확도)에 부합.
→ 남은 HARVESTED 풀이 깨끗해져 미래 오염 위험 제거.
```

---

## TASK-001: 215건 재분류 (직독 기준)

```
정규식 1차 분류:
  E_BUILDING_HOLD     60   (소방/승강기/건물관리)
  F_NEEDS_READ        59   (추가 직독 필요)
  B_FRAGMENT          54   (문장 조각)
  D_OUT_OF_SCOPE      25   (범위밖)
  A_CLEAN_UNIVERSAL   11   (정규식상 CLEAN)
  C_HIDDEN_CONDITION   6   (조건 숨음)

★ 직독 재검증 결과 (정규식 신뢰 불가 확인):
  - A_CLEAN 11건 직독 → 진짜 CLEAN 0~1건.
    나머지는 "명령 받은 사업주"(전제), "심사받은 사업주"(전제),
    예술인/노무제공자(범위밖), 프레스 전환스위치(설비전제).
  - F_NEEDS_READ 59건 직독 → 완결 무조건 명령 0건.
    전부 조건절(하거나/제N조에 따라/노출된) 포함.

→ 카운트 분석법의 위험 재확인:
  "사업주는"으로 시작해도 뒷부분에 조건이 숨어 CLEAN 아님.
  글을 읽어야만 잡힘 (헌법 검증원칙).
```

---

## TASK-002: CLEAN_UNIVERSAL 승격

```
승격: 0건.

이유:
  직독 결과 215건 중 sector만으로 발동하는
  완결 무조건 의무가 추가로 없음.
  진짜 CLEAN은 직전 MVP에서 이미 94건 전량 승격됨.

→ 헌법 원칙 "무리한 승격 금지" 준수.
→ 없는 것을 만들지 않음.
```

---

## TASK-003: 제외/보류 처리 (직독 기반)

```
처리 내역 (HARVESTED 215 → 분산):

  OUT_OF_SCOPE → REJECTED        28건
    예술인/노무제공자/보험/장애인/파견/주택/행정청
    exclude_reason 기록

  HIDDEN_CONDITION → PENDING     21건
    작업/설비/물질/명령 전제 숨음
    → 조건 입력 시 EXISTS/THRESHOLD로 재평가 (버림 아님)

  FRAGMENT → REJECTED            61건
    문장조각/주어불명/선행조건 의존

  BUILDING_HOLD + 잔여 → HARVESTED 유지   105건
    소방/승강기/건물관리 = BUILDING 서비스 확장 후보
    추가 직독 필요분 포함

상태 분포 (정제 후, condition_type='NONE'):
  CONFIRMED   94   (baseline, 변동 없음)
  HARVESTED  105   (BUILDING_HOLD + 직독대기)
  PENDING     21   (조건부 재평가 대상)
  REJECTED    90   (OUT_OF_SCOPE 28 + FRAGMENT 61 + 기존 1)
```

> review_status 제약: PENDING/CONFIRMED/REJECTED/HARVESTED만 허용.
> PENDING_FRAGMENT 등 세분 상태 없음 → exclude_reason으로 사유 기록.

---

## TASK-004: obligation_instance 재생성

```
CONFIRMED 변동 없음 (UNIVERSAL 94 유지) → 재생성 불필요.

factory e9c56af6 obligation_instance:
  기존 95건 그대로 (UNIVERSAL 93 + THRESHOLD 2).

UNIVERSAL CONFIRMED sector baseline:
  공통(I,C,B)   89
  INDUSTRIAL     4
  BUILDING       1
  = 94 (INDUSTRIAL factory는 89+4=93 적용)
```

---

## TASK-005: Adapter 연결 재검증

```
CONFIRMED 무변동 → Adapter 경로 동일.

  obligation_instance 95
    → Glue (obligation_instances_to_trigger_candidates)
    → candidate 95
    → build_obligations_from_trigger_candidates
    → obligations 95

누락 0 / 오염 법령: 정제로 오염 후보 제거됨.
→ CURSOR-TASK-001 검증과 동일 결과 (95 통과).
→ Boundary/Data Contract 무변경 확인.
```

---

## 핵심 발견

### 발견 1: baseline은 이미 최적이었다

```
직전 MVP 94건이 UNIVERSAL의 사실상 전량.
215건 추가 정제로도 승격 0건.
→ "더 짜낼 게 없다"가 정확한 진단.
→ 건수를 늘리는 게 품질이 아님. 오염 제거가 품질.
```

### 발견 2: 정규식은 끝까지 신뢰 불가

```
A_CLEAN 11 / F_NEEDS_READ 59 직독 → 추가 CLEAN 0.
"사업주는"으로 시작해도 조건이 뒤에 숨음.
→ 헌법 검증원칙(글 읽기) 재입증.
→ 카운트로 승격했으면 오염 89건 유입될 뻔.
```

### 발견 3: 품질은 "제거"로도 향상된다

```
오염 후보 89건(OUT_OF_SCOPE 28 + FRAGMENT 61)을
HARVESTED 풀에서 REJECTED로 분리.
→ 미래에 이 풀을 재승격해도 오염 안 섞임.
→ baseline 건수는 그대로지만 풀이 깨끗해짐.
→ 이게 "품질 개발"의 실체 (건수 아님).
```

### 발견 4: HIDDEN 21건은 자산으로 보존

```
작업/설비/물질 전제 21건 → PENDING (REJECTED 아님).
→ EXISTS 입력 수집 후 재평가 대상.
→ 버리지 않고 조건부 자산으로 보존.
```

---

## 성공 기준 답변

```
UNIVERSAL baseline이 증가하고 obligation_instance/Adapter에
반영되는가?

부분 충족 — 정직한 결과:
  baseline 건수 증가: 0 (이미 최적)
  품질 향상: ✅ (오염 89건 제거, 풀 정화)
  obligation_instance: 95 유지 (오염 없음)
  Adapter 통과: 95 (무변경)
  Boundary/Data Contract: 무변경 ✅

→ "증가"는 없었으나 "정제"는 성공.
→ 건수 집착 대신 정확도 확보 (헌법 정신).
```

---

## 남은 품질 이슈

```
1. HARVESTED 105건 잔여
   - BUILDING_HOLD(소방/승강기) = 건물 서비스 확장 시 처리
   - 일부 추가 직독 여지 (단 CLEAN 가능성 낮음)

2. PENDING 21건 (HIDDEN_CONDITION)
   - EXISTS 입력 수집 후 EXISTS/THRESHOLD로 재분류
   - 현재는 보류 (조건 데이터 없음)

3. UNIVERSAL baseline 94가 천장
   - 더 늘리려면 semantic_clause 원천 확대 필요 (별도 트랙)
   - 현 자산 내에서는 94가 최대 CLEAN
```

---

## 다음 단계 (헌법 ① 내부)

```
UNIVERSAL은 정제 완료 (천장 도달).
다음 품질 후보:
  - THRESHOLD 별표 확장 (안전관리자/보건관리자 — appendix)
  - EXISTS 입력 수집 (가장 큰 미연결, 입력단 동반)
  - PENDING 21 재평가 (EXISTS 수집 후)

→ UNIVERSAL보다 THRESHOLD/EXISTS가 증가 여지 큼.
```

---

*WO-UNIVERSAL-QUALITY-001 완료. 품질 개발 — ① Applicability 내부.*
*핵심: baseline 94 천장 확인, 승격 0 (이미 최적). 오염 89건 제거로 풀 정화.*
*정규식 신뢰 불가 재입증 — 직독만이 CLEAN 판별. Boundary/Contract 무변경.*
