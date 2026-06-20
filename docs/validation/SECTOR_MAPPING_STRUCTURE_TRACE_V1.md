# 거름망 + 법령 섹션매핑 구조 확인 — SECTOR_MAPPING_STRUCTURE_TRACE_V1

**작성일**: 2026-06-20
**목적**: 거름망(단어매칭) 결과의 섹션별 법령 매핑 오류 구조 확인. "두 개를 다 조정"의 기준선.
**성격**: 확인 + 구조 확정. 수정 없음.

---

## 사장님 제기 (이번 작업의 본질)

```
거름망은 단어(token) 위주 매칭이다.
  → 결과에서 문서(법조문 글)를 읽으면
  → 섹션별(공통/산업/건물/건설) 법령 매핑이 잘못된 부분이 나온다.

법령에 "이건 건물이다 / 산업이다"라고 sector가 기재돼 있다.
SPECIAL_FACILITY(특수)는 서비스 안 함 → 예외/특수 처리 미확정.

= 거름망(단어매칭) + 법령 섹션매핑(sector 기재) 두 개를 다 조정한다.
```

---

## 확인 1: 법령 sector 기재 구조 (단일 vs 다중)

```
[semantic_clause] — 실제 채워져 작동하는 법령. sector = text(단일).
  COMMON        46,726   ← 공용 (사장님 기억 "공용 없다"와 달리 실재, 최다)
  BUILDING       4,539
  CONSTRUCTION   4,079
  INDUSTRIAL     3,151
  → SPECIAL_FACILITY(특수) 없음.
  → 단일 sector 구조 (한 조문 = 한 sector). COMMON 포함 4종.

[master_rule_v2] — sectors = ARRAY(다중) 타입이나 현재 0행(비어 있음).
  → 다중구조로 설계됐으나 데이터 없음.
  → 사장님이 "다중구조일 것"이라 한 기억은 이 설계(ARRAY)와 일치하나,
    실제 작동 데이터는 semantic_clause(단일)이다.

= 현재 실데이터 기준: 법령 sector는 COMMON 포함 단일 4종 구조.
  특수(SPECIAL_FACILITY)는 법령에도 없고 사업장에도 1건뿐.
```

---

## ★ 확인 2: 거름망 결과의 섹션 매핑 오류 (실측 교차표)

```
task_candidate(거름망 결과) × 법령 sector × 사업장 sector 대조:
  연결: task_candidate.part_id = semantic_clause.source_part_id
        + factories.sector

┌─────────────┬──────────────┬───────┬──────────────┐
│ 사업장 sector │ 법령 sector   │ 건수  │ 판정         │
├─────────────┼──────────────┼───────┼──────────────┤
│ INDUSTRIAL  │ COMMON       │ 1037  │ 정상(공용)    │
│ CONSTRUCTION│ COMMON       │  730  │ 정상(공용)    │
│ BUILDING    │ COMMON       │  474  │ 정상(공용)    │
│ INDUSTRIAL  │ INDUSTRIAL   │  299  │ 정상(일치)    │
│ CONSTRUCTION│ CONSTRUCTION │   15  │ 정상(일치/극소)│
│ BUILDING    │ BUILDING     │    4  │ 정상(일치/극소)│
├─────────────┼──────────────┼───────┼──────────────┤
│ BUILDING    │ INDUSTRIAL   │   56  │ ★오매핑       │
│ INDUSTRIAL  │ CONSTRUCTION │   43  │ ★오매핑       │
│ BUILDING    │ CONSTRUCTION │   30  │ ★오매핑       │
│ CONSTRUCTION│ INDUSTRIAL   │   25  │ ★오매핑       │
│ INDUSTRIAL  │ BUILDING     │   12  │ ★오매핑       │
│ CONSTRUCTION│ BUILDING     │   10  │ ★오매핑       │
└─────────────┴──────────────┴───────┴──────────────┘

오매핑 합계 = 176건 (사업장 sector ≠ 법령 sector, 공용 제외).
```

---

## 확인 3: 두 가지 문제가 동시에 보인다

```
[문제 A] 단어 거름망이 sector를 안 본다 → 교차 오염
  건물 사업장에 산업법령 56건, 건설법령 30건이 붙음.
  거름망(run_facility_applicability)이 binding_field 값만 비교하고
  법령의 sector('이건 건물이다')를 매칭 조건에 안 넣기 때문.
  → 거름망 조정 대상.

[문제 B] 동일 sector 매칭이 비정상적으로 적다
  CONSTRUCTION×CONSTRUCTION 15건, BUILDING×BUILDING 4건뿐.
  건설/건물 고유 법령(4079/4539건)이 있는데 거름망 통과는 극소.
  앞 WO 확인대로 건설 binding_field가 draft_slot에 0종이라
  건설 고유 법령이 거름망을 못 통과.
  → 법령 섹션매핑(어느 조문이 어느 sector 입력을 요구하는가) 조정 대상.
```

---

## "두 개를 다 조정한다" — 조정 대상 2종 (확인, 작업은 별도)

```
[조정 1] 거름망에 sector 매칭 추가
  현재: 단어(binding_field) 값만 비교.
  필요: 법령 sector(semantic_clause.sector)와 사업장 sector를
        매칭 조건에 반영 → 교차 오염(176건) 차단.
        단 COMMON은 모든 sector에 허용(공용).
  → 매칭 로직 = 엔진 영역. GPT 설계, Claude 구현.

[조정 2] 법령 섹션매핑 정합화
  현재: 건설/건물 고유 법령이 거름망 입력통로(binding_field) 부재로 미통과.
  필요: 섹터별 법령이 요구하는 입력(binding_field)을 draft_slot에 생성
        + FIELD_MAP·factories 컬럼 연결.
  → 법령 컴파일 = GPT. 저장/조회 = Claude.

특수(SPECIAL_FACILITY) 처리:
  법령에 특수 sector 없음 + 사업장 1건뿐 + 서비스 안 함.
  → 예외(제외)로 둘지 특수 유지할지 = 사장님 결정 사항(미확정).
```

---

## 완료 (확인)

```
거름망 결과의 섹션별 법령 매핑 구조를 확인하였다:
  - 법령 sector는 실데이터상 COMMON 포함 단일 4종(semantic_clause).
    master_rule_v2는 ARRAY(다중) 설계이나 0행.
  - 거름망 결과에 sector 오매핑 176건 존재
    (건물에 산업/건설 법령 등 교차 오염).
  - 동일 sector 매칭은 건설 15·건물 4건으로 비정상적으로 적음
    (건설/건물 고유 법령이 binding_field 부재로 거름망 미통과).

조정 대상 2종:
  ① 거름망에 sector 매칭 반영(교차오염 차단, COMMON 예외)
  ② 법령 섹션매핑 정합화(섹터별 binding_field 생성·연결)
특수(SPECIAL_FACILITY) 예외/유지 = 미확정(사장님 결정).
수정은 수행하지 않았다. 확인만.
```
