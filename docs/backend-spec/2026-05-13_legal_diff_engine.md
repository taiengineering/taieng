# Legal Diff Engine
## 2026-05-13

## 역할
법령 객체의 구조적 변화만 분석. AI semantic inference 금지.

## Diff Types (8종)
- ARTICLE_ADDED / ARTICLE_REMOVED / ARTICLE_TEXT_CHANGED
- THRESHOLD_CHANGED
- APPENDIX_CHANGED / FORM_SCHEMA_CHANGED
- REQUIREMENT_RULE_CHANGED / ENFORCEMENT_DATE_CHANGED

## 예시
개정 전: 5000㎡ → 개정 후: 3000㎡ → `THRESHOLD_CHANGED`

## 절대 금지
- AI semantic meaning inference
- 유사 조문 자동 연결
- probabilistic estimation
