# Checklist Activation Work Log
## 2026-05-13

---

## 문제

inspection_set_items = 0건 (GAP)

## 분석

1. BUG-04 결정: 점검항목 자동생성 폐기
2. 안전관리자가 최초 1회 수동 세팅
3. checklist_item_candidate 802건 = 참조 풀 (template pool)

## 해결

Requirement Engine API 구현:
- GET /requirement/checklist-candidates: 후보 목록 조회
- POST /requirement/activate-checklist: 후보 → 실제 항목 전환

## 결과

체크리스트 활성화 경로 확보.
안전관리자 UI에서 candidate 선택 → inspection_set_items 생성 가능.
