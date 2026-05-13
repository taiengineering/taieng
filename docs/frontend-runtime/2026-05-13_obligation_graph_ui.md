# Obligation Graph UI
## 2026-05-13

---

## 페이지
`/html/runtime/obligation-graph.html`

## API 연결
- GET /requirement/obligation-graph

## UX 흐름
1. 사업장 선택
2. 3칸 레이아웃: 의무사항 | 필수문서 | 점검세트
3. 각 노드에 상세정보 표시
4. 점검세트에 항목 수 표시 (0건이면 경고)

## 제한
- 관리자 전용 (visualization)
- 작업자 앱 연결 금지
- 운영 orchestration 금지
