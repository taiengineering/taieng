# 세션 핸드오프 — 법령엔진 15차C

**작성일**: 2026-06-16  
**상태**: 1단계(D-001~007) 완료  
**다음 세션 시작점**: 2단계 — WO-APPENDIX-COLLECT-001

---

## ★ 이 문서 하나만 읽으면 됩니다

다른 설계 문서(Phase 2.1~v4, Cursor_Phase_2_2 등)는 **읽지 마세요**.
현행 기준 문서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN_v2.md`
구현 WO: `docs/2026-06-16_WO_D_PIPELINE_IMPL.md` (v2.1)

---

## 오늘 완료한 것 (15B~15C)

### D-001~007 전체 완료

| WO | 엔드포인트 | 상태 |
|---|---|---|
| D-001 SemanticClause Pipeline | `GET /semantic-pipeline/clauses` | ✅ total 53,053 |
| D-002 Common Sieve | `POST /common-sieve/run` | ✅ KEEP/DROP/PENDING 정상 |
| D-003 Section Sieve | `POST /section-sieve/run` | ✅ SPECIAL 0건 |
| D-004A Track A Adapter | `POST /check-adapter/run-track-a` | ✅ 260건 |
| D-005 KSIC Signal | `POST /ksic-signal/run` | ✅ process_noun_match 정상 |
| D-006 Reverse Check | `POST /reverse-check/trace-track-a` | ✅ full_trace 포함 |
| D-007 Refinery | `POST /refinery/run` | ✅ obligation_text 생성 |

### D-007 글읽기로 확인된 핵심 발견

파이프라인이 드러낸 Track A 오염 (limit=10 기준):
- `건축물의 분양에 관한 법률 제6조` — 부동산 거래 제한, 안전 의무 아님
- `공동주택관리법 시행령 제10조` — 공동주택 법인 의무, 제조업 해당 없음  
- `녹색건축 인증에 관한 규칙 제7조` — 인증기관 의무
- `작업환경측정기관 점검` — 측정기관(기관) 의무, 사업주 아님

**이것이 D단계의 목적 달성**: 오염이 숫자가 아닌 글로 보인다.

### 핵심 교훈 (이번 세션)

1. `load_track_a_results(status_filter=None)` → 0건 반환. 반드시 `status_filter` 명시
2. `stored_diagnosis_result` 테이블 없음 → D-007은 메모리 객체 반환으로 구현
3. `facility_applicability.factory_id` (facility_id 아님) — 컬럼명 실측 필수

---

## 다음 세션 시작점: 2단계

### 우선순위 1 — WO-APPENDIX-COLLECT-001 (별표 수집)

**왜**: 산안법 제16조 선임 기준이 시행령 별표3에 있는데 DB에 없음.
**선행 없이 D-004B 착수 불가.**

작업 내용:
1. `law_appendix` 테이블 DDL 생성 (apply_migration)
2. `law_article` 중 별표/별지/서식 포함 조문 확인
3. 별표 수집기 작성 (`law_appendix_collector.py`) — `law_collector.py` 수정 금지

성공 기준: 산안법 시행령 별표3 조회 시 "제조업 50인 이상" 등 행 존재

### 우선순위 2 — Track A/B diff 분석

`/refinery/run?limit=500` 실행 후 의무 목록 전체 글읽기:
- APPLICABLE + 사업주 의무 아닌 것 분류
- Track A 오염율 측정
- GPT 작업지시(WO-LEG-Compiler-003) 발행 필요 여부 판단

### 우선순위 3 — D-004B 설계 (별표 수집 완료 후)

현재 `NOT IMPLEMENTED` 상태 유지. 착수 조건:
- D-001~007 완료 ✅
- WO-APPENDIX-COLLECT-001 완료 (미완)
- Track A/B diff 분석 완료 (미완)
- 사장님 설계 승인 (미완)

---

## 절대 금지 (다음 세션도 유효)

```
삭제 금지 함수:
  evaluate_single_factory
  evaluate_draft_for_facility  
  fetch_compiler_candidates
  emit_stored_diagnosis_result (존재하지 않으나 참조 금지)

GPT 전속 테이블 (읽기만):
  constraint_node, numeric_constraint, rule_candidate
  executable_draft, draft_slot, compatibility_validation

D-004B 착수 금지 (별표 수집 선행 미완료)
```

---

## 커밋 이력 (15B~15C)

| SHA | 내용 |
|---|---|
| eb05e54 | D-006 Reverse Check 초기 |
| cd8e5e7 | D-006 status_filter 수정 |
| 0d35bef | D-007 Refinery |

기존 엔진 무결성: `/anonymous-diagnosis` 결과 변동 없음 ✅
