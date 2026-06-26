# WO-OPERATIONAL-INTEGRATION-001 — 기존 운영 Persist 재사용 (Execution)

**작성일:** 2026-06-26 | **상태:** 배선 설계 확정 + **읽기경로 검증에서 전제 불일치 발견** → 코드 푸시 보류(대표 확인 필요)
**방법:** 기존 persist/transform/report 핸들러 코드 직독. TASK-004(HTML이 171 출력하는지)의 직접 결과.

> 목표: 171을 **기존 운영 Persist** 재사용으로 factory_diagnosis_results에 연결. 새 persist/engine/adapter 0.

---

## Boundary

```
Applicability 변경  NO   Data Contract 변경  NO   Architecture 변경  NO   Breaking  NO
```

---

## TASK-001/002 — 기존 Persist 재사용 배선 (설계 확정)

기존 `/persist`의 쓰기 블록(build_result_data → is_latest 토글 → insert)을 사설 헬퍼로 추출해
`/persist`와 `/from-instances`가 **동일한 기존 persist**를 공유. 새 schema/JSON 없음 — build_result_data 그대로.

### 변경 파일 (1개): routers/obligation_adapter.py
```python
# (추가) factories.sector 공급 — from-instances에는 v4_result가 없으므로
def _factory_sector(factory_id: str) -> str:
    try:
        supabase = get_supabase()
        res = (supabase.table("factories").select("sector")
               .eq("id", factory_id).limit(1).execute())
        if res.data:
            return str(res.data[0].get("sector") or "INDUSTRIAL").upper()
    except Exception:
        pass
    return "INDUSTRIAL"

# (추가) 기존 persist 쓰기 블록 추출 — /persist·/from-instances 공유 (새 저장로직 아님)
def _persist_result_data(factory_id, sector, result_data, obligation_count, source) -> str:
    supabase = get_supabase()
    supabase.table("factory_diagnosis_results").update({"is_latest": False}) \
        .eq("factory_id", factory_id).eq("sector", sector).eq("is_latest", True).execute()
    row = {
        "factory_id": factory_id, "sector": sector, "diagnosis_stage": 2,
        "input_data": {"factory_id": factory_id, "source": source},
        "result_data": result_data, "rule_count": obligation_count,
        "is_latest": True, "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ins = supabase.table("factory_diagnosis_results").insert(row).execute()
    if not ins.data:
        raise HTTPException(status_code=500, detail="factory_diagnosis_results 저장 실패")
    return str(ins.data[0].get("id"))

# (리팩터) /persist → _persist_result_data 사용 (동작 동일)
# (배선) /from-instances에 persist 옵션:
@router.post("/from-instances/{factory_id}")
def adapt_from_obligation_instances(factory_id: str, persist: bool = False):
    ...
    candidates = obligation_instances_to_trigger_candidates(factory_id, supabase)
    adapter_result = build_obligations_from_trigger_candidates(candidates, factory_id, trigger_codes=[])
    diagnosis_id = None
    if persist and adapter_result["obligation_count"] > 0:
        sector = _factory_sector(factory_id)
        result_data = build_result_data(adapter_result, {"facility_sector": sector})
        diagnosis_id = _persist_result_data(
            factory_id, sector, result_data,
            adapter_result["obligation_count"], "FROM_INSTANCES_OBLIGATION_INSTANCE")
    return {..., "persisted": diagnosis_id is not None, "diagnosis_id": diagnosis_id, ...}
```

기본 `persist=False` → 기존 /from-instances 동작 불변(JSON만). `persist=true` → 기존 persist 재사용 저장.

---

## 변경 Call Graph (제안)

```
obligation_instance
  → Glue (obligation_instances_to_trigger_candidates)
  → Adapter (build_obligations_from_trigger_candidates)        [171, 불변]
  → [persist=true] build_result_data → _persist_result_data    [기존 persist 재사용]
  → factory_diagnosis_results (is_latest=true)
  → diagnosis_transform (GET /diagnosis/transform/latest)       [읽음 — 코드 계약 일치]
```

---

## TASK-003 — diagnosis_transform 읽기 (코드 검증)

```
build_result_data 출력 result_data = {obligations, key_obligations, sector, rule_count, ...}
diagnosis_transform._extract_obligations(rd)는 rd["obligations"]를 읽는다.
∴ persist된 171 obligations는 diagnosis_transform이 수정 없이 읽는다. (데이터 계약 일치)

[캐빗] _fetch_latest_row는 created_by == user_id 권한 체크. 기존 /persist는 created_by 미설정
→ user 스肀코프 GET은 403 가능(기존 persist 동일 동작). 별도 읽기경로/service-role 확인 필요.
```

---

## TASK-004 — HTML Report 검증 (⚠ 전제 불일치 발견)

```
routers/diagnosis_report.py (유료 HTML/PDF, GET /diagnosis/report-pdf/{public_token})
  → supabase.table("anonymous_diagnosis_results").select("full_result, ...").eq("public_token", ...)
  → full_result.rules_table / obligations 를 읽음

∴ HTML PDF 리포트는 factory_diagnosis_results가 아니라 anonymous_diagnosis_results를 읽는다.
   → 171을 factory_diagnosis_results에 persist해도 유료 PDF 리포트에는 도달하지 않는다.
   → WO 고정 전제 "diagnosis_report는 diagnosis_transform 결과를 출력"과 코드 불일치.
```

---

## TASK-005 — SaaS 검증 (이전 확정 사실)

```
REFINEMENT-OUTPUT-MAPPING-001 확정: SaaS 점검항목관리는 inspection_master(설비 템플릿)로 prefill,
법령엔진 FK 0 → 구조적 분리. ∴ SaaS 점검은 factory_diagnosis_results obligations를 읽지 않는다.
```

---

## 검증 기준 (171 불변)

```
obligation 개수/verdict/reason/category/description:
  171은 build_obligations_from_trigger_candidates 산출(변경 없음). persist는 저장만 함.
  ∴ 5개 항목 구조적 불변. (PR #111 미병합 시 law_name 빈값 — 개수/verdict/reason/category/description과 무관)
```

---

## 완료 조건 vs 실제 (정직한 E2E)

```
Applicability → obligation_instance → Glue → obligation_adapter → Persist(기존) → factory_diagnosis_results
  → diagnosis_transform        : 연결됨 (코드 계약 일치, created_by 캐빗)
  → HTML(유료 PDF)            : 연결 안됨 (anonymous_diagnosis_results 별도 파이프)
  → SaaS 점검               : 연결 안됨 (inspection_master 별도 파이프)

→ persist 배선은 171을 factory_diagnosis_results→diagnosis_transform까지 정확히 연결한다.
   그러나 유료 HTML PDF·SaaS 점검은 서로 다른 테이블을 읽으므로 그것만으로는 도달하지 않는다.
```

---

## 수정 파일 목록 / 산출물

```
수정 대상(1개): routers/obligation_adapter.py (배선 옵션 + 기존 persist 재사용 헬퍼)
추가/수정 없음: obligation_adapter_service, Glue, diagnosis_transform, diagnosis_report, 템플릿
상태: 코드 diff 준비 완료(상기). 푸시는 위 HTML/SaaS 불일치 확인 후 대표 결정 대기.
```

---

*WO-OPERATIONAL-INTEGRATION-001 — persist 배선 설계 확정. 단, TASK-004 검증이 HTML/SaaS 별도 파이프를 드러냄 → 완료 선언 전 대표 확인 필요.*
