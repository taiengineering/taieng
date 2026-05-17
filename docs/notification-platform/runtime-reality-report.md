# Runtime Reality Report

작성일: 2026-05-17
범위: Notification Engine · 현실 vs 구조

---

## 현실 분류

| 영역 | 상태 | 근거 |
|---|---|---|
| Queue Runtime | ✅ 실제 사용됨 | scheduler 1분 polling, emit-test 동작 |
| Adapter (Telegram) | ⬜ 가설 | Bot token 설정됨, 실채널 미전달 |
| Adapter (SMS) | ⬜ 가설 | MessageMi 연동됨, 실발송 미확인 |
| Adapter (IN_APP) | ✅ 실제 사용됨 | notifications 테이블 insert 확인 |
| Adapter (Push) | ⬜ Mock | 로깅만 수행 |
| Feed UI | ⬜ 가설 | 배포 완료, 실사용자 접속 미확인 |
| Timeline | ⬜ 가설 | trace_id 저장, 실추적 미확인 |
| Quiet Hour | ⬜ 가설 | DELAYED 로직 완료, 실시간대 미테스트 |
| Retry/DLQ | ⬜ 가설 | 로직 완료, 실장애 미발생 |
| Event Wiring | ⬜ 가설 | 14 wiring 등록, 실이벤트 미연결 |
| Digest | ⬜ 가설 | Shadow mode, 실묶음 미발생 |
| Audience Resolver | ⬜ 가설 | DB resolve 구현, 실대상 미확인 |

---

## 요약

| 분류 | 건수 |
|---|---|
| 실제 사용됨 | 2 |
| 가설 (미검증) | 9 |
| Mock | 1 |

---

## 과도하게 확장됨 가능성

| 영역 | 위험 |
|---|---|
| Digest Runtime | 실사용 전 구조 완성 — 사용되지 않을 수 있음 |
| Event Wiring 14건 | 실이벤트 발생 전 등록 — 실제 필요 여부 미확인 |
| Platform Grammar 40+ 문서 | 운영 전 과다 문서화 가능성 |
| Policy 8건 | 실제 사용되는 정책 수 미확인 |

---

## 핵심

**현실과 구조를 분리해서 봐야 한다.**
구조가 완성되었다고 플랫폼이 동작하는 것이 아니다.
