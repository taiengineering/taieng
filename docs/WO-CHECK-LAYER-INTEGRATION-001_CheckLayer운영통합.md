# WO-CHECK-LAYER-INTEGRATION-001 — Check Layer 운영 통합 (Execution)

**작성일:** 2026-06-26 | **상태:** 설계·핵심 구현 완료 → 전송 diff는 Cursor 핸드오프(프로덕션 430줄 파일)
**전제(재분석 안함):** 운영=obligation_adapter, trigger_diagnosis=비운영, six_w 운영 미배선 (VERIFY-001 확정)

> 목표: 새 엔진 0. 검증된 six_w_heuristic을 운영 Check Layer에 **옵션**으로 재사용 연결.

---

## Boundary / Freeze

```
Applicability 수정  NO   Glue 수정  NO   obligation_adapter 로직 변경  NO
Data Contract 변경  NO   Architecture 변경  NO   새 Engine/Adapter/Trace  NO
trigger_diagnosis 운영전환  NO
```

---

## 연결 대상 확정 (운영 Check Layer)

```
운영 Check Layer = routers/diagnosis_transform.py  ("Transform/정제 레이어")
  - factory_diagnosis_results.result_data 읽기전용 → 응답/HTML 변환
  - obligation_adapter·Glue·Applicability는 금지 목록 → 미터치
  - 그래서 6W 옵션은 이 Check Layer "내부"에서 기존 서비스 재사용이 유일한 경계준수 통합점
```

---

## TASK-001~003 — 재사용 구조 (복사/신규 없음)

```
Check Layer(diagnosis_transform)
  └─ _attach_six_w(obligations, supabase)         [신규, Check Layer 내부 얼릴글루]
       └─ services.trigger_six_w_service.extract_six_w_for_candidate()   [재사용]
            └─ engine.six_w_heuristic.extract_six_w()                    [재사용]

- 새 Engine/Adapter/Trace 작성 없음. trigger_diagnosis 6W 코드를 **import 재사용**(복사/중복 없음).
- 옵션(기본 OFF): include_six_w=true 일 때만 호출. 항상 호출 아님.
```

---

## 변경된 Call Graph (운영)

```
factory_diagnosis_results.result_data
  → diagnosis_transform._build_transform(row)        (기존, 불변)
  → [include_six_w=true 일 때만] _attach_six_w(obligations, supabase)
       → extract_six_w_for_candidate → extract_six_w
       → obligation에 six_w 키만 추가
  → 응답 (six_w 있으면 포함, 없으면 기존과 동일)
```

---

## six_w 연결 방식 (Cursor 핸드오프 — routers/diagnosis_transform.py 서지컬 3-편집)

### EDIT 1 — ObligationModel에 옵션 필드
```python
class ObligationModel(BaseModel):
    id: str
    category: str
    title: str
    risk_level: str
    description: str
    evidence: list[str]
    action_url: Optional[str] = None
    auto_schedulable: bool = False
    six_w: Optional[dict] = None   # WO-CHECK-LAYER-INTEGRATION-001 (옵션, 기본 None)
```

### EDIT 2 — Check Layer 내부 재사용 함수 추가 (_build_transform 근처)
```python
def _attach_six_w(obligations: list[dict], supabase=None) -> list[dict]:
    """Check Layer 6W 옵션 (WO-CHECK-LAYER-INTEGRATION-001).

    engine/six_w_heuristic.py를 services.trigger_six_w_service.extract_six_w_for_candidate
    경유로 재사용(복사/신규 엔진 없음). 부가 필드 six_w만 추가 —
    obligation 개수/verdict/reason/category 무변경. 실패 시 six_w=None(graceful).
    """
    try:
        from services.trigger_six_w_service import extract_six_w_for_candidate
    except Exception:
        for o in obligations:
            o["six_w"] = None
        return obligations
    for o in obligations:
        try:
            candidate = {
                "action_text": o.get("description") or o.get("title") or "",
                "condition_text": o.get("condition") or "",
                "trigger_code": o.get("trigger_code") or "",
            }
            o["six_w"] = extract_six_w_for_candidate(candidate, supabase=supabase)
        except Exception:
            o["six_w"] = None
    return obligations
```

