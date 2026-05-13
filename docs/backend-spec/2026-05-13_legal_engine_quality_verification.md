# Legal Engine Quality Verification
## 2026-05-13

## 목적
법령 deterministic correctness 검증.

## 검증 대상
- obligation correctness
- threshold correctness
- requirement mapping correctness
- completeness correctness
- document/checklist linkage correctness

## Golden Scenario 확대 (5개 도메인, 12건)
| 도메인 | 시나리오 |
|--------|----------|
| FIRE | 3건 (6200/3500/900㎡) |
| ELECTRICAL | 2건 (300/50 kVA) |
| INDUSTRIAL | 3건 (300/50/5명) |
| GAS | 2건 (3t/500kg) |
| HAZARDOUS | 2건 (지정수량 초과/미달) |

## DB
legal_quality_verification 테이블 (PASS/WARNING/FAIL/UNSUPPORTED)

## 절대 금지
정답 추론 금지. golden scenario 기반 deterministic 비교만.
