# Legal Change Signal Cron
## 2026-05-13

## 구조
```
법제처 API → 변경 감지 → legal_change_event
                    → raw 수집 → legal_source_registry
                    → 후보 생성 → legal_intake_candidate
                    → 관리자 검토 대기
```

## Cron 실행
- 주기: 매일 1회 (03:30 KST 권장)
- Railway cron 또는 외부 scheduler
- 수동 실행: POST /legal-intake/run-cron (admin-only)

## Event Types (9종)
LAW_CREATED, LAW_REVISED, LAW_REPEALED,
ARTICLE_CREATED, ARTICLE_REVISED, ARTICLE_DELETED,
APPENDIX_REVISED, FORM_REVISED, ENFORCEMENT_DATE_CHANGED

## 절대 금지
- 자동 publish
- AI 법령 해석
- semantic fallback
- 유사 법령 매핑
