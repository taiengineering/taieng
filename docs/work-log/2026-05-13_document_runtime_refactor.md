# Document Runtime Refactor
## 2026-05-13

## 기존 방식 (폐기)
```
입력 → PDF 생성 → 파일 저장
```

## 신규 구조
```
Structured Runtime Data 저장
→ Requirement Engine 평가 (Mandatory/Recommended)
→ Web Rendering (HTML/WebView)
→ 필요 시 PDF 생성 (on-demand)
```

## Source of Truth
- DB runtime data = Source of Truth
- PDF = 출력 artifact only

## 구현
- document_requirement_rule 테이블 생성 (31건)
- Requirement Engine v2.0.0 업데이트
- /requirement/requirement-rules API 추가
- document-completeness API mandatory/recommended 분리 반환
