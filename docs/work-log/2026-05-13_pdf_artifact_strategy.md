# PDF Artifact Strategy
## 2026-05-13

## 원칙

PDF는 on-demand generation.

## 생성 조건
- 제출 (관공서 제출)
- 다운로드 (사용자 요청)
- 외부 제출 (이메일/API)
- 인쇄 (현장 출력)

## 생성 프로세스
```
1. Requirement Engine 평가 (mandatory 충족 확인)
2. Runtime Snapshot 생성 (immutable)
3. Gotenberg 렌더링
4. PDF artifact 반환
```

## Snapshot 구조
```json
{
  "checklist_values": [...],
  "evidence_references": [...],
  "signatures": [...],
  "timestamps": {...},
  "completeness_state": {
    "mandatory_fulfilled": true,
    "recommended_fulfilled": false
  }
}
```

## 절대 금지
- PDF를 Source of Truth로 사용
- Mandatory 미충족 상태에서 PDF 생성
- Snapshot 없는 PDF 생성
