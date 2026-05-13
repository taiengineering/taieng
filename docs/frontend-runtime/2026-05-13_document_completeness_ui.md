# Document Completeness UI
## 2026-05-13

---

## 페이지
`/html/runtime/document-completeness.html`

## API 연결
- GET /requirement/document-completeness

## UX 흐름
1. 사업장 선택
2. 9종 법정서식 자동 평가
3. 생성 가능: 초록 카드 + "생성 가능" 배지
4. 생성 불가: 빨간 카드 + 누락 항목 표시

## 표시 예시
- ✅ 생성 가능 (required fields 12개 충족)
- ❌ 생성 불가 (사업장 정보 없음)

## Deterministic Boundary
- AI 판단 금지
- requirement 기반 completeness만 평가
