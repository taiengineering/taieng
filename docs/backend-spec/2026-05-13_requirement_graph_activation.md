# Requirement Graph Activation
## 2026-05-13

---

## 핵심 발견

### inspection_set_items = 0 (GAP 1)

**설계 의도 확인:** BUG-04 결정에 따라 점검항목 자동생성 폐기.
안전관리자가 최초 1회 수동세팅하는 방식.

**활성화 경로:**
```
checklist_item_candidate (802건, 참조 풀)
    ↓ 안전관리자 선택
/requirement/activate-checklist API
    ↓ deterministic 전환
inspection_set_items (활성화된 점검항목)
```

### inspection_rule_mapping = 0 (GAP 2)

**현황:** inspection_sets에 이미 `legal_rule_id` (309/324건) 연결됨.
implicit 연결은 존재하지만 explicit 매핑 테이블이 비어있음.

**원인:** inspection_rule_mapping.rule_id는 UUID 타입이지만,
inspection_sets.legal_rule_id는 TEXT 코드(ex: 'OSHHIGH-004').
타입 불일치로 자동 매핑 불가.

### company_form_mapping = 0 (GAP 3)

회사별 커스터마이제이션 레이어 미구축.

## 구현 완료

### Requirement Engine v1.0.0

| Endpoint | 역할 | Boundary |
|----------|------|----------|
| GET /requirement/document-completeness | 문서 생성 가능 여부 평가 | DETERMINISTIC |
| GET /requirement/checklist-candidates | 체크리스트 후보 목록 | DETERMINISTIC |
| POST /requirement/activate-checklist | 후보 → 실제 점검항목 전환 | DETERMINISTIC_MANUAL |
| GET /requirement/obligation-graph | 의무 → 문서 → 체크리스트 그래프 | DETERMINISTIC |

## Mapping Graph 현황

```
obligation_form_mapping (11건)
    ↓
doc_rule_mapping (227건) + field_rule_mapping (1,615건)
    ↓
document_schema_candidate (323건)
    ↓
checklist_item_candidate (802건: 659 mandatory, 143 optional)
    ↓ 안전관리자 수동 선택
inspection_set_items (활성화 대기)
```
