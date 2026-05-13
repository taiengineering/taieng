# Document Completeness Engine
## 2026-05-13

---

## 역할

```
현재 데이터 상태
→ requirement completeness 평가
→ 부족 requirement 안내
→ 문서 생성 가능 여부 판단
```

## API 응답 예시

```json
{
  "creatable": false,
  "missing": [
    {"field": "pressure_value", "reason": "압력값 누락"},
    {"field": "photo", "reason": "사진 1개 부족"},
    {"field": "signature", "reason": "서명 없음"}
  ]
}
```

## Deterministic Boundary

| 구분 | 허용 | 금지 |
|------|------|------|
| 필수필드 충족 평가 | ✅ deterministic | ❌ |
| 문서 생성 가능 판단 | ✅ deterministic | ❌ |
| 부족 항목 안내 | ✅ deterministic | ❌ |
| 필수 여부 추측 | ❌ | ✅ AI 금지 |
| 채우기 추천 | ❌ | ✅ decision 금지 |

## 데이터 기반

- obligation_form_mapping: 11건 (의무 → 서식)
- field_rule_mapping: 1,615건 (필드 → 법령)
- doc_rule_mapping: 227건 (문서 → 법령)
- checklist_item_candidate: 802건 (체크리스트 요구사항)
