# WO-STEP1-OBLIGATION-MAPPING-001 — Mapping Adapter 구현 + 라이브 전환 보류 보고

**작성일:** 2026-06-27 | **상태:** 글루 함수 구현완료(아래) / 라이브 엔진 배선 **보류**(전제조건 미충족).
**판정: 매핑 함수는 준비됨. 그러나 지금 step1 엔진을 라이브 전환하면 소비자 진단의 99.98%가 깨짐 → 전환 보류 권장.**

> 정직 보고: 이번 WO의 매핑 함수(TASK-001~004)는 작성했다. 그러나 TASK-005(엔진 블록 교체)를 지금 라이브에 적용하면 성공기준 "Response 동일 / Consumer UX 변경 0"을 **위반**한다. 이유는 데이터·입력소스 두 가지(아래). 매핑은 형식 변환일 뿐, 데이터 부재/입력 미반영을 해결하지 못한다.

---

## ⛔ 라이브 전환 차단요인 (코드·데이터 직독)

### 차단 1 — obligation_instance 데이터 거의 없음 (치명)
```
전체 factories                         5,812
obligation_instance 보유 factory       1   (e9c56af6, 171행)
→ Applicability 전환 시 5,811개(99.98%) 시설이 빈 결과/오류.
```
Applicability 파이프는 사전 생성된 obligation_instance / 시설속성을 읽는다. 그 데이터가 1개 시설에만 존재 → 라이브 전환 즉시 대부분 소비자 진단이 0건.

### 차단 2 — 입력폼 미소비 (입력 구동 동작 상실)
```
레거시: body.input(근로자수·위험물·공사금액 등) → _evaluate_conditions 요청단위 평가 (입력 구동)
신규:   v4_evaluate(factory_id)/from-instances → DB 저장 시설속성·obligation_instance (factory_id 구동)
        ※ body.input 미사용. step1은 input을 factories/시설속성에 반영하지 않음.
→ 엔진 교체 시 사용자가 폼에 넣은 값이 진단에 반영되지 않음(같은 시설=입력 무관 동일 결과).
```
입력 반영하려면 "input→시설속성 브리지"가 필요하나, 본 WO는 `map_obligations_to_raw_leg` 1함수만 허용(Persist/Applicability 변경 NO) → **범위 밖**.

### 차단 3 — 역할 경계
`run_diagnose_step1_v510`은 `services/legal_v510_svc.py`(legal_engine 서비스 = GPT 전담). TASK-005 in-place 교체는 GPT 영역 → Claude는 매핑 함수(글루)와 정확한 diff만 제공, 엔진 서비스 직접 수정은 보류.

---

## TASK-001~004 — map_obligations_to_raw_leg() 구현 (허용된 단일 글루 함수, 준비 완료)
배치 위치 제안: `services/obligation_raw_leg_mapper.py` (신규 글루 모듈 1개 — WO 허용 범위).
```python
# services/obligation_raw_leg_mapper.py
"""WO-STEP1-OBLIGATION-MAPPING-001
Applicability/Obligation 출력 → 레거시 raw_leg 변환 (글루, 무판단).
새 법령/판단 생성 금지. 카테고리→버킷 분류 + 필드 복사만.
to_candidate_contract() 입력과 동형(필드명 불변).
"""
from __future__ import annotations
from typing import Any, Dict, List

# TASK-002 Category → bucket (확정 규칙 외 생성 금지)
_CATEGORY_TO_BUCKET = {
    "선임": "appointment_required",
    "점검": "inspection_required",
    "조치": "action_required",
    "신고": "report_required",
    "교육": "action_required",   # WO 지정
    "서류": "report_required",   # WO 지정
}

def _to_rule_item(o: Dict[str, Any]) -> Dict[str, Any]:
    """obligation → to_candidate_contract/_make_candidate 가 읽는 rule-dict 키 (가공 금지)."""
    title = o.get("title") or ""
    desc = o.get("description") or ""
    return {
        "rule_id": str(o.get("id") or o.get("source_clause_id") or ""),
        "law_name": o.get("law_name") or "",
        "law_article": o.get("law_article") or "",
        "article_title": title,
        "obligation_summary": title,
        "description": desc,
        "remarks": desc,
        "rule_type": o.get("rule_type") or "",
        # TASK-003 원본 보존(복사)
        "title": title,
        "category": o.get("category") or "",
        "risk_level": o.get("risk_level") or "MEDIUM",
        "evidence": o.get("evidence") or [],
    }

def map_obligations_to_raw_leg(
    obligations: List[Dict[str, Any]],
    *,
    sector: str = "",
    engine_version: str = "",
    evaluated_at: str = "",
) -> Dict[str, Any]:
    """obligations[] → 레거시 raw_leg (to_candidate_contract 입력 동형)."""
    buckets: Dict[str, List[Dict[str, Any]]] = {
        "appointment_required": [], "inspection_required": [],
        "action_required": [], "report_required": [],
    }
    for o in (obligations or []):
        if not isinstance(o, dict):
            continue
        bucket = _CATEGORY_TO_BUCKET.get(o.get("category") or "", "action_required")
        buckets[bucket].append(_to_rule_item(o))

    total = sum(len(v) for v in buckets.values())
    return {
        "engine_version": engine_version,
        "mode": sector,
        "evaluated_at": evaluated_at,
        "total_rules_checked": len(obligations or []),
        "not_applicable_count": 0,
        "applicable_count": total,
        "appointment_required": buckets["appointment_required"],
        "inspection_required": buckets["inspection_required"],
        "action_required": buckets["action_required"],
        "report_required": buckets["report_required"],
        "summary": {
            "total": total,
            "appointment": len(buckets["appointment_required"]),
            "inspection": len(buckets["inspection_required"]),
            "action": len(buckets["action_required"]),
            "report": len(buckets["report_required"]),
            "notify": 0,
        },
    }
```
※ `to_candidate_contract`는 4버킷(appointment/inspection/action/report_required)을 순회하므로 출력 동형. 미지정 카테고리는 action 폴백. risk/evidence는 복사 보존(다운스트림이 직접 읽진 않음).

