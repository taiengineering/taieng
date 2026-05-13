# Mandatory / Recommended Governance
## 2026-05-13

## 원칙

| 구분 | Mandatory | Recommended |
|------|-----------|-------------|
| 의미 | 법령 필수 | 권고/운영 권장 |
| 미충족 시 | 생성 불가 | 생성 가능 + warning |
| UI | 빨간 | 노란 |
| 결정 권한 | system (deterministic) | system (deterministic) |
| AI 개입 | 금지 | 금지 |

## Governance 규칙

1. requirement_level 변경은 법령 근거 변경 시만 허용
2. recommended → mandatory 승격은 legal_basis 필수
3. 운영상 편의로 mandatory 승격 금지
4. source_trace = DETERMINISTIC_RULE만 허용
