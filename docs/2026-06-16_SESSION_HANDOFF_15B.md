# 법령엔진 15차B 세션 핸드오프

작성일: 2026-06-16  
다음 세션 시작점: D-005 KSIC Signal Engine 착수

---

## 오늘 한 것

**WO-D-001~004A 완료 (Claude 직접 구현)**

| WO | 상태 | 코드 |
|---|---|---|
| D-001 SemanticClause Pipeline | ✅ 완료 | `semantic_clause_schema.py` / `semantic_clause_service.py` / `semantic_pipeline_api.py` |
| D-002 Common Sieve Engine | ✅ 완료 | `candidate_clause_schema.py` / `common_sieve_service.py` / `common_sieve_api.py` |
| D-003 Section Sieve | ✅ 완료 | `section_candidate_schema.py` / `section_sieve_service.py` / `section_sieve_api.py` |
| D-004A Track A Adapter | ✅ 완료 | `check_input_schema.py` / `check_engine_adapter.py` / `check_adapter_api.py` |

**실측에서 확인한 것 (오늘 가장 중요)**

1. `semantic_clause_fix` 실제 콼럼명: `source_article_id`, `source_text`, `sector` (WO 명세와 다름 — Claude가 DB 직접 확인해 수정)
2. Track A 파이프라인: `factories + draft_slot → facility_applicability` (SemanticClause와 무관한 별개 엔진)
3. D-004A는 facility_applicability rows를 읽어 CheckResult로 변환하는 힘(evaluate_single_factory 미수정)

**검증 결과**

- `/semantic-pipeline/clauses?limit=5` → 53,053건 확인 ✅
- `/common-sieve/run?limit=500` → keep:48, drop:321, pending:131 ✅
- `/section-sieve/run?facility_sector=INDUSTRIAL&limit=200` → 15개 ✅
- `/check-adapter/run-track-a?facility_id=e9c56af6-...` → 260개 CheckResult ✅
- 기존 anonymous-diagnosis 무결성 ✅ (D-001~004A 전후 동일 결과)

---

## 다음 세션 시작점

**WO-D-005: KSIC Signal Engine**

해당 파일:
- `schemas/ksic_signal_schema.py`
- `services/ksic_signal_service.py`
- `routers/ksic_signal_api.py`

시작 전 DB 확인 필요:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'process_noun_match_stats'
ORDER BY ordinal_position;
```

주의사항:
- KSICSignal은 의무 추가용 신호 (제거 근거 가능 금지)
- KSIC 신호 없어도 기존 CheckResult 유지

---

## 현재 router_registry/legal_engine.py 상태

```python
ROUTERS = [
    ...
    {"module": "routers.semantic_pipeline_api"},   # D-001
    {"module": "routers.common_sieve_api"},         # D-002
    {"module": "routers.section_sieve_api"},        # D-003
    {"module": "routers.check_adapter_api"},        # D-004A
    # D-005~007 미등록
]
```

---

## 절대 금지 (여전히 유효)

- evaluate_single_factory 수정 금지
- evaluate_draft_for_facility 수정 금지
- SemanticClause → facility_applicability_eval 연결 금지
- GPT 관리 테이블 (constraint_node 등) 수정 금지
- D-004B 착수 금지 (D-001~007 + APPENDIX 완료 후)

---

## 참고: 테스트용 factory_id

`e9c56af6-5de7-487d-bd2e-0d452291a562` (facility_applicability 260건 있음)
