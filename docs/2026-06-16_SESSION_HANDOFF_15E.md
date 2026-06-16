# 세션 핸드오프 — 법령엔진 15E

**작성일**: 2026-06-16  
**다음 세션 시작점**: Domain Rule WO 설계 또는 Actor Overlay 연결

---

## ★ 이 문서 하나만 읽으면 됩니다

다른 설계 문서는 읽지 마세요.
현행 기준: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
구현 WO: `docs/2026-06-16_WO_D_PIPELINE_IMPL.md`
Actor WO: `docs/2026-06-16_WO_LEG_COMPILER_003.md`

---

## 오늘 완료한 것 (15D~15E)

### Actor Resolution Overlay 완료

**DB 생성 완료**:
- `actor_resolution_pattern` DDL ✅ (81개 패턴 입력)
- `semantic_clause_actor_resolution` DDL ✅
- Overlay 적용 ✅ — 53,053건 중 24,127건 매칭 성공

### K-01~05 측정 결과 (핸심)

**K-01: 전체 분류 통계 (53,053건)**

| 구분 | 건수 | 비율 |
|---|---|---|
| 매칭 성공 | 24,127건 | 45.5% |
| UNKNOWN 잡존 | 28,926건 | 54.5% |
| — AUTHORITY | 15,670건 | 29.5% |
| — BUSINESS | 5,369건 | 10.1% |
| — FRAGMENT | 2,697건 | 5.1% |
| — ASSOCIATION | 391건 | 0.7% |

**K-02~03: 화성 제2공장 209건에 Overlay 적용**

| actor_group | 건수 |
|---|---|
| AUTHORITY | 189건 |
| BUSINESS | 78건 |
| FRAGMENT | 31건 |
| ASSOCIATION | 16건 |

→ AUTHORITY + FRAGMENT + ASSOCIATION 제거 시 236건 제거 가능, 78건 잔존

**K-05: BUSINESS actor인데 여전히 오염인 것 (Domain 문제)**

| 법령명 | actor_code | 이유 |
|---|---|---|
| 소방시설공사업법 | ACTOR:CONSTRUCTOR | 공사업자 의무, 제조업 해당 없음 |
| 공동주택관리법 | ACTOR:MANAGER | 공동주택 관리자 의무 |
| 정보통신공사업법 | ACTOR:CONSTRUCTOR | 공사업자 의무 |
| 건설산업기본법 | ACTOR:CONSTRUCTOR | 건설업 의무 |
| 초고층 복합건축물 재난관리 | ACTOR:MANAGER | 건물 관리 의무 |

**최종 판정: Actor 문제 + Domain 문제 둘 다 존재**

```
Actor 문제 = AUTHORITY 189건 (행정청의 무 ACTOR로 사업주와 혼입)
Domain 문제 = BUSINESS actor인데 업종 불일치
                   (CONSTRUCTOR ≠ 제조업, MANAGER ≠ 공장)
```

---

## 다음 세션 해야 할 것

### 우선순위 1 — Actor Overlay → D-002 연결

AUTHORITY/FRAGMENT로 분류된 clause가 Track A의 executable_draft에도 연결됐는지 확인.
`facility_applicability` 조회 시 `actor_group = AUTHORITY`인 것들을 배제하는 연결선 만들기.

### 우선순위 2 — Domain Rule WO 설계

BUSINESS actor인데 오염인 것을 업종/송도 단위로 필터:
- ACTOR:CONSTRUCTOR → INDUSTRIAL sector 대상이 맞는지 확인
- ACTOR:MANAGER → 대상 시설 유형 (BUILDING vs INDUSTRIAL) 확인
- law_sector_mapping에 CONSTRUCTOR 개념 추가 기준 설계 필요

### 우선순위 3 — D-004B-PILOT-SAFETY-MANAGER

- 선행 조건: Domain Rule WO 운영 후
- `appendix_condition` 7건 + 산안법 시행령 별표3 기반
- industry_name 텍스트 매칭으로 파일랿 가능

---

## 절대 금지 (유효)

```
GPT 전속 테이블 (읽기만):
  constraint_node, rule_candidate, executable_draft, draft_slot
  semantic_clause_actor_resolution 에 DROP 컨럼 추가 금지

삭제 금지:
  evaluate_single_factory
  evaluate_draft_for_facility
  semantic_clause_fix 직접 수정

D-004B-PILOT 독단 착수 금지 (사장님 승인 필수)
```

---

## 커밋 이력 (15D~15E)

| SHA | 내용 |
|---|---|
| 48f082f | WO-LEG-Compiler-003 초기본 |
| b5526e5 | WO-LEG-Compiler-003 위치 명확화 + K-01~05 추가 |
| DB | actor_resolution_pattern (81건) + semantic_clause_actor_resolution (24,127건) |
