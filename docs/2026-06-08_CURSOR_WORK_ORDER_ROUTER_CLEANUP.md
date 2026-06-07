# Cursor 작업 지시서 — 라우터 잔재 정리 (2026-06-08)

> 분석 근거 문서: `docs/2026-06-08_ROUTER_AUDIT_ORPHAN_CLEANUP.md`
> 대상 repo: `taiengineering/tai-api`

## 0. 절대 준수 사항 (위반 시 STOP)
- **건드리지 말 것:** `legal_engine`·`document_engine` 그룹에 등록된 모듈, law engine/판정 로직/스키마/rule data 일체.
- **보류(삭제 금지):** `legal_engine_v510.py`, `law_collector.py`, `law_collector_admrul.py`, `law_catalog_collector.py` — GPT 도메인. 별도 확인 전까지 그대로 둔다.
- **헬퍼 삭제 금지:** `_messaging_compat.py`, `_rule_gen_prompts.py`, `matching_deps.py`, `health.py`.
- **자가판단 패치 금지:** 지시에 없는 파일·판단이 필요하면 즉시 STOP하고 기획창에 정확한 상황을 보고. 추측으로 진행하지 않는다.
- **각 Phase 완료 후 반드시 결과 보고 → 승인 후 다음 Phase 진행.** 한 Phase 안에서도 batch는 잘게 나눈다.
- 작업은 브랜치에서: `git checkout -b cleanup/router-orphan-20260608` → 작업 → PR. main 직접 push 금지.

## Phase 0 — 안전장치 & 전수 진단
1. 백업 브랜치 생성: `git checkout -b cleanup/router-orphan-20260608`
2. 정적분석 전수:
   - `pip install vulture`
   - `vulture routers/ --min-confidence 80 > /tmp/vulture_routers.txt`
3. orphan 후보별 참조 검사 (예시 명령):
   - `grep -rn "import {name}\|routers\.{name}" --include=*.py . | grep -v "routers/{name}.py"`
   - 결과가 0줄 → 死코드 후보 / 1줄 이상 → 보존 또는 추가 확인
4. 검사 결과를 `docs/2026-06-08_ROUTER_AUDIT_ORPHAN_CLEANUP.md` 섹션 7 표에 모듈별로 누적 기록.
5. **보고 후 Phase 1 진행.**

## Phase 1 — Watch Engine 19개 삭제 (이관 완료, 최저 위험)
대상 (`routers/`):
`watch_engine_api.py`, `watch_engine_alert_api.py`, `watch_engine_browser_api.py`, `watch_engine_sla_api.py`, `watch_engine_incident_api.py`, `watch_engine_recovery_api.py`, `watch_engine_governance_api.py`, `watch_engine_identity_api.py`, `watch_engine_control_api.py`, `watch_engine_document_api.py`, `watch_engine_intelligence_api.py`, `watch_engine_memory_api.py`, `semantic_adapter_api.py`, `production_guard_api.py`, `control_runtime_gateway_api.py`, `synthetic_control_api.py`, `calibration_api.py`, `trans_engine_api.py`, `browser_synthetic.py`

1. 위 19개 각각 grep로 **활성 코드**(등록된 routers/·services/·main.py) 참조 0 확인. `router_registry/external.py`의 주석 라인은 무시.
   - 참조 발견 파일은 제외하고 그 사실을 STOP 보고.
2. `router_registry/external.py`의 Watch Engine 주석 블록도 함께 삭제.
3. `git rm` 으로 참조 0 파일 삭제 → commit → push (작업 브랜치).
4. PR 병합 후 main 배포 → `/health` 200 확인. 503이면 즉시 직전 커밋 revert.
5. **보고.**

## Phase 2 — 버전 스텁 삭제
대상: `factory_process.py`, `factory_process_v2.py`, `oauth.py`, `auth_oauth.py`, `workers.py`
1. 각각 grep 참조 검사. 특히:
   - `oauth`/`auth_oauth`: `auth.py` 및 다른 모듈이 import하지 않는지 확인.
   - `workers`: `worker_registry` 와 혼동 주의 (`\bworkers\b` 단어 경계로 검색).
2. 참조 0 확인된 것만 `git rm`. 참조 발견 시 STOP 보고.
3. commit → push → 배포 → `/health` 확인.
4. **보고.**

## Phase 3 — 기타 orphan (Phase 0 검사 통과분만)
- 분석 문서 C그룹 ~30개 중 vulture + grep로 참조 0 확인된 것만 대상.
- `ksic_engine.py`: KSIC 기능 노출 여부 확인 전까지 **보류**.
- **5~10개씩** 나눠 삭제 → 배포 → 확인. 한 번에 전부 삭제 금지.
- 조금이라도 의심되면 개별 STOP 보고.

## Phase 4 — fcm 중복 등록 정리 (기획창 확정)
- `fcm`이 `saas_core`·`external` 양쪽 그룹에 등록됨.
- **확정: `external` 그룹 유지, `saas_core`에서 제거.** (FCM 푸시는 외부 연동 성격)
- 작업: `router_registry/saas_core.py`의 `{"module": "routers.fcm"}` 라인 1개 삭제. `external.py`의 fcm 등록은 그대로 둔다. `routers/fcm.py` 파일은 삭제하지 않는다.
- 배포 → `/health` 200 → FCM 알림 동작 1건 확인.

## 배포·검증 공통 규칙
- `git push origin main` → 자동배포(1~2분).
- 배포 후 `/health` 200 필수. 503이면 즉시 직전 커밋 revert.
- 배포 후 APScheduler 재기동: `POST /cron/reload`.
- **`railway up` / `railway redeploy` CLI 사용 금지.**
