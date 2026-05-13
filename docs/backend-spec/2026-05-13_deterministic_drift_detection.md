# Deterministic Drift Detection
## 2026-05-13

## Drift 유형

### Obligation Drift
동일 input_hash에 대해 obligation 결과가 달라지는 상황.
- 어제: 12 obligations → 오늘: 15 obligations → CRITICAL

### Completeness Drift
동일 snapshot에 대해 문서 생성 가능 여부가 변경.
- mandatory_missing > 0인데 creatable=true → CRITICAL

### Hidden Mandatory Drift
recommended가 사실상 mandatory로 동작.
- recommended missing 시 reject 증가 → HIGH
- recommended usage 95%+ 강제화 → HIGH

### Soft-Null Contamination
- 빈 문자열, null-like, 깨진 파일, invalid signature

## 절대 금지
- 같은 입력 → 다른 결과 (deterministic 위반)
- AI가 obligation 변경
- semantic fallback으로 mapping 변경
