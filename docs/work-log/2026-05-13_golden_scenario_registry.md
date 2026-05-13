# Golden Scenario Registry
## 2026-05-13

## 예시
```json
{
  "scenario_code": "FIRE_BUILDING_6200",
  "domain_type": "FIRE",
  "input_payload": {"building_area": 6200},
  "expected_obligations": ["FIRE_MANAGER_REQUIRED"]
}
```

## 원칙
- deterministic truth dataset
- AI 학습 데이터 아님
- regression validation 전용
- supported_status: SUPPORTED/UNSUPPORTED/PARTIAL
