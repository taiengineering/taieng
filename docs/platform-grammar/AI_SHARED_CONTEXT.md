# TAI Platform — AI Shared Context

이 문서는 Claude 기획창, Claude Code, Cursor, GPT 등 모든 AI 도구가 참조하는 공통 컨텍스트.

---

## 1. 플랫폼 철학

TAI Safe는 B2B/B2G 산업안전 컴플라이언스 SaaS.
핵심 철학: 안전관리자 1인 집중 → 작업자 참여형 분산 관리.

Watch Engine은 TAI Safe의 **Business Flow Integrity Engine**.
Infra Monitoring이 아니다. Business Workflow Observability이다.

## 2. 절대 금지 방향

- Infra CPU/RAM/Network 모니터링
- APM 플랫폼
- Kubernetes operator
- AI 자동 복구 / self-healing
- LLM 기반 자동 추론
- 벡터DB / ML anomaly detection
- Full IAM / OAuth Provider
- CRM / Billing analytics
- Distributed tracing 플랫폼
- Grafana/Datadog 대체 시도

## 3. 현재 우선순위

1. Payment E2E
2. 진단→SaaS Setup 연결
3. SaaS 운영 E2E
4. Document MVP 10종
5. Worker UX 3~5초 응답

Watch Engine은 위 P0 작업의 **운영 안정성 기반**.

## 4. Watch Engine 구조

9개 레이어:
Event → Integrity → Incident → Alert → Recovery → Knowledge → Governance → Identity → Cockpit

17개 DB 테이블, 11개 라우터, 9개 Scheduler job, 18개 Cockpit 섹션.

상세: `docs/platform-grammar/platform-entity-map.md`

## 5. 용어 정의

상세: `docs/platform-grammar/core-language.md`

핵심 구분:
- Event ≠ Workflow (기록 vs 구조)
- Integrity ≠ Incident (탐지 vs 판단)
- Alert ≠ Notification (규칙 vs 전달)
- Governance ≠ Identity (조직 vs 개인)
- Recovery ≠ Automation (추천 vs 자동실행)
- Knowledge ≠ AI (축적 vs 추론)
- Stability ≠ SLA (종합 안정성 vs 시간 기준)

## 6. Cockpit 철학

Cockpit은 Dashboard가 아니다.
**Operational Control Surface**이다.

차이:
- Dashboard = 보기 전용
- Control Surface = 보기 + 판단 + 조치 + 기록

Cockpit에서 가능한 것:
- 이슈 확인/해결/무시
- 알림 규칙 설정/무음
- 복구 조치 기록
- 패턴 동기화
- 반복탐지 실행
- Telegram 테스트

## 7. 법령엔진과의 관계

법령엔진 = TAI Safe의 핵심 도메인 엔진 (Kiwi + rule-based)
Watch Engine = 법령엔진 포함 전체 서비스의 운영 무결성 감시

법령엔진의 절대 원칙 (No LLM, 법문 보존, 100% 매핑)은 Watch Engine과 독립.
Watch Engine은 법령엔진의 output을 event로 관찰할 뿐, 법령엔진 내부에 개입하지 않음.
