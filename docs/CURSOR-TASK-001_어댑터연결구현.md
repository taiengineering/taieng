# CURSOR-TASK-001
# obligation_instance → 기존 45CM Adapter 연결 구현

**작성일:** 2026-06-24 | **대상:** Cursor / Claude Code (로컬 편집 → git push → Railway 배포)
**선행 문서:** docs/WO-OBLIGATION-ADAPTER-INTEGRATION-001_어댑터연결.md
**선행 규격:** docs/WO-CHECKENGINE-API-CONTRACT-001_CheckEngine연결규격.md

---

## 핵심 문장 (작업 중 항상 상기)

```
이 작업은 Applicability Engine을 기존 45CM Adapter 체인에
연결하는 Glue Code 작업이다.
Check Engine, Check Layer, Refinement Layer는 수정하지 않는다.
Glue는 판단하지 않고 변환만 한다.
```

---

## 목적

```
obligation_instance를
기존 build_obligations_from_trigger_candidates() 입력으로 변환하여
45CM Adapter 체인에 연결한다.

obligation_instance 95건
  → candidate 변환 (JOIN 1회)
  → 기존 Adapter 통과
  → obligations response 생성
```

---

## 금지사항

```
Check Engine 수정 금지       (services/check_engine_adapter.py 등)
정제레이어 수정 금지         (routers/diagnosis_transform.py)
Refinement Layer 수정 금지
cmc 수정 금지                (condition_mapping_candidate)
새 법령 분석 금지
새 Trigger 생성 금지         (trigger_generator/trigger_obligation_generator)
obligation_adapter_service 수정 금지  (기존 함수 그대로 호출만)
```

기존 무수정 호출 대상:
- `services/obligation_adapter_service.build_obligations_from_trigger_candidates()`
- `services/obligation_adapter_service.build_result_data()`

---

## 참조 문서

```
1. docs/WO-OBLIGATION-ADAPTER-INTEGRATION-001_어댑터연결.md
   - Glue 함수 완성형 (그대로 사용)
   - 공급 SQL
   - 전수 정합성 검증 결과 (95건 NULL 0)
   - executor='사업주' 필터 주의사항
   - Trace Log 규격

2. docs/WO-CHECKENGINE-API-CONTRACT-001_CheckEngine연결규격.md
   - Adapter Contract (candidate 입력 구조)
   - CheckVerdict / CheckResult 규격
   - Layer Boundary 정의

→ 위 두 문서를 먼저 읽고 시작할 것.
→ "왜 이 방식으로 붙였는지"의 근거가 거기 있음.
```

---

## 구현 파일

```
신규 1개:
  services/obligation_instance_adapter.py

수정 1개:
  routers/obligation_adapter.py  (엔드포인트 1개 추가만, 기존 함수 무수정)
```

---

## 구현 함수

### services/obligation_instance_adapter.py (신규)

```python
"""Applicability Engine(obligation_instance) → 45CM Adapter Glue.

원칙:
  - 변환만. 판단/필터/법령생성 없음.
  - FastAPI import 없음 (순수 서비스).
  - obligation_adapter_service 무수정 호출.
  - status='ACTIVE'는 Engine이 이미 정한 것 (새 판단 아님).
"""
from __future__ import annotations

from typing import Any, Dict, List

from db.supabase_client import get_supabase


def _confidence_band(value) -> str:
    """numeric confidence → HIGH/MEDIUM/LOW."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "MEDIUM"
    if v >= 0.9:
        return "HIGH"
    if v >= 0.8:
        return "MEDIUM"
    return "LOW"


def _fetch_instance_rows(factory_id: str) -> List[Dict[str, Any]]:
    """obligation_instance + semantic_clause JOIN rows (ACTIVE만).

    PostgREST 조인: obligation_instance.source_clause_id → semantic_clause.id
    """
    supabase = get_supabase()
    res = (
        supabase.table("obligation_instance")
        .select(
            "source_clause_id, trigger_type, trigger_l2, "
            "applicable_sectors, confidence, "
            "semantic_clause!inner(source_article_id, source_part_id, "
            "executor_text, condition_text, action_text, content_type)"
        )
        .eq("factory_id", factory_id)
        .eq("status", "ACTIVE")
        .execute()
    )
    return res.data or []


def obligation_instances_to_trigger_candidates(
    factory_id: str,
) -> List[Dict[str, Any]]:
    """obligation_instance → build_obligations_from_trigger_candidates() 입력.

    변환만 수행. 새 판단/필터/법령/Trigger 없음.
    """
    rows = _fetch_instance_rows(factory_id)
    candidates: List[Dict[str, Any]] = []
    for r in rows:
        sc = r.get("semantic_clause") or {}
        trigger_l2 = r.get("trigger_l2") or "UNIVERSAL"
        sectors = r.get("applicable_sectors") or []
        candidates.append({
            "clause_id": str(r.get("source_clause_id") or ""),
            "source_article_id": str(sc.get("source_article_id") or ""),
            "source_part_id": str(sc.get("source_part_id") or ""),
            "trigger_code": f'{r.get("trigger_type")}:{trigger_l2}',
            "executor_text": sc.get("executor_text"),
            "condition_text": sc.get("condition_text"),
            "action_text": sc.get("action_text"),
            "content_type": sc.get("content_type"),
            "sector": sectors[0] if sectors else None,
            "confidence": _confidence_band(r.get("confidence")),
        })
    return candidates
```

> 주의: PostgREST 임베디드 조인(`semantic_clause!inner(...)`)이 환경에서
> 동작하지 않으면, 2-step (obligation_instance 조회 → source_clause_id IN
> semantic_clause 조회 → dict 병합)으로 대체. 결과 candidate 형식은 동일.
> 직전 WO 문서의 "공급 SQL"을 RPC로 써도 됨.

