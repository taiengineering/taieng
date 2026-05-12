# FN-06 요약 워크오더 — diagnosis-result-v2.html

**상세 문서:** `tai-api/docs/workorder-FN06-result-renderer.md`  
**의존:** BE-08 Transform API 완료 후 착수  
**우선순위:** P1

---

## 핵심 요약

| 항목 | 내용 |
|------|------|
| 신규 파일 | `diagnosis-result-v2.html` |
| API | `GET /diagnosis/{id}/result/transformed` 단일 호출 |
| 레이아웃 | 65/35 (좌: 의무사항 5탭, 우: ROI+스케줄+CTA) |
| 구성 순서 | 헤드라인 카드 → 경고 배너 → 의무 탭 → ROI 카드 → SaaS CTA → next_actions |
| 금기 | 엔진 API 직접 호출 금지 / 가격 하드코딩 금지 / 카카오 금지 |

---

## 의무사항 탭 5종

| 탭 | category 값 |
|----|-------------|
| 선임 | `선임` |
| 점검 | `점검` |
| 신고 | `신고` |
| 교육 | `교육` |
| 서류 | `서류` |

---

## ROI 카드 규칙

- `roi.penalty_max_krw` — font-size ≥ 32px, color #dc2626
- `roi.subscription_annual_krw` — API 응답값 그대로 (하드코딩 금지)
- `roi` null 시 섹션 숨김

---

## 엣지 케이스

- `schema_version` ≠ `v2026.04` → 재진단 유도 배너 + 렌더링 중단
- API 404/403/500 → 각각 안내 메시지 + 복구 버튼

---

## 완료 조건

- [ ] Transform API 단일 호출 (엔진 API 직접 호출 0건)
- [ ] 5탭 정상 분류 + 빈 탭 처리
- [ ] ROI 수치 API 기반 (하드코딩 0건)
- [ ] schema_version 불일치 graceful fallback
- [ ] 모바일 360px 가독성

---

## 실행 프롬프트

```
FN-06 착수. BE-08 완료 확인 후.
참고: tai-api/docs/workorder-FN06-result-renderer.md
신규: diagnosis-result-v2.html (main 브랜치 직접)
Transform API만 사용. 엔진 API 직접 호출 금지. 가격 하드코딩 금지.
```
