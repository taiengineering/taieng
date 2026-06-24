# WO-PENDING-RESOLVE-001
# PENDING 41건 조문 단위 정밀 분리

**작성일:** 2026-06-24 | **상태:** 완료 (조문 단위 상태 전이)
**선행:** WO-CANDIDATE-REVIEW-001
**금지:** 신규 Harvest / TRUE_UNIVERSAL / APPENDIX / 패턴 재분석 / 기존 446 CONFIRMED 수정
**대상:** PENDING 41건 (DEMOLITION 39 + BOILER 2)에 대해서만 상태 변경

> EXISTS 1차 승격을 닫는 작업. 키워드 오염을 조문 직독으로 정리.

---

## 결론 먼저

```
PENDING 41건 전량 정리 완료.

  CONFIRMED  6   (진짜 건축물/구조물 해체작업)
  REJECTED  35   (석면 14 + 설비해체 10 + 무관 9 + 보일러 2)
  PENDING    0   (잔여 없음)

condition_mapping_candidate 최종:
  CONFIRMED 452 (기존 77 + 1차 369 + 이번 6)
  REJECTED   35
  PENDING     0
  HARVESTED   0

기존 77 무수정. EXISTS 1차 승격 라인 종료.
```

---

## TASK-001: PENDING 41건 전수 추출 (조문 직독)

```
DEMOLITION (has_demolition): 39건
BOILER (has_boiler): 2건
→ 41건 전부 조문 텍스트 직독 완료.
```

---

## TASK-002: DEMOLITION 39건 분리

### A. 진짜 해체작업 의무 → CONFIRMED (6건)

| 조문 | 판정 근거 |
|---|---|
| 터널 지보공 부재 해체 | 구조물 해체작업 |
| 해체공법 붕괴우려 (건축물관리법 해체계획서) | 건축물 해체작업 |
| 무너뜨리는 작업 중 | 해체작업 |
| 교량 설치·해체·변경 | 구조물 해체작업 |
| 구축물 시공·해체 하중 | 해체작업 안전 |
| 거푸집·동바리 조립·해체 | 해체작업 |

→ condition_code DETAIL을 DEMOLITION_WORK로 정제. confidence 0.88.

### B. 석면해체 → REJECTED/REASSIGN (14건)

```
"석면해체·제거작업" 조문들이 has_demolition으로 흡수됨.
→ 실제 소관: has_asbestos_demo (ASBESTOS Trigger, 이미 CONFIRMED)
→ 중복 방지 위해 REJECTED + exclude_reason 기록.
   'REASSIGNED_TO: has_asbestos_demo'
```

### C. 설비 설치·해체·점검 작업 → REJECTED/REASSIGN (10건)

```
크레인/리프트/승강기/항타기/비계/차량계하역기계의
설치·조립·수리·점검·해체 작업.
→ 실제 소관: 각 설비 EXISTS Trigger.
→ "해체" 키워드로 has_demolition에 잘못 수확됨.
→ REJECTED + 'REASSIGNED_TO: 설비 EXISTS Trigger'
```

### D. 무관 (키워드 오염) → REJECTED (9건)

```
난간 임시 해체, 방호장치 해체 금지, 전기작업,
안전밸브 해체, 가스배관 해체, 무포장 화물 내리기,
"그 밖의 작업", 순간풍속 10m 초과(타워크레인 풍속).
→ has_demolition(건축물 해체)과 무관.
→ REJECTED.
```

---

## TASK-003: BOILER 2건 분리

| 조문 | 판정 |
|---|---|
| 탱크·보일러 내부 용접·용단 작업 | REJECTED (REASSIGN: WORK_ACT 용접) |
| 불활성기체 배관 보일러·탱크 작업 | REJECTED (REASSIGN: FACILITY 밀폐공간) |

```
둘 다 "보일러" 단어는 있으나 보일러 설비 의무가 아님.
→ 보일러는 작업 "장소"일 뿐, 의무 원인은 용접/밀폐공간.
→ REJECTED + 'REASSIGNED_TO: WORK_ACT(용접)/FACILITY(밀폐공간)'
```

---

## TASK-004: REASSIGN 처리 원칙

```
안전한 방식 채택 (신규 INSERT 안 함):
  - PENDING 행을 REJECTED로 전이.
  - exclude_reason에 REASSIGNED_TO 대상 기록.
  - 실제 재배정 INSERT는 생략 (unique 충돌 + 이미 해당 Trigger가 커버).

근거:
  석면해체 → has_asbestos_demo가 이미 CONFIRMED로 동일 의무 커버.
  설비해체 → 각 설비 Trigger가 이미 커버 또는 별도 처리.
  → 중복 INSERT 불필요. 기록만으로 추적성 확보.
```