### EDIT 3 — 두 엔드포인트에 옵션 파라미터 + 조건 호출
```python
@router.get("/{diagnosis_id}", summary="[BE-08] ID 기반 Transform")
async def transform_by_id(
    diagnosis_id: str,
    include_six_w: bool = Query(False),   # WO-CHECK-LAYER-INTEGRATION-001 (옵션)
    current_user: dict = Depends(get_current_user),
):
    row = await _fetch_row_by_id(diagnosis_id, str(current_user["id"]))
    result = _build_transform(row)
    if include_six_w:
        result["obligations"] = _attach_six_w(result["obligations"], get_supabase())
    logger.info(f"[BE-08] transform_by_id: diagnosis_id={diagnosis_id}")
    return result


@router.get("/latest/{factory_id}", summary="[BE-08] 시설 최신 진단 Transform")
async def transform_latest(
    factory_id: str,
    sector: Optional[str] = Query(None),
    stage:  Optional[str] = Query(None),
    include_six_w: bool = Query(False),   # WO-CHECK-LAYER-INTEGRATION-001 (옵션)
    current_user: dict = Depends(get_current_user),
):
    row = await _fetch_latest_row(factory_id, sector, stage, str(current_user["id"]))
    result = _build_transform(row)
    if include_six_w:
        result["obligations"] = _attach_six_w(result["obligations"], get_supabase())
    logger.info(f"[BE-08] transform_latest: factory_id={factory_id}")
    return result
```

파일 크기 18.8KB(~430줄) · 프로덕션 읽기 엔드포인트 → 메모리 규칙상 Cursor/로컬 편집 후 push 권장(MCP 전체덮어쓰기 위험 회피).

---

## TASK-004 — 회귀 (구조적 보장)

```
기본 include_six_w=False → _attach_six_w 문달 안 들어감 → 출력 바이트 동일.
  obligation 개수 171 → 171   (불변)
  verdict                     (불변)
  reason                      (불변)
  category                    (불변)
include_six_w=True 일 때도 _attach_six_w는 o["six_w"]만 set — 다른 키 미변경.
  ∴ 4개 항목은 옵션 상태와 무관하게 불변(추가만 수행).
```

---

## TASK-005 — HTML/SaaS 무파손

```
HTML(diagnosis_report.py)·SaaS는 include_six_w를 전달하지 않음 → 기본 OFF → 출력 동일.
six_w는 부가 키 → 옵션 ON이어도 기존 소비자는 미사용 키 무시, 깨지지 않음.
E2E 검증: 기본 OFF·부가적이므로 구조적 보장. 실제 live 호출 검증은 구동 서버 필요(본 환경 네트워크 off → 코드 근거로만 확인).
```

---

## TASK-006 — 운영 구조 확정

```
Applicability
  ↓
obligation_instance
  ↓
Glue (obligation_instance_adapter)
  ↓
obligation_adapter (obligation_adapter_service)
  ↓
Check Layer (diagnosis_transform)
    └─ six_w_heuristic (Option: include_six_w, 기본 OFF)
  ↓
Refinement
  ↓
HTML / SaaS
```

---

## 확정 사실 캐빗 (재분석 아님, VERIFY-001 결과)

```
- diagnosis_transform은 factory_diagnosis_results를 읽는다. 이를 쓰는 건 obligation_adapter /persist(V4).
- /from-instances(우리 171)는 persist 없음 → 현재는 result_data에 적재되지 않는다.
- 따라서 six_w 옵션은 "result_data에 적재된 obligations"에 부착된다. 171에 six_w를 보려면
  171을 factory_diagnosis_results에 persist하는 별도 배선이 선행되어야 한다(대표님 판단 사항, 본 WO 범위 밖).
- 이 WO는 Check Layer의 6W 옵션 연결까지 완료. persist 배선은 별도 WO.
```

---

## 산출물 체크

```
1. 운영 통합 결과        → Check Layer 옵션 통합(기본 OFF), 설계·diff 확정
2. 변경 Call Graph       → 상기
3. six_w_heuristic 연결  → extract_six_w_for_candidate 재사용(복사 없음)
4. 회귀 테스트          → 기본 OFF·부가적 → 171/verdict/reason/category 구조적 불변
5. E2E 검증           → 구조적 보장(live 호출은 구동서버 필요) + persist 캐빗 명시
6. WO 문서            → 본 문서
```

---

*WO-CHECK-LAYER-INTEGRATION-001 — 설계·diff 확정. 새 엔진 0, 재사용·옵션·기본OFF. 전송 편집은 Cursor(430줄 프로덕션 파일).*