### candidate 입력 규격 (기존 Adapter가 받는 형식 — 무수정)

```
clause_id, source_article_id, source_part_id, trigger_code,
executor_text, condition_text, action_text, content_type,
sector, confidence
```

정합성: 직전 WO에서 실측 95건 전수 검증 — 위 10필드 NULL 누출 0.

---

## 라우터 추가

### routers/obligation_adapter.py (엔드포인트 1개 추가)

```python
# 상단 import 추가
from services.obligation_instance_adapter import (
    obligation_instances_to_trigger_candidates,
)
from services.obligation_adapter_service import (
    build_obligations_from_trigger_candidates,  # 이미 import되어 있을 수 있음
)


@router.post("/from-instances/{factory_id}")
def adapt_from_obligation_instances(factory_id: str):
    """obligation_instance(Applicability Engine) → 45CM obligations.

    Glue: obligation_instance → candidate → 기존 Adapter.
    Check Engine / 정제레이어 무수정.
    """
    candidates = obligation_instances_to_trigger_candidates(factory_id)
    adapter_result = build_obligations_from_trigger_candidates(
        candidates, factory_id, trigger_codes=[]
    )
    return {
        "status": "ok",
        "factory_id": factory_id,
        "candidate_count": len(candidates),
        "obligation_count": adapter_result["obligation_count"],
        "verdict": adapter_result["verdict"],
        "obligations": adapter_result["obligations"],
        "source": adapter_result["source"],
    }
```

> persist(저장)까지 필요하면 기존 `/{factory_id}/persist` 패턴의
> `build_result_data()` + factory_diagnosis_results insert를 재사용.
> 단 이번 TASK 성공 기준은 obligations response 생성까지.

### 라우터 등록 확인

```
main.py 직접 import 금지 → router_registry/ legal_engine 또는
runtime_bridge 그룹에 spec 추가 (기존 obligation_adapter가 등록된 그룹과 동일).
obligation_adapter.router는 이미 등록되어 있으므로
같은 router에 엔드포인트만 추가하면 별도 등록 불필요.
```

---

## 테스트 factory

```
factory_id: e9c56af6-5de7-487d-bd2e-0d452291a562
  sector: INDUSTRIAL
  worker_count: 280
  obligation_instance: 95건 (batch WO-MVP-001-LIVE, status ACTIVE)

호출:
  POST /obligation-adapter/from-instances/e9c56af6-5de7-487d-bd2e-0d452291a562
```

---

## 성공 기준

```
obligation_instance 95건
  ↓ candidate 변환
candidate 95건 (10필드 채워짐)
  ↓ 기존 Adapter 통과 (executor='사업주' 필터로 ~2건 자연 제외)
obligations response 생성 (~93건)

확인:
  - candidate_count = 95
  - obligation_count ≈ 93 (executor 필터 반영)
  - verdict = APPLICABLE
  - obligations[].law_name / law_article / category 채워짐
```

기대 분포 (직전 WO 기준):
- UNIVERSAL family 93 / THRESHOLD family 2
- executor 비-사업주 2건 → Adapter 자연 제외

---

## Trace Log 기준

각 단계 기록 (입력 / 출력 / 건수 / 소요시간):

```
단계            입력              출력            건수    소요
──────────────────────────────────────────────────────────
fetch_rows      factory_id        oi+sc rows      95      ?ms
변환 (Glue)     rows              candidate       95      ?ms
Adapter         candidate         obligations     ~93     ?ms
response        obligations       JSON            ~93     ?ms

기록 위치: 응답 로그 또는 docs 후속 노트.
소요시간은 실제 호출 시 측정.
```

---

## 역할 경계

```
Cursor/Claude Code (이 TASK):
  - services/obligation_instance_adapter.py 생성
  - routers/obligation_adapter.py 엔드포인트 1개 추가
  - lint / 타입체크 / 로컬 테스트
  - main push → Railway 자동배포
  - 실제 factory 호출 → Trace Log 기록

수정 금지 (다른 소유):
  - Check Engine (GPT Compiler / facility_applicability 계보)
  - Check Layer (diagnosis_transform)
  - Refinement Layer
  - obligation_adapter_service (기존 함수 무수정 호출만)
  - Applicability Engine 매핑 로직 (cmc / obligation_instance 생성기)

Boundary 검증 (완료 후 자가확인):
  - Glue가 필드 변환만 했는가? (판단/필터/법령/Trigger 생성 0)
  - status='ACTIVE' 외 새 필터 없는가?
  - 기존 Adapter/Check Engine/정제레이어 diff 0인가?
```

---

## 완료 후 다음

```
이 TASK 완료 시:
  Applicability Engine이 45CM 체인에 정식 연결됨.
  → 이후는 구조 작업 아님.
  → Applicability Engine 품질(UNIVERSAL/THRESHOLD/EXISTS)만 고도화.
  → 구조 재수정 루프 위험 최소.

후속 후보 (별도 WO):
  - EXISTS 입력 수집 (진단 UI → facility_profiles has_*)
  - UNIVERSAL 215 HARVESTED 추가 정제
  - THRESHOLD 별표(appendix) 임계값 확장
  - 범위밖 2건(장애인고용/보험료) 결과 정리
```

---

*CURSOR-TASK-001. Glue Code 구현 인계장.*
*핵심: Glue는 판단하지 않고 변환만 한다. Check Engine/Check Layer/Refinement 무수정.*
*완성형 코드/SQL/검증은 docs/WO-OBLIGATION-ADAPTER-INTEGRATION-001 참조.*
