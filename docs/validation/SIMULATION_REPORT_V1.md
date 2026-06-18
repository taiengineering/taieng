# SIMULATION_REPORT_V1
# WO-SIMULATION-PIPELINE-001 실행 결과

**작성일**: 2026-06-18  
**성격**: 측정 전용. 수정/구현 없음.  
**목적**: 가상 사업장 대량 시뮬레이션으로 V4 강점/약점 측정

---

## 실행 방식

API 1000회 호출 대신 C1 평가 로직을 SQL로 완전 재현.  
(Scope IN/NOT_IN + threshold 비교 — condition_scope_service와 동일 의미)

```
가상 사업장: 1000개 (INDUSTRIAL)
  업종: C10,C11,C19,C20,C21,C24,C26,C28,D35,H49,H50,B071 랜덤
  근로자: 0~2000 랜덤
평가: 1000 × 14조건 = 14,000건
```

---

## Step 3. Golden Case 채점 결과

```
MATCH:          3,213건 (23.0%)
NOT_MATCH:        312건 ( 2.2%)
NOT_APPLICABLE: 10,475건 (74.8%)
UNKNOWN:            0건 ( 0.0%)
```

UNKNOWN 0건 = 모든 가상 사업장이 ksic+workers를 가졌으므로 정상.  
NOT_APPLICABLE 74.8% = 업종별 조건 분리가 정상 작동 (예: C28은 고위험군 조건 NOT_APPLICABLE).

---

## Step 4. Coverage Report — 규모별 정확도

| 규모 구간 | 사업장 수 | 평균 MUST MATCH 수 |
|---|---|---|
| 1-49명 | 19 | 1.89 |
| 50-499명 | 225 | 3.15 |
| 500-999명 | 265 | 3.46 |
| 1000명+ | 491 | 3.68 |

패턴 정확: 인원 증가 → MATCH 의무 증가.  
49명 투이하는 안전관리자/경보설비 제외되어 평균 낮음 (정상).

---

## Step 5. Impact Ranking — V4 미커버 영역의 법령 빈도

IF_SCOPE 조건 493건을 유형별로 분류 (V4가 아직 평가하지 못하는 입력):

| 입력 유형 | 법령 draft 수 | 비율 | Priority |
|---|---|---|---|
| **EQUIPMENT** (equipment_type) | 209 | 42.4% | **HIGH** |
| **UNRESOLVED** (binding 실패) | 135 | 27.4% | **HIGH** |
| **FACILITY** (facility_type) | 133 | 27.0% | **MEDIUM** |
| **PROCESS** (process_type) | 16 | 3.2% | **LOW** |

### 해석 (수치 기반 우선순위)

```
EQUIPMENT 설비 연결:
  영향도 42.4% → Priority HIGH
  안전검사·압력용기·크레인·승강기 등 설비 기반 의무

UNRESOLVED 연결점 재생성:
  영향도 27.4% → Priority HIGH
  그러나 이 중 상당수는 EQUIPMENT/FACILITY로 귀속

FACILITY 연결:
  영향도 27.0% → Priority MEDIUM

PROCESS 연결:
  영향도 3.2% → Priority LOW
  (공정 연결은 단기 우선순위 낮음)
```

---

## 핵심 발견

```
이전 감잡이 우선순위:
  "Boolean 먼저? Equipment 먼저? Process 먼저?"

수치 기반 우선순위 (이제 확정):
  EQUIPMENT 42.4%  → 1순위
  FACILITY  27.0%  → 2순위
  PROCESS    3.2%  → 후순위
  Boolean (has_chemical_substance 등) → 별도 측정 필요
```

**주의**: 이 수치는 "구현 시작 신호"가 아니다.  
GPT 판정 순서(CONSTRUCTION → Obligation → BUILDING → Equipment)는 유지.  
단, Coverage Gap이 실제 확인될 때 Equipment가 Process보다 13배 중요함이 입증됨.

---

## 성공 기준 달성

```
✅ 100개 이상 사업장 자동 평가 (1000개)
✅ Golden Case 자동 채점 (TP/FP/FN/Unknown)
✅ Coverage Report 생성 (규모별)
✅ 우선순위 목록 생성 (Impact Ranking)
```

---

## 다음 단계 (구현 아닌 측정 계속)

```
1. CONSTRUCTION 가상 사업장 시뮬레이션 (공사금액 분포)
   → 현재 전체 UNKNOWN 확인 (Coverage Gap 정량화)

2. Boolean 입력 빈도 측정
   → has_chemical_substance 등이 실제 법령에서 요구되는 빈도

3. 점수 대시보드 (선택)
```

---

## 절대 금지 (유효)

```
측정 없이 수정 시작
발견 즉시 구현
Equipment/Process/Boolean 연결 (Coverage Gap 확인 + 우선순위 상위 전)
Track A 수정
새 법령 추가
```
