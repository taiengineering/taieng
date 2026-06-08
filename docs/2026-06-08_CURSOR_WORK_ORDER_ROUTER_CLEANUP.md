# Cursor 작업 지시서 — 라우터 잔재 정리 (2026-06-08, v3 격리유지 정책)

> 분석 근거 문서: `docs/2026-06-08_ROUTER_AUDIT_ORPHAN_CLEANUP.md`
> 대상 repo: `taiengineering/tai-api`

## ★ 핵심 정책 (서비스 오픈 전)
- **모든 Phase는 격리(`_archive/routers_20260608/`로 이동)까지만 수행한다.**
- **실삭제(`git rm`)는 보류** — 서비스 오픈·안정화 이후 Phase 9에서 일괄 처리.
- 오픈 전이라 트래픽이 없으므로 "1일 달력 관찰" 대신 **능동 스모크 검증**으로 대체한다.
- 격리만으로 "런타임 제외 = 꼬임 해소" 목적은 즉시 달성되며, `_archive` 보존으로 즉시 복원 가능.

## 0. 절대 준수 사항 (위반 시 STOP)
- **건드리지 말 것:** `legal_engine`·`document_engine` 그룹 등록 모듈, law engine/판정 로직/스키마/rule data 일체.
- **보류(격리도 금지):** `legal_engine_v510.py`, `law_collector.py`, `law_collector_admrul.py`, `law_catalog_collector.py` — GPT 도메인. 별도 확인 전까지 그대로 둔다.
- **헬퍼 격리/삭제 금지:** `_messaging_compat.py`, `_rule_gen_prompts.py`, `matching_deps.py`, `health.py`.
- **자가판단 패치 금지:** 지시에 없는 판단이 필요하면 즉시 STOP하고 기획창에 보고.
- **각 Phase 완료 후 보고 → 승인 후 다음 Phase.** batch는 잘게.
- 작업은 브랜치 → PR. main 직접 push 금지.
- ⚠️ 정적 grep만 믿지 말 것 — `router_registry/__init__.py`는 `importlib.import_module()` 동적 로드. 격리 배포 + 스모크가 실질 검증.

## STD. 격리 표준 절차 (Phase 1~3 공통)
**1단계 — 격리**
1. `git mv routers/{name}.py _archive/routers_20260608/{name}.py` (`_archive/`에 `__init__.py` 만들지 않음).
2. commit → push → 병합 → 배포.

**2단계 — 격리 검증 (능동 스모크)**
3. `/health` 200 확인.
4. `/health` 모듈 상태(`MODULE_STATUS`)에 `degraded`·`failed_modules` 없음 확인.
5. `POST /cron/reload` 200 — 스케줄러 정상 등록 확인.
6. 핵심 경로 수동 스모크 1회씩: 진단 플로우, 인증, 결제. → 동적 import 강제 깨움.
7. Slack `#tai-alert`에 `ROUTER_LOAD_FAILURE` 없음 확인.
8. **이상 발생 시 즉시 직전 커밋 revert(파일 원위치) 후 STOP 보고.**

**3단계 — 실삭제: 보류** (Phase 9에서 일괄)

## Phase 0 — 진단 (완료)
- vulture + grep 전수 검사, 결과는 분석 문서 섹션 7 표에 누적.

## Phase 1 — Watch Engine 19개 (격리 완료)
- 상태: `_archive/`로 격리 완료, `external.py` 주석 블록 제거, 배포 검증 통과(10/10 loaded).
- 잔여 검증: FCM 스모크, Slack 무알림 확인.
- 실삭제: 보류 (Phase 9).

## Phase 2 — 버전 스텁 (격리만)
대상: `factory_process.py`, `factory_process_v2.py`, `oauth.py`, `auth_oauth.py`, `workers.py`
1. grep 참조 검사 (`oauth`/`auth_oauth`는 `auth.py` import 여부, `workers`는 `\bworkers\b` 경계).
2. 참조 0 확인분만 **STD 1~2단계(격리+스모크)**. 참조 발견 시 STOP 보고.
3. 실삭제 보류. **보고.**

## Phase 3 — 기타 orphan (격리만, Phase 0 통과분)
- 분석 문서 C그룹 ~30개 중 vulture+grep 참조 0 확인분만.
- `ksic_engine.py`: KSIC 기능 확인 전까지 보류.
- **5~10개씩** STD 1~2단계 격리. 배치마다 스모크 검증.
- 의심 시 개별 STOP 보고. 실삭제 보류.

## Phase 4 — fcm 중복 등록 정리 (완료)
- `saas_core`에서 `routers.fcm` 등록 제거 완료. `external` 유지, `routers/fcm.py` 파일 보존.
- 잔여: FCM 푸시 스모크 1건.

## Phase 9 — 최종 일괄 실삭제 (서비스 안정화 후)
- 서비스 오픈 후 충분히 안정 확인되면 `_archive/routers_20260608/` 전체 `git rm` → 배포 → `/health` 재확인.
- 이 단계는 **별도 승인 후** 진행.

## 배포·검증 공통 규칙
- `git push origin main` → 자동배포(1~2분).
- 배포 후 `/health` 200 필수. 503/`degraded`면 즉시 revert.
- `POST /cron/reload` 로 APScheduler 재기동.
- **`railway up` / `railway redeploy` CLI 금지.**
