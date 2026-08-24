# WP-FRONT-01 — NEW DEVELOPMENT GAPS

- baseline: tai-admin@0a61fe5e / tai-api@27970b61

## NEW 결정 규칙 (TRIGGER + BOUNDARY)

NEW는 **TRIGGER 조건이 성립하고 AND BOUNDARY 조건도 성립**할 때만 허용한다. TRIGGER만으로는 부족하다.

**TRIGGER** (아래 중 하나 이상)
- backend LIVE capability인데 이를 소비하는 UI가 없다
- 필수 사용자 flow가 중간에서 단절되었다
- 해당 업무의 user-facing UI 자체가 없다

**AND BOUNDARY** (아래 둘 다)
- 기존 화면으로 해당 업무 수행이 불가능하고
- 기존 화면의 합리적 확장으로도 해결할 수 없다

→ 기존 화면 확장이 가능하면 **NEW 금지 → MODIFY**. 단순 UX 개선/재디자인은 TRIGGER가 아니다.

이 규칙에서 equipment history(TRIGGER 성립, BOUNDARY 불성립=확장 가능)는 MODIFY-L, runtime document review queue(TRIGGER 성립 AND BOUNDARY 성립)는 NEW로 일관되게 갈린다.

---

## GAP-1. 설비 체크인 (flow H)

### 실측
- 백엔드: `equipment_checkins.py` LIVE. `POST /equipment-checkins`(익명 현장 스캔), `GET /equipment-checkins`(로그인 이력), `GET /equipment-checkins/{id}`.
- 프론트: tai-admin/vue3에 `/equipment-checkins` 호출 **0건** (code search 확인).

### 판정 — 2분할
1. **작업자 체크인 제출 UI** (POST, 익명 QR/RFID 스캔)
   - `POST /equipment-checkins`는 **인증 불필요**(현장 익명 접근 허용). 이 설계가 로그인 관리자용 tai-admin scope가 아님을 방증.
   - → **tai-admin NEW 금지**. 워커앱/PWA scope. (본 WP scope 밖)
2. **관리자 체크인 이력 UI** (GET, 로그인+회사스코프)
   - tai-admin scope. 현재 소비 0(UNUSED).
   - equipment-qr-manager가 이미 설비 목록 + QR/RFID 필드를 다룸 → 체크인 이력/상태/필터 **흡수 가능**.
   - → **MODIFY-L** (equipment-qr-manager 확장). 확장 불가 근거 없음 → **NEW 아님**.

### 게이트 결과
- TRIGGER 성립(backend GET LIVE, 관리자 이력 UI 없음). 그러나 BOUNDARY 불성립 — equipment-qr-manager의 합리적 확장으로 해결 가능. → **NEW 불성립, MODIFY-L**.

---

## GAP-2. Runtime Document 관리/검토 lifecycle (flow I/J 연장)

### 실측
- 백엔드 `document_engine_api.py v1.2.0` (prefix `/document-engine`) LIVE 엔드포인트 중 프론트 미소비(UNUSED):
  - `GET /documents` (factory/company/status 필터, 횡단 목록)
  - `GET /documents/{id}` (상세)
  - `POST /documents/{id}/status` — SUBMITTED_FOR_REVIEW / APPROVED_BY_HUMAN (reviewer 인증·원자 트랜잭션 강제)
  - `GET /transitions` (허용 상태전이 규칙)
  - `POST/GET /documents/{id}/evidence` (증빙 링크)
  - `GET /documents/{id}/audit-log` (감사 로그)
  - `GET /metrics`, `/metrics/factory/{id}` (메트릭)
- 프론트: document-forms는 `POST /documents`(생성), `PATCH /documents/{id}`(수정), `POST /documents/{id}/generate`(PDF) **3개만** 소비. 횡단 목록·상태전이·증빙·감사·메트릭 **전무**.
- engine-document는 서식 카탈로그(runtime 문서 아님).

### 게이트 판정
**TRIGGER** ✅ (성립)
- backend LIVE, UI 없음 — documents list / status / evidence / audit-log / metrics
- 필수 flow 단절 — 문서 생성 후 제출→검토→승인 lifecycle이 프론트에서 끊김

**AND BOUNDARY** ✅ (성립)
- 기존 화면 수행 불가 — document-forms는 **단건 작성 전용**(한 서식→한 문서→PDF). 여러 runtime document 횡단 조회·검토·승인 큐가 구조적으로 없음
- 기존 확장 불가 — 작성기(document-forms)와 검토 큐(관리자 review)는 **다른 사용자·다른 목적**. 작성기에 흡수하면 역할 혼재

### 결과 — **NEW 확정** (P1)
TRIGGER 성립 AND BOUNDARY 성립 → NEW.
- 신규 route: Runtime Document 관리/검토 화면
  - 생성 문서 횡단 목록(factory/status 필터)
  - 상태(DRAFT / SUBMITTED_FOR_REVIEW / APPROVED_BY_HUMAN ...)
  - 검토/승인 액션(POST /status, reviewer 인증)
  - 증빙 조회/등록(evidence)
  - 감사 이력(audit-log)
- 경계: **단건 작성 후속 상세만** 필요하면 document-forms MODIFY-L로 흡수 가능. 그러나 지시서가 명시한 cross-document review queue는 document-forms와 역할이 달라 NEW route 타당.
- flow I(증거)도 이 화면에 수렴 가능.

---

## GAP-3. (해당 없음) 그 외 flow

A~G, L은 화면+backend 양방향으로 닫혀 있다. K는 PARTIAL(알림 프론트 미조사)이지만 현재 NEW 근거는 없다. I/J의 runtime document 연장 영역은 GAP-2에서 별도 판정한다. 따라서 GAP-1(설비 체크인)·GAP-2(Runtime Document) 외 추가 NEW 근거 없음. 모두 KEEP 또는 MODIFY.

---

## NEW 최종 집계

| GAP | TRIGGER | BOUNDARY | 판정 |
|---|---|---|---|
| 설비 체크인 제출(작업자) | — | — | scope 밖(워커앱), NEW 금지 |
| 설비 체크인 이력(관리자) | 성립 | 불성립(확장 가능) | MODIFY-L |
| Runtime Document 관리/검토 | 성립 | 성립 | **NEW 확정** |

**tai-admin/vue3 scope 내 NEW = 1건** (Runtime Document 관리/검토 lifecycle).

초기 예상(대규모 신규개발)과 달리, 실측 결과 NEW는 1건이며 나머지는 기존 자산 정합성 보정(MODIFY)이다.
