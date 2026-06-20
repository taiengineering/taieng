# SECTOR FILTER CONNECTION REPORT V1
# WO-SECTOR-FILTER-CONNECTION-001

**작성일**: 2026-06-20
**목적**: 기존 섹터별 법령 참조 구조를 거름망에 연결. COMMON + 동일 sector 법령만 후보 유지.
**성격**: 구현(연결). 신규 법령/draft_slot/binding_field 생성 0건.
**커밋**: tai-api `cbe28f8`(sector filter) + `5b19ff8`(TRUNCATE CASCADE 수정)
**상태**: 배치 재실행 완료, DB 반영 검증 완료 (교차 오매핑 잔존 0건).

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

추가 수정(5b19ff8): TRUNCATE ... CASCADE.
  document_requirement_candidate가 task_candidate를 FK 참조해
  기존 TRUNCATE가 실패하던 것 수정. 자식 체인은 후속 배치가 재생성.
```

---

## 설계 결정: law_sector 미상 처리 (명시)

```
semantic_clause에 sector 매핑이 없는 part = 보수적 통과 (차단 안 함).
이유: 필터 목적 = "확실한 오매핑만 제거".
      sector 불명을 차단하면 멀쩡한 task가 사라질 위험(과잉 차단)보다 안전.
통계로 LAW_SECTOR_UNKNOWN_PASS 별도 집계 → 추후 매핑 확장 시 가시화.
실제 배치에서 이 통과분 = 2,377건 (아래).
```

---

## ★ 실제 배치 재실행 결과 (2026-06-20, railway run, DB 반영 완료)

```
실행: railway run python3 scripts/run_task_candidate.py (taiengcokr 계정)

배치 로그:
  대상 applicability: 5,331건
  factory sector: 699건 / law sector 매핑 part: 49,997건
  Task Candidate 재생성: 3,405건 / Relation: 15,389건 / Facilities: 31

  [sector-filter] 판정 분포:
    허용 COMMON:        2,190
    허용 SAME_SECTOR:     338
    허용 LAW_UNKNOWN:   2,377  (법령 sector 매핑 없어 보수적 통과)
    차단 CROSS_SECTOR:    426  ← 오매핑 차단

DB 검증 (재실행 후 task_candidate × semantic_clause):
    COMMON 유지:        2,311
    동일 sector 유지:     339
    교차 오매핑 잔존:       0  ✅ 완전 차단
```

---

## 미리보기(176/110) vs 실제 배치(426) 차이 설명 (정직)

```
사전 SQL 미리보기 = 현재 task_candidate에 있던 part(187개)만 대상 → 110~176건.
실제 배치 = facility_applicability(5,331건)부터 전체 재생성 +
           semantic_clause 전체(49,997 part) 로드 → 판정 대상이 훨씬 넓음 → 426건.
= 미리보기가 부분 집계였고, 배치 로그(426)가 전체 기준 정답.
  핵심 검증(교차 오매핑 잔존 0)은 동일하게 충족.
```

---

## 성공 기준 점검

```
SF-01 거름망 평가 시 facility sector 확인  → ✅ (factories.sector 699건 로드)
SF-02 법령 sector 확인                     → ✅ (semantic_clause 49,997 part 로드)
SF-03 COMMON + 동일 sector만 허용          → ✅ (sector_allowed, 7/7 단위검증)
SF-04 기존 binding_field 평가 유지         → ✅ (앞단에 filter만 추가)
SF-05 교차 sector 오매핑 차단              → ✅ (426건 차단, DB 잔존 0)
SF-06 신규 법령/draft_slot/binding_field 0건 → ✅ (기존 데이터만 참조)
```

---

## 후속 필요 작업 (CASCADE 영향)

```
TRUNCATE CASCADE로 task_candidate 자식 체인도 비워짐:
  document_requirement_candidate / form_mapping_candidate /
  checklist·evidence·field_coverage_candidate.
→ 후속 배치 순서 재실행으로 재생성 필요:
  railway run python3 scripts/run_schedule_candidate.py
  railway run python3 scripts/run_penalty_candidate.py
  railway run python3 scripts/run_compliance_package.py
  (sector filter 적용된 task_candidate 기준으로 자식 깨끗이 재생성)
```

---

## 완료 문장

```
기존 섹터별 법령 참조 구조가 거름망에 연결되었다.
신규 법령 생성 없이 COMMON + 동일 sector 법령만 후보로 남도록 처리하였다.
배치 재실행 결과 교차 오매핑 426건이 차단되고 DB 검증상 오매핑 잔존 0건,
COMMON 2,311건·동일 sector 339건은 유지됨을 확인하였다.
```

---

## 다음 단계 (2단계 예고, 이번 WO 범위 아님)

```
1단계(이 WO): sector filter 연결 → 오매핑 차단 ✅ 완료
2단계(다음): 건설 고유 입력 binding 확장 → 건설 고유 의무 활성화
  (WO-CONSTRUCTION-FILTER-CONNECTION 매핑표 + GPT 법령 컴파일 선행)

별도 과제: LAW_UNKNOWN 통과 2,377건
  = semantic_clause sector 매핑이 없는 part. 추후 매핑 확장 시 추가 정합화 대상.
```
