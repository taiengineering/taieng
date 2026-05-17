# Channel Purpose Boundary

작성일: 2026-05-17
범위: 채널별 역할 경계

---

## 채널 역할

| Channel | Purpose | 대상 |
|---|---|---|
| IN_APP | 일반 운영 알림 (Feed) | 전체 로그인 사용자 |
| PUSH | 모바일 알림 | 앱 사용자 |
| SMS | 긴급 접근성 | 전여 전화번호 |
| TELEGRAM | 실시간 운영 알림 | 운영자/안전관리자 |
| EMAIL_GMAIL | 공식 문서 전달 | 관리자/대표 |
| ALIMTALK | 비즈 공식 알림 | 결제/계약 당사자 |
| SLACK | 운영 협업 | 내부 운영팀 |
| WEBHOOK | 외부 연동 | 외부 시스템 |

---

## 규칙

1. **채널 역할 혼합 금지** — Slack으로 결제 알림 발송 금지
2. **Purpose 일치** — 긴급은 SMS, 비즈는 ALIMTALK, 운영은 TELEGRAM
3. **대상 일치** — 작업자는 PUSH, 운영자는 TELEGRAM
4. **Fallback 허용** — primary 실패 시 secondary로 전환 (Phase 2)
