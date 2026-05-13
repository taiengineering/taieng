# Law API Collection Cron
## 2026-05-13

## 수집 대상 API
- 법제처 열린데이터 (open.law.go.kr)
- 현행법령 목록 API
- 법령 상세 API
- 조문 상세 API

## 수집 흐름
```
1. 변경법령 목록 조회 (promulgation_date 기준)
2. 기존 registry hash 비교
3. 신규/변경 → legal_change_event 생성
4. raw payload 저장 → legal_source_registry
5. 후보 생성 → legal_intake_candidate (REVIEW_REQUIRED)
```

## 현재 상태
- API stub 구현 완료
- 실제 법제처 API 키 연동 필요
- Railway 네트워크 egress 활성화 필요
