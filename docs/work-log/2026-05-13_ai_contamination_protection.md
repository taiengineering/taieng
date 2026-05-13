# AI Contamination Protection
## 2026-05-13

## 원칙

AI는 **suggestion only**. 절대 **decision authority** 금지.

## 탐지 대상

| 항목 | 탐지 방법 |
|------|----------|
| AI → mandatory 결정 | source_trace 검사 |
| AI → obligation 변경 | source_trace 검사 |
| AI → completeness override | source_trace 검사 |
| AI → automatic activation | source_trace 검사 |

## source_trace 금지값

```
AI_DECISION, INFERRED, GUESSED, SEMANTIC_FALLBACK
```

CHECK 제약으로 DB 레벨에서 차단.

## 허용 AI 영역

- 검색 보조, 자동완성, 추천, 문서 초안, UX 보조
- 단: decision authority 금지