---

## TASK-005~006: 상태 전이 + 검증

| 항목 | 결과 | 판정 |
|---|---|---|
| PENDING 41 → 잔여 | 0 | ✅ |
| CONFIRMED 증가 | 446 → 452 (+6) | ✅ |
| REJECTED | 35 | ✅ |
| 기존 77 무수정 (reviewer NULL) | 77 | ✅ |
| condition_code 중복 | 0 | ✅ |
| COMMON sector | 0 | ✅ |
| NULL sector | 0 | ✅ |

---

## 산출물 A~E 요약

```
A. PENDING 41 판정: CONFIRMED 6 / REJECTED 35
B. DEMOLITION 분리: 진짜해체 6 / 석면 14 / 설비해체 10 / 무관 9
C. BOILER 분리: 용접 1 / 밀폐공간 1 (둘 다 REJECTED)
D. REASSIGN 후보: 석면→has_asbestos_demo, 설비해체→설비Trigger,
   보일러→WORK/FACILITY (전부 exclude_reason 기록, INSERT 생략)
E. 상태 전이: CONFIRMED 452 / REJECTED 35 / PENDING 0
```

---

## 핵심 발견

### 발견 1: "해체" 키워드가 4종을 흡수했다

```
has_demolition / "해체" 키워드 39건 실제 구성:
  진짜 건축물 해체:  6 (15%)
  석면해체:         14 (36%)  ← MATERIAL 흡수
  설비 해체작업:    10 (26%)  ← EQUIPMENT 흡수
  무관 오염:         9 (23%)

→ 다의어 키워드의 위험성 실증.
→ "해체"는 건축물해체/석면해체/설비해체/난간해체로 분산.
→ EXISTS 키워드 수확의 한계가 가장 큰 그룹.
→ 조문 직독 없이는 절대 못 거름.
```

### 발견 2: 보일러는 "장소"였지 "설비 의무"가 아니었다

```
"탱크·보일러 내부에서 용접" = 보일러 설비 점검 의무 아님.
보일러는 작업이 일어나는 밀폐 장소.
의무 원인 = 용접작업 / 밀폐공간.

→ EXISTS 키워드가 "단어 등장"과 "의무 원인"을 혼동.
→ 조문의 주어(무엇이 의무를 발생시키는가)를 봐야 정확.
```

### 발견 3: REJECTED는 손실이 아니다

```
35건 REJECTED 중 대부분은 REASSIGN(다른 Trigger가 커버).
실제 손실(완전 무관) = 9건뿐.
→ 석면/설비 의무는 다른 입력필드로 이미 도달 가능.
→ has_demolition에서 빠질 뿐, 의무 자체는 누락 안 됨.
```

### 발견 4: EXISTS 정확도 = 다의어 그룹만 문제

```
22그룹 중 20그룹 PASS (단어 고유).
2그룹만 PARTIAL (해체·보일러, 다의어).
→ DIVING/CRANE/HAZMAT처럼 고유 단어는 100% 정확.
→ 향후 키워드 수확 시 다의어 사전 식별 필요.
```

---

## 성공 기준 답변

```
PENDING 41건이 CONFIRMED / REJECTED / REASSIGN으로 정리됐는가?
  ✅ CONFIRMED 6 (진짜 해체작업)
  ✅ REJECTED 35 (석면14+설비10+무관9+보일러2)
  ✅ REASSIGN: exclude_reason에 대상 기록 (석면/설비/용접/밀폐공간)
  ✅ PENDING 0

EXISTS 1차 승격 라인 종료.
```

---

## 다음 단계

```
WO-PENDING-RESOLVE-001 (현재) — 완료. EXISTS 1차 종료.
      ↓
선택지 1: WO-HARVEST-TO-ASSET-002
  TRUE_UNIVERSAL 310 sector 일괄 적재 → REVIEW
선택지 2: WO-APPENDIX-HARVEST-001
  appendix_condition 입력 → THRESHOLD 병목 해소
      ↓
최종: 엔진 가동 검증 (452 CONFIRMED 기반 진단 출력 확인)
```

---

*WO-PENDING-RESOLVE-001 완료. PENDING 41 → CONFIRMED 6 / REJECTED 35 / PENDING 0.*
*핵심: "해체" 키워드가 4종(건축물/석면/설비/무관) 흡수 — 조문 직독으로 분리.*
*EXISTS 1차 승격 종료. CONFIRMED 452. 기존 77 무수정.*
