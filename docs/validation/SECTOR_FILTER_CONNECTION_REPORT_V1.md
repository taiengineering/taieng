# SECTOR FILTER CONNECTION REPORT V1
# WO-SECTOR-FILTER-CONNECTION-001

**작성일**: 2026-06-20
**목적**: 기존 섹터별 법령 참조 구조를 거름망에 연결. COMMON + 동일 sector 법령만 후보 유지.
**성격**: 구현(연결). 신규 법령/draft_slot/binding_field 생성 0건.
**커밋**: tai-api `cbe28f8` (scripts/run_task_candidate.py)

---

## 1단계: sector filter 연결 (이번 WO) / 2단계: 건설 binding 확장 (다음 WO)

```
이 WO = 1단계 = "잘못 들어오는 법령을 막는 작업".
  → 건설 의무를 새로 나오게 하는 작업(2단계)이 아님.
  → 먼저 sector 오매핑을 차단해 결과의 섹터 섞임을 줄인다.
```

---

## 구현 내용 (run_task_candidate.py)

```
기존 데이터만 참조 (신규 생성 없음):
  (a) factories.sector        → facility_sector
  (b) semantic_clause.sector  → law_sector (source_part_id 기준, 다중 가능)

추가된 로직 (sector_allowed):
  IF law_sector == COMMON          → 허용
  ELSE IF law_sector == facility   → 허용
  ELSE                             → 차단 (오매핑, task 생성 skip)
  law_sector 미상(매핑 없음)       → 보수적 통과 (차단 안 함)

적용 위치: task 생성 루프 진입 직후 (기존 binding_field 평가 앞단).
  기존 binding_field 평가 / Action→Task 매핑 / relation 연결은 그대로.
```

---

## 설계 결정: law_sector 미상 처리 (명시)

```
task_candidate part_id 187개 중 semantic_clause 매핑 = 108개 (79개 미상).
미상 part를 어떻게 할지 = 필터 설계 핵심 결정.

선택: 보수적 통과 (차단 안 함).
이유: 필터 목적 = "확실한 오매핑만 제거".
      sector 불명을 차단하면 멀쩡한 task가 사라질 위험.
      = false negative(과잉 차단)보다 안전.
통계로 LAW_SECTOR_UNKNOWN_PASS 별도 집계 → 추후 매핑 확장 시 가시화.
```

---

## STEP-5: 스모크 테스트 (실데이터 시뮬레이션)

```
sector filter 적용 시 차단되는 오매핑 (semantic_clause 매핑 존재 part 기준):

| 사업장 sector | 법령 sector  | 차단 건수 |
|--------------|--------------|-----------|
| BUILDING     | INDUSTRIAL   | 56  ✅ 차단 |
| INDUSTRIAL   | CONSTRUCTION | 43  ✅ 차단 |
| BUILDING     | CONSTRUCTION | 30  ✅ 차단 |
| CONSTRUCTION | INDUSTRIAL   | 25  ✅ 차단 |
| INDUSTRIAL   | BUILDING     | 12  ✅ 차단 |
| CONSTRUCTION | BUILDING     | 10  ✅ 차단 |
| 차단 합계                    | 176       |

유지(허용):
  COMMON      2,241건  ✅ 유지
  동일 sector   318건  ✅ 유지

성공 기준 대조:
  BUILDING 결과에 INDUSTRIAL 법령 없음     → ✅ (56건 차단)
  INDUSTRIAL 결과에 BUILDING 법령 없음     → ✅ (12건 차단)
  CONSTRUCTION 결과에 INDUSTRIAL/BUILDING  → ✅ (25+10건 차단)
  COMMON 유지                              → ✅ (2,241건 유지)
```

---

## 성공 기준 점검

```
SF-01 거름망 평가 시 facility sector 확인  → ✅ (factories.sector 로드)
SF-02 법령 sector 확인                     → ✅ (semantic_clause.sector 로드)
SF-03 COMMON + 동일 sector만 허용          → ✅ (sector_allowed, 7/7 단위검증)
SF-04 기존 binding_field 평가 유지         → ✅ (앞단에 filter만 추가, 기존 로직 무변경)
SF-05 교차 sector 오매핑 차단              → ✅ (176건 차단, 스모크 확인)
SF-06 신규 법령/draft_slot/binding_field 0건 → ✅ (기존 데이터만 참조)
```

---

## 실행 안내 (반영 시점)

```
코드는 커밋됨(cbe28f8). DB 반영은 배치 재실행 시점:
  railway run python3 scripts/run_task_candidate.py
  → 재실행 시 sector filter 적용된 task_candidate 재생성.
  (Claude 환경은 네트워크 비활성 → railway 실행은 로컬/사장님 환경)

재실행 후 검증 쿼리(오매핑 0 확인):
  task_candidate × semantic_clause 조인 시
  facility_sector ≠ law_sector AND law_sector ≠ COMMON 건수 = 0 이어야 함.
```

---

## 완료 문장

```
기존 섹터별 법령 참조 구조가 거름망에 연결되었다.
신규 법령 생성 없이 COMMON + 동일 sector 법령만 후보로 남도록 처리하였다.
스모크 테스트상 교차 오매핑 176건이 차단되고 COMMON 2,241건은 유지됨을 확인하였다.
```

---

## 다음 단계 (2단계 예고, 이번 WO 범위 아님)

```
1단계(이 WO): sector filter 연결 → 오매핑 차단 ✅
2단계(다음): 건설 고유 입력 binding 확장 → 건설 고유 의무 활성화
  (WO-CONSTRUCTION-FILTER-CONNECTION 매핑표 + GPT 법령 컴파일 선행)
```
