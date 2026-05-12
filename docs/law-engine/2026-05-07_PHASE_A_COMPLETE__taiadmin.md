# PHASE A 완료 — master_rule_v2 테이블 생성 (2026-05-07)

> Phase A 작업 결과 기록. HANDOFF_2026-05-07.md 보충 문서.

## 생성 결과

| 요소 | 수 |
|---|---|
| 컬럼 | 44 |
| 인덱스 | 12 (PK + UNIQUE rule_code + sectors GIN + 9 보조) |
| CHECK 제약 | 7 |
| FK 제약 | 4 (source_clause/article/law + legacy_mblr) |
| 트리거 | 1 (updated_at) |
| 행 수 | 0 (변환 대기) |

## CHECK 제약 7개

1. `master_rule_v2_sectors_valid` — sectors는 4 sector 표준만 허용
2. `master_rule_v2_sectors_nonempty` — 최소 1개 sector 필수
3. `master_rule_v2_obligation_category_valid` — 8 enum (점검/작업_전/보고/서류/신고/선임/조치/기타)
4. `master_rule_v2_cycle_consistency` — cycle_type ↔ cycle_value/unit/base_event 일관성
5. `generation_method_check` — AUTO_REGEX/MANUAL/HYBRID
6. `generation_confidence_check` — 0.00 ~ 1.00
7. `status_check` — DRAFT/VALIDATED/ACTIVE/DEPRECATED

## FK 제약 4개 (출처 추적)

- `source_clause_id` → semantic_clause(id) ON DELETE RESTRICT
- `source_article_id` → law_article(id) ON DELETE RESTRICT
- `source_law_id` → law_master(id) ON DELETE RESTRICT
- `legacy_mblr_id` → master_building_legal_rules(id) ON DELETE SET NULL

## 인덱스 12개

```
master_rule_v2_pkey                              (PK)
master_rule_v2_rule_code_key                     (UNIQUE)
idx_master_rule_v2_sectors                       (GIN, 다중 sector 검색)
idx_master_rule_v2_source_clause                 (의미절 추적)
idx_master_rule_v2_source_law                    (법령별 룰 조회)
idx_master_rule_v2_obligation_category           (탭 필터)
idx_master_rule_v2_status                        (상태별 조회)
idx_master_rule_v2_needs_review (PARTIAL)        (검토 대기 룰)
idx_master_rule_v2_when_cycle                    (주기별 조회)
idx_master_rule_v2_industry (GIN)                (산업 매칭)
idx_master_rule_v2_equipment (GIN)               (설비 매칭)
idx_master_rule_v2_legacy_mblr (PARTIAL)         (legacy 매핑 추적)
```

## 시범 INSERT 검증

다중 sector ['BUILDING','CONSTRUCTION'] 정상 저장 + updated_at 트리거 정상.
삭제 후 0 rows 클린 상태로 정리됨.

## 4계층 흐름 진행도

```
[Layer 1] semantic_clause (58,495)        ← ✅ 완료
              │ (Phase B: 자동 변환)
              ▼
[Layer 2] master_rule_v2 (44 cols)         ← ✅ Phase A 완료, 변환 대기
              │ (Phase E: 법령엔진 API)
              ▼
[Layer 3] inspection_sets (324)            ← 🟡 Phase D: 4가지 세팅 컬럼 보강
              │
              ▼
[Layer 4] work_schedules (0)              ← ✅ 인프라 준비됨
```

## 다음 작업 (Phase B)

`docs/extraction/scripts/convert_clause_to_rule.py` 작성:
- DESIGN_master_rule_v2_2026-05-07.md의 7단계 알고리즘 구현
- semantic_clause → master_rule_v2 자동 변환
- 예상 결과: ~46,000건 변환 (VALIDATED ~30K, DRAFT ~16K)
