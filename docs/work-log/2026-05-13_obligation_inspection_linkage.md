# Obligation ↔ Inspection Linkage
## 2026-05-13

---

## 현황

- inspection_sets: 324건 (309건 legal_rule_id 연결)
- inspection_rule_mapping: 0건 (explicit 매핑 테이블 비어있음)
- law_inspection_map: 10건

## 분석

inspection_sets는 이미 legal_rule_id(TEXT)를 가지고 있어 implicit 연결 존재.
inspection_rule_mapping.rule_id는 UUID 타입이라 직접 매핑 불가.

## Obligation Graph API

GET /requirement/obligation-graph?factory_id=xxx

응답:
```
{
  "obligations": [...],  // obligation_form_mapping
  "inspection_sets": [   // 사업장별 점검세트
    {"id": ..., "legal_rule_id": "OSHHIGH-004", "item_count": 0}
  ]
}
```

## 다음 단계

- inspection_rule_mapping에 TEXT 코드 기반 매핑 칼럼 추가 검토
- 또는 inspection_sets.legal_rule_id를 직접 활용 (이미 연결됨)
