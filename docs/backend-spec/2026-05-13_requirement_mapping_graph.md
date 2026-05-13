# Requirement Mapping Graph 검증
## 2026-05-13

---

## Mapping Graph 현황

### obligation → document
| 테이블 | 건수 | 상태 |
|--------|------|------|
| obligation_form_mapping | 11 | ✅ 활성 |
| doc_rule_mapping | 227 | ✅ 활성 |
| rule_doc_mapping | 0 | ❌ 미사용 |
| form_mapping_candidate | 68,642 | ✅ 대규모 후보 |
| field_rule_mapping | 1,615 | ✅ 활성 |

### document → checklist
| 테이블 | 건수 | 상태 |
|--------|------|------|
| inspection_sets | 324 | ✅ 활성 |
| inspection_set_items | 0 | ⚠️ GAP |
| checklist_item_candidate | 802 | ✅ 후보 활성 |
| checklist_coverage_candidate | 244 | ✅ 커버리지 후보 |
| inspection_rule_mapping | 0 | ⚠️ GAP |

### checklist → evidence
| 테이블 | 건수 | 상태 |
|--------|------|------|
| company_form_mapping | 0 | ⚠️ 회사별 매핑 미연결 |

## Mapping Graph 구조

```
사업장 입력 (factories)
    ↓
legal_context → 적용법령 결정 (deterministic)
    ↓
obligation_form_mapping (11건)
    ↓
doc_rule_mapping (227건) → 필수문서 결정
    ↓
field_rule_mapping (1,615건) → 필수필드 결정
    ↓
inspection_sets (324건) → 점검세트 결정
    ↓
checklist_item_candidate (802건) → 점검항목 후보
    ↓
evidence requirement → 필수증빙 결정
```

## 핵심 검증 결과

**"체크리스트가 문서 requirement 기반으로 생성되는가?"**

- obligation_form_mapping → doc_rule_mapping → inspection_sets 링크: **구조는 존재**
- inspection_set_items: 0건 → **실제 아이템 연결 미완료**
- checklist_item_candidate 802건이 inspection_set_items로 전환되지 않음

## GAP 해결 우선순위

1. **inspection_set_items 연결** — checklist_item_candidate → inspection_set_items 전환
2. **inspection_rule_mapping 연결** — 점검세트 → 법령조문 매핑
3. **company_form_mapping 연결** — 회사별 서식 매핑
