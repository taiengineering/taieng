# WO-REFINEMENT-DEDUP-001 — Refinement 출력 중복 병합 (Execution)

**작성일:** 2026-06-26 | **상태:** 설계·데이터 증명 완료 → 4-편집 Cursor 핸드오프(diagnosis_transform.py 430줄 프로덕션)
**대상:** routers/diagnosis_transform.py (운영 Check/Refinement 레이어)

> 목표: raw 171 그대로 보존, **화면 출력에서만** 동일 의무 병합 → 169 표시. Trigger 정보는 trigger_sources 배열로 보존.

---

## Boundary
```
Applicability 내부(Refinement 출력) YES   Boundary/Contract/Breaking  NO
새 Router/Engine/Service  NO   raw persist/HTML/PDF/SaaS/Glue/Generator 미터치
```

---

## 병합 키 실데이터 증명 (factory_diagnosis_results 0b43c1e1)
```
키 = (source_clause_id=id) + law_name + law_article
  raw_total 171  →  merged_groups 169  →  dup_groups 2   ✓ (WO 목표 일치)

중복 2건:
  66160e36 (관리대상 유해물질 저장)   trigger_codes [MATERIAL_ACT:HAZMAT, NONE:UNIVERSAL]
  f857f0f1 (접촉설비 부식방지)        trigger_codes [MATERIAL_ACT:HAZMAT, NONE:UNIVERSAL]
→ 병합 후 이 2건은 trigger_sources=[MATERIAL_ACT:HAZMAT, NONE:UNIVERSAL], 나머지 167건은 단일 코드.
```

---

## Cursor 핸드오프 — routers/diagnosis_transform.py (서지컬 4-편집, 추가적)

### EDIT 1 — ObligationModel에 trigger_sources 필드(옵션)
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
    trigger_sources: list[str] = []   # WO-REFINEMENT-DEDUP-001 (병합된 trigger 보존)
```

### EDIT 2 — _obligation_from_item 반환 dict에 3필드 추가(추가적, 기존 필드 불변)
`return { ... }` 의 끝에 추가:
```python
    return {
        "id": str(item.get("rule_id") or item.get("id") or uuid.uuid4()),
        "category": cat,
        "title": str(title or "의무사항"),
        "law_name": law_name,
        "rule_type": rule_type,
        "risk_level": (item.get("risk_level") or item.get("severity") or "MEDIUM").upper(),
        "description": str(item.get("description") or item.get("remarks") or item.get("detail") or ""),
        "evidence": evidence,
        "action_url": item.get("action_url"),
        "auto_schedulable": bool(item.get("auto_schedulable") or item.get("schedulable") or False),
        # --- WO-REFINEMENT-DEDUP-001 (병합 키/trigger 보존용, 추가적) ---
        "source_clause_id": str(item.get("id") or item.get("rule_id") or ""),
        "law_article": str(item.get("law_article") or "").strip(),
        "trigger_sources": (
            item.get("trigger_sources")
            or ([item["trigger_code"]] if item.get("trigger_code") else [])
        ),
    }
```

### EDIT 3 — 병합 함수 추가 (_extract_obligations 앞 또는 근처)
```python
def _merge_by_clause_law(obligations: list[dict]) -> list[dict]:
    """출력 직전 중복 병합 (WO-REFINEMENT-DEDUP-001).

    동일 (source_clause_id, law_name, law_article) → 1건으로 표시.
    병합 대상은 trigger 정보뿐 — trigger_sources 배열로 union.
    verdict/reason/description/category/title(obligation_summary)/law_name/law_article 불변(첫 항목 보존).
    raw는 건들지 않음(호출부에서 transform 결과 리스트에만 적용).
    """
    merged: list[dict] = []
    index: dict[tuple, dict] = {}
    for o in obligations:
        key = (
            str(o.get("source_clause_id") or o.get("id") or ""),
            str(o.get("law_name") or ""),
            str(o.get("law_article") or ""),
        )
        srcs = o.get("trigger_sources") or []
        existing = index.get(key)
        if existing is None:
            o["trigger_sources"] = list(dict.fromkeys(srcs))  # 중복제거·순서보존
            index[key] = o
            merged.append(o)
        else:
            for s in srcs:                                    # trigger만 union
                if s not in existing["trigger_sources"]:
                    existing["trigger_sources"].append(s)
    return merged
```

### EDIT 4 — _extract_obligations 마지막 return 직전 병합 적용
```python
    result.sort(key=lambda o: RISK_ORDER.get(o.get("risk_level", ""), 0), reverse=True)
    result = _merge_by_clause_law(result)   # WO-REFINEMENT-DEDUP-001: 출력 직전 병합 (171→169)
    return result
```

파일 18.8KB(~430줄)·프로덕션 읽기 엔드포인트 → 메모리 규칙상 Cursor/로컬 편집 후 push 권장(MCP 전체덮어쓰기 위험 회피).

---

## 회귀 검증 (TASK-006)
```
raw 171      factory_diagnosis_results.result_data.obligations — 미터치(메모리에서만 병합) ✓ 유지
display 169  병합 키(실데이터) 증명: 171→169 ✓
trigger 보존  trigger_sources 배열(병합 2건=[HAZMAT,UNIVERSAL]) ✓
불변 필드    verdict/reason/description/category/title/law_name/law_article — 첫 항목 보존, 미변경 ✓
HTML        diagnosis_report는 anonymous_diagnosis_results 읽음(별도 파이프) → 영향 0 ✓
기존 API     transform 외 엔드포인트 미영향. Data Contract 변경 없음(추가 필드만) ✓
```

## 참고 (이 WO 범위 밖, 기존 속성)
```
diagnosis_transform 인증 조회는 created_by==user_id 체크 → 시스템 persist row(created_by null)는 403 가능.
따라서 인증 HTTP로 display 169를 확인하려면 created_by 조치 필요(별도 WO). 병합 로직 자체는 실데이터로 171→169 증명됨.
```

---

*WO-REFINEMENT-DEDUP-001 — 설계·diff·데이터증명 완료. raw 171 보존, 표시 169, trigger_sources 보존. 전송 편집은 Cursor.*