## TASK-005 — 엔진 블록 교체 diff (GPT 적용 대상, 미적용)
`run_diagnose_step1_v510()` 내부:
```
[제거]  all_rules = fetch_diagnosis_rules(...)
        eval_ctx = normalize_input(inp); eval_ctx['sector']=sector_raw
        applicable, not_applicable = _evaluate_conditions(eval_ctx, all_rules)
        triggered={...}; _classify_rules_db(applicable, triggered); ... raw_leg={...}
[삽입]  obligations = <APPLICABILITY 파이프>(factory_id)         # ← 차단2: 입력 브리지 필요
        from services.obligation_raw_leg_mapper import map_obligations_to_raw_leg
        raw_leg = map_obligations_to_raw_leg(
            obligations, sector=sector_raw,
            engine_version=engine_version, evaluated_at=evaluated_at)
[불변]  to_candidate_contract(raw_leg) / presentation / persist / diagnosis_id / return
[주의]  하단 diagnosis_rule_results insert는 `applicable`(rule dict) 사용 →
        교체 시 obligations 기반으로 재작성 또는 생략 결정 필요(GPT).
```

## TASK-006/007 — 회귀·실행 검증 (현시점 결과)
```
POST URL / Response 구조 / diagnosis_id 방식 / candidate_contract 구조: 매핑상 유지 가능 ✓
그러나 실제 실행 시:
  - e9c56af6(유일 데이터 보유): 정상 동작 예상(171→버킷 분류)
  - 그 외 5,811개 시설: 빈 결과(obligation_instance 없음) ✗  → Contract Diff/UX 변경 발생
∴ "동일 Factory로 실행" 1건은 통과 가능하나, 운영 전체로는 PASS 불가.
```

## 최종 완료 조건 대조
```
Frontend 변경 0           ✓ (해당 없음)
URL 변경 0                ✓
Contract 변경 0           ✓ (매핑 동형)
Legacy Engine 제거 완료    ✗ 보류 — 제거 시 99.98% 시설 진단 0건
Applicability 전환 완료    ✗ 보류 — 데이터·입력 전제 미충족
Consumer UX 변경 0        ✗ 전환 시 위반(대부분 빈 결과)
```

## 전제조건 (전환을 PASS로 만들기 위한 선행 작업 — 별도 WO)
```
P1. obligation_instance 전 시설 생성(배치/온보딩) — 현재 1/5,812 → 대상 시설 커버.
P2. 입력 브리지: body.input → 시설속성 반영 후 Applicability evaluate (입력 구동 보존),
    또는 step1 입력 항목을 Applicability 평가 컨텍스트로 직접 주입.
P3. diagnosis_rule_results insert 경로 obligations 기반 재작성(GPT).
P4. created_by 보강(레거시 step1 persist는 created_by 없음 — 필요 시).
→ P1·P2 충족 후 본 매핑 함수로 라이브 전환 + e2e 회귀 시 PASS.
```

## 권고
```
지금 라이브 step1 엔진을 전환하지 말 것(소비자 5,800+ 시설 진단 붕괴 위험).
매핑 함수는 준비 완료(위) — 전제조건 P1·P2 충족 시 GPT가 엔진블록 교체 적용.
단계적 롤아웃: 데이터 보유 시설 화이트리스트 → 점진 확대 권장.
```

## Boundary 준수
```
Frontend/URL/API Contract/Response/DB Schema/Persist/Transform/Applicability/Generator/Trigger: 변경 0.
legal_engine 서비스(legal_v510_svc.py): 미수정(GPT 영역 — diff만 제공).
신규: map_obligations_to_raw_leg 1함수(허용 범위) — 라이브 미배선.
```

*WO-STEP1-OBLIGATION-MAPPING-001 — 매핑 함수 준비 완료. 라이브 전환은 데이터(1/5,812)·입력소스 전제 미충족으로 보류. P1·P2 후 GPT 배선 → PASS.*
