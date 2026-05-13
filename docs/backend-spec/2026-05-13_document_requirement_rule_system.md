# Document Requirement Rule System
## 2026-05-13

---

## 핵심 철학

TAI에서 문서는 "파일"이 아니다.
문서는 **"Requirement-backed Structured Data View"**이다.

## 2-Tier Requirement Rule

### MANDATORY
- 법령/필수 requirement
- 미충족 시: **문서 생성 불가** (`creatable: false`)
- UI: 빨간색, 생성 차단

### RECOMMENDED
- 권고/운영상 권장
- 미충족 시: **문서 생성 가능** + warning (`creatable: true`)
- UI: 노란색, 권고 표시

## API 응답 구조

```json
{
  "creatable": false,
  "mandatory_missing": [
    {"field": "pressure_value", "reason": "압력 측정값 누락"}
  ],
  "recommended_missing": [
    {"field": "additional_photo", "reason": "권장 사진 부족"}
  ]
}
```

## DB 테이블

`document_requirement_rule`
- form_code + field_code (UNIQUE)
- requirement_level: MANDATORY | RECOMMENDED
- evidence_type: PHOTO | SIGNATURE | CERTIFICATE | ATTACHMENT
- legal_basis: 법적 근거
- source_trace: DETERMINISTIC_RULE only (inferred/guessed 금지)

## 초기 데이터: 31건 (7종 서식)

| 서식 | MANDATORY | RECOMMENDED |
|------|-----------|-------------|
| OSHACT-FORM-002 | 4 | 2 |
| OSHACT-FORM-030 | 4 | 2 |
| FIRE-FORM-001 | 3 | 1 |
| FIRE-FORM-002 | 5 | 2 |
| ELEC-FORM-001 | 3 | 1 |
| GAS-FORM-001 | 3 | 1 |

## Hidden Mandatory Drift 방지

절대 금지:
- recommended 누락 시 reviewer reject 강제
- recommended 누락 시 자동 escalation
- recommended 누락 시 생성 차단
- UI 압박 wording
