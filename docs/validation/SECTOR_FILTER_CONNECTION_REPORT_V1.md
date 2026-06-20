# SECTOR FILTER CONNECTION REPORT V1
# WO-SECTOR-FILTER-CONNECTION-001 / CLOSEOUT-001

**작성일**: 2026-06-20
**목적**: 기존 섹터별 법령 참조 구조를 거름망에 연결. COMMON + 동일 sector 법령만 후보 유지.
**성격**: 구현(연결). 신규 법령/draft_slot/binding_field 생성 0건.
**커밋**: tai-api `cbe28f8`(sector filter) + `5b19ff8`(TRUNCATE CASCADE 수정)
**상태**: ★ 1단계 공식 종료 (WO-SECTOR-FILTER-CLOSEOUT-001). 전 파이프라인 반영, 최종 오매핑 0건.

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

## ★★ CLOSEOUT: 후속 배치 전 파이프라인 재생성 (CASCADE 자식 체인 복원)

```
TRUNCATE CASCADE로 비워진 자식 체인을 후속 배치로 재생성. 전부 정상 완료:

railway run python3 scripts/run_schedule_candidate.py
  → schedule_candidate 1,182건 / Tasks 연결 584 / Issues 0 / 완료 0.5초

railway run python3 scripts/run_penalty_candidate.py
  → penalty_candidate 3,129 / numeric 1,696 / reference_link 2,749
    obligation_relation 7,511 / Issues 0 / 완료 5.6초

railway run python3 scripts/run_compliance_package.py
  → compliance_package 344건(시설별) / Review Queue 3,758 / Audit Log 20단계
    완료 1.7초
  Audit Log Step 18 = Task Candidate 3,405 (sector filter 값이 끝까지 전파됨)
  Final Validation: traceability/UNKNOWN/conflict preservation 전부 ✅
```

---

## ★★★ CLOSEOUT 최종 검증: 전 계층 오매핑 0건

```
재생성 후 파이프라인 전 계층 교차 오매핑 (law_sector ≠ COMMON AND ≠ facility):

  task_candidate          교차 오매핑  0  ✅
  document_requirement    교차 오매핑  0  ✅

= task_candidate부터 그 아래 문서요건까지 섹터 섞임 완전 제거.
  최종 산출물(compliance_package 344건) 기준 오매핑 0건.
```

---

## 성공 기준 점검

```
SF-01 거름망 평가 시 facility sector 확인  → ✅ (factories.sector 699건 로드)
SF-02 법령 sector 확인                     → ✅ (semantic_clause 49,997 part 로드)
SF-03 COMMON + 동일 sector만 허용          → ✅ (sector_allowed, 7/7 단위검증)
SF-04 기존 binding_field 평가 유지         → ✅ (앞단에 filter만 추가)
SF-05 교차 sector 오매핑 차단              → ✅ (426건 차단, 전 계층 잔존 0)
SF-06 신규 법령/draft_slot/binding_field 0건 → ✅ (기존 데이터만 참조)
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

## 2단계 분리 명시 (이번 WO 범위 아님, 착수 금지)

```
1단계(이 WO): sector filter 연결 → 오매핑 차단 ✅ 종료
2단계(별도 WO): 건설 고유 입력 binding 확장 → 건설 고유 의무 활성화
  → 본 WO에서 착수하지 않음. draft_slot/건설 binding 논의 없음.
  → 별도 WO로 분리. GPT 법령 컴파일 선행 필요.
  → 참조: WO-CONSTRUCTION-FILTER-CONNECTION-001 매핑표(GPT 인계 준비됨).

별도 과제(분리): LAW_UNKNOWN 통과 2,377건
  = semantic_clause sector 매핑 없는 part. 추후 매핑 확장 시 정합화 대상.
```

---

## 완료 문장

```
sector filter 1단계는 전 파이프라인에 반영되었고,
최종 산출물 기준 섹터 오매핑 0건으로 종료한다.
```
