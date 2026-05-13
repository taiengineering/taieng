# Legal Correctness Density Expansion
## 2026-05-13

## Golden Scenario: 12건 → 50건

| 도메인 | SUPPORTED | UNSUPPORTED | 총계 |
|--------|-----------|-------------|------|
| FIRE | 10 | 0 | 10 |
| ELECTRICAL | 8 | 0 | 8 |
| INDUSTRIAL | 12 | 0 | 12 |
| GAS | 8 | 0 | 8 |
| HAZARDOUS | 7 | 1 | 8 |
| CONSTRUCTION | 4 | 0 | 4 |
| **총계** | **49** | **1** | **50** |

## Boundary Value 시나리오
- FIRE: 4999/5000/5001㎡
- ELECTRICAL: 74/75/76 kVA
- INDUSTRIAL: 49/50/51명
- GAS: 999/1000/1001 kg
- HAZARDOUS: 0.99/1.00/1.01 지정수량비

## Unsupported Coverage: 7건
ENVIRONMENT, NUCLEAR, MARINE, AVIATION, FOOD_SAFETY, MINING, HAZARDOUS(혼합)
