# WO-OPERATIONAL-INTEGRATION-001 — 기존 운영 Persist 재사용 (Execution)

**작성일:** 2026-06-26 | **상태:** 배선 설계 완료 + **TASK-004/005 검증에서 전제 불일치 발견** → 코드 푸시 보류(대표님 확인 필요)
**방법:** 기존 persist 호출부(routers/obligation_adapter.py)·HTML 리포트 코드 직독. 새 분석 없음.

> 목표: 171을 **기존 운영 Persist**로 factory_diagnosis_results에 태워 운영 파이프라인에 연결.

---

## Boundary

```
Applicability 변경  NO   Data Contract 변경  NO   Architecture 변경  NO   Breaking  NO
허용: 기존 Persist 재사용, 최소 배선 수정, 기존 함수 재사용
```

---

## ★ 검증 결과 핵심 (TASK-004/005) — 운영 읽기 경로가 둘로 갈린다

기존 HTML 리포트·SaaS의 실제 데이터 소스를 코드로 확인한 결과:

```
diagnosis_transform (웹 변환, BE-08)
    GET /diagnosis/transform/latest/{factory_id}
    → factory_diagnosis_results.result_data 읽음                 ✅ persist하면 도달

diagnosis_report (유료 HTML/PDF)
    GET /diagnosis/report-pdf/{public_token}
    → anonymous_diagnosis_results.full_result 읽음             ❌ factory_diagnosis_results 안 읽음
      (public_token 기반, full_result.rules_table/obligations 추출)

SaaS 점검항목관리
    → inspection_master(설비 템플릿, FK 0) prefill            ❌ 법령엔진 obligations 안 읽음
      (REFINEMENT-OUTPUT-MAPPING-001에서 기확정)
```

∴ 171을 factory_diagnosis_results에 persist하면 **diagnosis_transform**에는 도달하지만,
   **유료 PDF 리포트(anonymous_diagnosis_results)와 SaaS(inspection_master)에는 도달하지 않는다.**
   WO 전제 "diagnosis_report는 diagnosis_transform 결과를 출력한다"는 코드상 성립하지 않음(별도 파이프).
   → persist 배선은 정확하나, 완료 조건(→HTML→SaaS)는 코드상 재확인 필요.
```

---

## 배선 설계 (기존 Persist 재사용, 새 persist/router/service 0)

기존 `/persist`의 쓰기 블록(build_result_data → is_latest 토글 → insert)을 사설 헬퍼로 추출해
`/persist`와 `/from-instances`(옵션 persist=true)가 **동일한 기존 persist를 공유**.
검증: factories.sector(e9c56af6)=INDUSTRIAL 확인.

### Cursor 핸드오프 — routers/obligation_adapter.py (추가 2함수 + /persist 리팩터 + /from-instances 옵션)

```python
# (상단 import에 Optional 추가)
from typing import Any, Dict, Optional

# --- 신규 헬퍼 1: factory sector (from-instances용 sector 공급) ---
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

# --- 신규 헬퍼 2: 기존 persist 쓰기 블록 추출 (동작 동일) ---
def _persist_result_data(factory_id, sector, result_data, obligation_count, source) -> str:
    supabase = get_supabase()
    supabase.table("factory_diagnosis_results").update({"is_latest": False})\
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

# --- /persist 리팩터 (동작 동일, 쓰기 블록을 헬퍼로 교체) ---
#   result_data = build_result_data(adapter_result, v4_result)
#   sector = v4_result.get("facility_sector") or "INDUSTRIAL"
#   diagnosis_id = _persist_result_data(factory_id, sector, result_data,
#                      adapter_result["obligation_count"], "V4_OBLIGATION_ADAPTER")

# --- /from-instances 에 persist 옵션 ---
@router.post("/from-instances/{factory_id}")
def adapt_from_obligation_instances(factory_id: str, persist: bool = False):
    supabase = get_supabase()
    candidates = obligation_instances_to_trigger_candidates(factory_id, supabase)
    adapter_result = build_obligations_from_trigger_candidates(candidates, factory_id, trigger_codes=[])
    diagnosis_id: Optional[str] = None
    if persist and adapter_result["obligation_count"] > 0:
        sector = _factory_sector(factory_id)
        result_data = build_result_data(adapter_result, {"facility_sector": sector})
        diagnosis_id = _persist_result_data(factory_id, sector, result_data,
                          adapter_result["obligation_count"], "FROM_INSTANCES_OBLIGATION_INSTANCE")
    return { ... 기존 필드 ..., "persisted": diagnosis_id is not None, "diagnosis_id": diagnosis_id }
```

새 persist/engine/adapter/router/service 0. build_result_data·기존 쓰기 패턴 재사용. 기본 persist=false → 기존 동작 불변.

---

## 변경 Call Graph

```
obligation_instance → Glue → build_obligations_from_trigger_candidates (171, 불변)
  → [persist=true] build_result_data → _persist_result_data → factory_diagnosis_results
  → GET /diagnosis/transform/latest → diagnosis_transform → 171 읽음 ✅
  ✗ diagnosis_report(PDF)는 anonymous_diagnosis_results를 읽음 → 미도달
  ✗ SaaS는 inspection_master를 읽음 → 미도달
```

---

## 검증 기준 (171 보존)

```
171 obligations는 build_obligations_from_trigger_candidates 산출(불변).
persist는 그것을 저장만 함 → obligation 개수/verdict/reason/category/description 불변.
build_result_data 출력 ↔ diagnosis_transform._extract_obligations 입력: result_data.obligations 키 일치 → 171 읽힘(코드 근거).
```

---

## 먼저 확인이 필요한 점 (대표님 판단)

```
1. diagnosis_transform._fetch_latest_row는 created_by == user_id 권한 체크를 한다.
   기존 /persist는 created_by를 set하지 않음(null) → 인증 사용자 조회 시 403 가능.
   (기존 persist 동작 그대로. 본 WO가 만든 게 아니라 기존 속성.)
2. 유료 PDF 리포트는 anonymous_diagnosis_results를 읽음 → 171을 PDF에 보이려면
   그 파이프에 적재하는 별도 배선이 필요(본 WO 범위 밖, 별도 판단).
3. SaaS 점검항목은 inspection_master 파이프 → 법령엔진 obligations와 구조적 분리(기확정).
```

---

## 산출물

```
1. 변경 Call Graph     → 상기
2. 수정 파일 목록     → routers/obligation_adapter.py (persist 옵션, 상기 diff) — 푸시 보류
3. 실행 결과          → 코드 배선 준비 완료. live persist 호출은 배포 후 1회(환경 네트워크 off → 직접 호출 불가)
4. E2E 검증         → factory_diagnosis_results → diagnosis_transform 코드 계약 일치 확인.
                          HTML(PDF)·SaaS는 별도 파이프로 미도달(상기 핵심).
```

---

*WO-OPERATIONAL-INTEGRATION-001 — persist 재사용 배선 설계 완료. 단, HTML(PDF)=anonymous_diagnosis_results,*
*SaaS=inspection_master 별도 파이프로 확인됨. factory_diagnosis_results→diagnosis_transform만 연결됨.*
*거짓 완료 방지를 위해 코드 푸시 보류 — 대표님 확인 후 진행.*
