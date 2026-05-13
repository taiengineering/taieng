# Checklist Activation UI
## 2026-05-13

---

## 페이지
`/html/runtime/checklist-activation.html`

## API 연결
- GET /requirement/checklist-candidates
- POST /requirement/activate-checklist

## UX 흐름
1. 안전관리자가 점검세트 선택
2. 후보 항목 목록 조회 (802건, 필수/선택 필터)
3. 체크박스로 항목 선택
4. "활성화" 버튼 클릭 → inspection_set_items 생성
5. confirm 확인 후 실행

## Deterministic Boundary
- 자동생성 금지 (BUG-04 설계 의도)
- AI 추천 금지
- 사람이 선택 후 활성화
