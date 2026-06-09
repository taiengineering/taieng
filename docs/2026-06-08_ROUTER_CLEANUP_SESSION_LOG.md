# 라우터 잔재정리 작업 로그 — 2026-06-08

> 관련 문서: ROUTER_AUDIT_ORPHAN_CLEANUP / CURSOR_WORK_ORDER_ROUTER_CLEANUP(v3) / ROUTER_ORPHAN_RECLASSIFICATION_AND_PIVOT / CURSOR_WORK_ORDER_ROUTER_ROLLBACK
> 대상 repo: `taiengineering/tai-api`

## 1. 진행 요약 (타임라인)
전수검사 → 격리(실삭제 보류) → 잔여검증 → 재감사 → 방향전환(롤백) 순으로 진행. 서비스 오픈 전이라 "1일 관찰" 대신 능동 스모크로 검증, 실삭제는 Phase 9로 보류.

## 2. 실행 내역 (격리)
| Phase | PR | main | 격리 파일 | 비고 |
|---|---|---|---|---|
| 1 + fcm | #99 | 08ef37d (v6.0.2) | Watch Engine 19개 + external.py 주석 제거 / fcm은 saas_core에서 제거(external 유지) | rebase 시 docs/CONDITION_CODE_RAW_INVENTORY.md add/add 충돌 → 해당 docs 커밋 skip, 라우터 2커밋만 rebase |
| 2 | #100 | 5ee4958 | factory_process, factory_process_v2, oauth, auth_oauth, workers | |
| 3-1차 | #101 | 0696d77 | alert_messages, areas, buildings, contacts, debug, emergency_report, feature_flags, industry, posts, roles | |
| 3-2차 | #102 | fc63b09 | kin_generate, process_management, slack_kin, teams, uploads, workflow_integrity | |
| 3-3차 | #103 | fb4a88a | connect_provider, fix_matching_api, tbm_issue | |

- 아카이브 합계: **43개** → `_archive/routers_20260608/`
- git rm(실삭제): 0건 / `_archive`에 `__init__.py` 없음

## 3. 검증 내역
- 각 Phase 격리 후 공통: `/health` 200, `GET /` MODULE_STATUS 10개 그룹 정상(loaded==total, failed 0), `/cron/reload` 200, `/auth/login` 200, `/anonymous-diagnosis` 200. 503/degraded 0건 → revert 불필요.
- Phase 1 잔여검증:
  - FCM 스모크 **FAIL** — `POST /workers/push-test` 502 `FIREBASE_CREDENTIALS 미설정`. 라우터는 핸들러까지 정상 도달(404 아님) → **라우터 정리와 무관한 인프라 이슈**.
  - Slack #tai-alert 직접확인 불가(로컬 토큰 없음) / 간접정상(MODULE_STATUS failed 0이면 ROUTER_LOAD_FAILURE 미발송 구조).

## 4. 주요 발견
1. **FIREBASE_CREDENTIALS 미설정 (Railway tai-api)** → FCM 푸시 발송 불가. 라우터 정리와 별개 인프라 트랙(대표 처리 필요).
2. **미등록 orphan 대부분이 "완성됐는데 router_registry 미등록"** → 본 작업의 성격은 잔재 제거가 아니라 "미등록 완성 기능 처리(등록/폐기)". 실삭제 보류 정책이 완성 기능의 영구 삭제를 방지함.

## 5. 코드 실측 분류 (확정)
- 직접 확인한 완성 기능: ksic_engine, safety_reports, pw_reset, law_viewer, documents, document_forms, document_schema, document_runtime, kosha_collect, inspection_templates, areas
- 진짜 잔재: factory_process(202B), factory_process_v2(205B), diagnosis_input_draft(ROLLBACK 빈 파일)
- 이관완료(45cminc): Watch Engine 계열 19개

**최종 처리 분류 (55개 = 격리43 + 보류10 + 기획2)**
| 처리 | 개수 |
|---|---|
| _archive 유지(진짜 제거) | 22 (스텁2 + 이관완료19 + diagnosis_input_draft 1) |
| routers/ 복원 | 22 |
| 등록 검토(미등록 완성) | 11 |

## 6. 현재 상태 / 다음 단계
- 현재: main fb4a88a, `_archive`에 43개 격리.
- 발행됨: 롤백 지시서(`cleanup/router-rollback-20260608` — diagnosis_input_draft 격리 + 22개 복원).
- 다음: (a) 롤백 실행 → (b) 복원분·등록검토군 기능별 등록/폐기 결정 → (c) Phase 9 일괄 실삭제(서비스 안정화 후).
- 별도 트랙: FIREBASE_CREDENTIALS 설정 후 FCM 재스모크, Slack #tai-alert 육안 확인, docs/CONDITION_CODE_RAW_INVENTORY.md 충돌(GPT 도메인) 확인.
