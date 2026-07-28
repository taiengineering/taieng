---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-10 연동 상태 관제
version: 2
status: DONE
owner: taiwang
---

# WO-10 — 연동 상태 관제 (IntegrationHealth)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **오브젝트:** integration_health_svc + 관제 엔드포인트
- **최종:** VERIFIED.

---

## 1. 현황 (실측)

- `internal_api_registry`(21): 자체 API 헬스체크 카탈로그(endpoint+expect_status+is_active).
- `report_api_registry`(20): 외부 정부 API 대장. APPROVED 13(키발급 13)·PENDING 7.
- 핵심 연동(결제·발송·PDF)은 대장에 없음 → env로 관리. 컨테이너 네트워크 차단 → 실 probe는 tai-api가 수행.

## 2. 구현 (완료)

**`services/integration_health_svc.py`** (커밋 633a260):
- `core_integrations()`: 결제(INICIS)·증빙(POPBILL)·메일(GMAIL/RESEND)·SMS(Edge)·PDF(Gotenberg)·프록시(OUTBOUND_PROXY) env 설정 여부(configured/not_configured, critical 표시). 네트워크 불필요.
- `gov_api_status()`: report_api_registry 집계(APPROVED/PENDING/key_issued + 목록).
- `get_health()`: core + gov 종합. core_critical_missing로 필수 미설정 강조.
- `probe_internal(group, base_url)`: internal_api_registry endpoint 실 GET → 상태코드 대조. 미서비스 그룹(수선/선임/컨설팅/매칭/전문가/견적) 제외.

**`routers/integration_health.py`** (커밋 f630f43):
- `GET /integrations/health` — core env + gov 집계(네트워크 불필요).
- `POST /integrations/probe` — 내부 API 헬스 probe(실 HTTP).
- external 등록 1d83dfc.

## 3. 검증 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| gov_api_status 집계 | VERIFIED | SQL 대조: total 20, approved 13, pending 7, key_issued 13 — 코드 로직과 일치 |
| core_integrations env 점검 | VERIFIED | os.getenv 기반, 네트워크 불필요. 배포 SUCCESS |
| 미서비스 그룹 제외 | VERIFIED | _EXCLUDED_GROUPS 필터(수선/선임/컨설팅/매칭/전문가/견적) |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(1d83dfc) + `/health` |
| 내부 probe 실행 | PENDING | API_SELF_URL env 설정 후 실 호출(배포 tai-api가 자기 도메인 probe) |

## 4. 사람 게이트

- 내부 probe 실행하려면 Railway env `API_SELF_URL`(예: https://api.taieng.co.kr) 설정. 미설정 시 probe는 안내 메시지 반환(health는 정상).

## 5. 산출물 (커밋)

1. `services/integration_health_svc.py`
2. `routers/integration_health.py`
3. `router_registry/external.py` (integration_health 등록)
