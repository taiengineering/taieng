# Watch Engine v1.1 — 운영 점검표

## 1. 필수 환경변수 (Railway)

| 변수 | 용도 | 필수 |
|------|------|:---:|
| `TELEGRAM_BOT_TOKEN` | Telegram 알림 발송 봇 토큰 | ⭐ |
| `TELEGRAM_CHAT_ID` | Telegram 알림 수신 채팅 ID | ⭐ |
| `SYNTHETIC_TEST_EMAIL` | Synthetic 로그인 테스트 계정 | ⭐ |
| `SYNTHETIC_TEST_PASSWORD` | Synthetic 테스트 비밀번호 | ⭐ |
| `SYNTHETIC_FACTORY_ID` | Synthetic 공정등록 대상 사업장 | ⭐ |

미설정 시: 해당 기능 skip (서비스 영향 없음)

## 2. Scheduler Job 목록 (5개, 모두 direct call)

| job_code | 주기 | 역할 |
|----------|------|------|
| INTEGRITY_EVALUATE | 5분 | integrity event 자동 평가 |
| ALERT_EVALUATE | 5분 | alert rule 기반 알림 발송 |
| SYNTHETIC_LOGIN | 5분 | 로그인 업무 heartbeat |
| SYNTHETIC_PROCESS_REG | 15분 | 공정등록 업무 heartbeat |
| SYNTHETIC_CLEANUP | 매일 3시 | synthetic 데이터 정리 |

## 3. Cockpit 접속 경로

```
admin.taieng.co.kr → 엔진감시 → Watch Engine
또는
admin.taieng.co.kr/html/horizontal-menu-template/watch-engine.html
```

## 4. UI에서 설정하는 항목 (DB 직접 수정 금지)

| 항목 | 위치 | 방법 |
|------|------|------|
| 알림 규칙 활성/비활성 | 알림 설정 섹션 | 🟢/⚪ 토글 |
| threshold (횟수/분) | 알림 설정 섹션 | 값 클릭 → prompt |
| cooldown (분) | 알림 설정 섹션 | 값 클릭 → prompt |
| 무음/해제 | 알림 설정 섹션 | 무음/무음해제 버튼 |
| 이슈 확인(ACK) | 활성 이슈 섹션 | 확인 버튼 |
| 이슈 해결 | 활성 이슈 섹션 | 해결 버튼 + 메모 |
| 이슈 무시 | 활성 이슈 섹션 | 무시 버튼 + 사유 |
| Telegram 테스트 | 알림 설정 섹션 | 테스트 버튼 |

## 5. 장애 시 확인 순서

1. **Cockpit 건강 요약 확인** — 전체 상태 (정상/주의/긴급)
2. **활성 이슈 확인** — CRITICAL 우선 확인
3. **Synthetic 심박 확인** — 마지막 성공 시간이 정상 범위인지
4. **스케줄러 상태 확인** — FAILED job 있는지
5. **최근 알림 이력 확인** — 발송 실패 있는지
6. **Railway 로그 확인** — `[CRON]` 로그 검색

## 6. Alert 폭탄 방지 구조

| 보호 장치 | 설명 |
|-----------|------|
| threshold | N회 이상 발생해야 알림 (1회 오류 무시) |
| cooldown | 같은 유형 알림 N분간 재발송 차단 |
| dedupe | 동일 rule+event_type 중복 발송 방지 |
| mute | UI에서 특정 규칙 임시 무음 |
| enabled | UI에서 규칙 완전 비활성화 |
| ignored | 이슈를 무시 처리하면 alert 대상 제외 |
| resolved | 해결 처리된 이슈는 alert 대상 제외 |

## 7. 전체 아키텍처

```
[Service] → emit_event() → business_event
                               │
              ┌─── scheduler (5분) ───┐
              │                       │
     INTEGRITY_EVALUATE         SYNTHETIC_LOGIN/REG
              │                       │
     Integrity Evaluator        Synthetic Runner
     flow_status + 4 rules      실제 API 호출
     false positive suppression  heartbeat 확인
              │                       │
     engine_integrity_event     business_event
              │
     ALERT_EVALUATE (5분)
              │
     Alert Engine
     rule matching + cooldown
     dedupe + mute 확인
              │
     Telegram 발송
     alert_history 기록
              │
     Founder Cockpit (30초 polling)
     - 건강 요약
     - 활성 이슈 (ACK/해결/무시)
     - 심박 상태
     - 스케줄러 상태
     - 위험 흐름 TOP
     - 알림 규칙 설정
     - 알림 이력
```

## 8. DB 직접 수정 금지 원칙

Watch Engine 운영에서 SQL을 직접 실행할 필요가 없어야 함.
모든 운영 행위는 Cockpit UI에서 수행.

예외:
- 신규 alert rule 추가 (초기 1회)
- flow_registry 초기 등록 (초기 1회)
- 비상 시 데이터 복구
