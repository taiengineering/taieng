---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-10 연동 상태 관제
version: 1
status: ACTIVE
owner: taiwang
---

# WO-10 — 연동 상태 관제 (IntegrationHealth)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-10
- **오브젝트:** integration_health_svc(신설) + 관제 엔드포인트
- **닫는 시나리오:** S27(연동 상태 한눈에)·S28(내부 API 헬스)

---

## 1. 현황 (실측)

| 테이블 | 성격 | 건수 |
|---|---|---|
| `internal_api_registry` | 자체 API 헬스체크 카탈로그(endpoint+expect_status+is_active) | 21 |
| `report_api_registry` | 외부 정부 API 연동 대장(system_name/apply_status/api_key_issued/env_var_name/api_base_url) | 20 |
| `law_external_catalog` | 법령 API 카탈로그(엔진 소관) | — |

- report_api_registry: APPROVED(키발급 완료: 건축물대장·도로명주소·법제처·산안공단·국세청 등), PENDING(신청중: 세움터·고용24·전기안전공사·화관법 등).
- **핵심 연동(결제·발송·PDF)은 이 대장에 없음** — 이니시스/팝빌/Gmail/MessageMi/Gotenberg는 별도 env로 관리.
- 제약: 컨테이너 네트워크 차단 → 실 probe는 배포된 tai-api가 수행. 어드민에서 트리거.

## 2. 설계 — 3축 관제

**`services/integration_health_svc.py`(신설):**

1. **핵심 연동 상태(env 점검)** — `core_integrations()`: 결제(INICIS_*)·증빙(POPBILL_*)·메일(GMAIL_SA_JSON+SENDER 또는 RESEND)·SMS(Edge)·PDF(Gotenberg)·프록시(OUTBOUND_PROXY)의 env 설정 여부 → configured/not_configured. 네트워크 불필요.
2. **정부 API 대장 집계** — `gov_api_status()`: report_api_registry에서 apply_status·api_key_issued 집계(APPROVED/PENDING 수, 목록).
3. **내부 API 헬스 probe** — `probe_internal(group?)`: internal_api_registry(is_active)에서 endpoint를 실제 GET 호출 → 상태코드 대조. tai-api 자기 도메인. 미서비스 그룹(수선/선임/컨설팅)은 제외 필터.

## 3. 엔드포인트

- `GET /integrations/health` — 핵심 연동 env 상태 + 정부 API 집계(1+2, 네트워크 불필요, 항상 응답).
- `POST /integrations/probe` — 내부 API 헬스 probe 실행(3, 선택 group). 실 HTTP.

## 4. 완료 판정 (IMPLEMENTED)

- integration_health_svc 3함수, 라우터, 등록.
- `/integrations/health`는 네트워크 없이 즉시 응답(env·DB 집계).
- probe는 배포 후 tai-api가 자기 엔드포인트 호출로 동작.
- `/health` 200, 배포 SUCCESS.

## 5. 산출물

1. `services/integration_health_svc.py`
2. `routers/integration_health.py`
3. router_registry 등록(external)
