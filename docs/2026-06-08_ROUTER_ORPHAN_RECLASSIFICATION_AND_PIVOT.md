# 라우터 Orphan 재분류 및 방향 전환 — 2026-06-08

> 선행 문서: `2026-06-08_ROUTER_AUDIT_ORPHAN_CLEANUP.md`, `2026-06-08_CURSOR_WORK_ORDER_ROUTER_CLEANUP.md` (v3)
> 대상 repo: `taiengineering/tai-api`

## 0. 요약 (가장 중요)
당초 "미등록 orphan = 잔재"로 보고 43개를 격리했으나, 코드 실측 결과 **대부분이 "완성됐는데 router_registry에 연결만 안 된 기능"**이었다. 14번 반복 개발 중 파일은 만들고 등록을 빠뜨린 것이 누적된 것. 즉 본 작업의 성격은 "잔재 제거"가 아니라 **"미등록 완성 기능 처리(등록 복구 또는 폐기 결정)"**이다.

**실삭제를 보류한 격리 정책이 결정적으로 옳았다.** 즉시 `git rm` 했다면 `ksic_engine`(진단 입력 핵심)·`safety_reports`(이상신고)·`contacts`·`process_management` 등 완성 기능을 영구 삭제할 뻔했다. 현재 전부 `_archive/routers_20260608/`에 있어 복원 가능.

## 1. 보류 10개 분류 (코드 실측)
| 파일 | 크기/엔드포인트 | 판정 |
|---|---|---|
| diagnosis_input_draft | 내용 없음, ROLLBACK 주석만 | **진짜 잔재** |
| ksic_engine | /ksic-engine (업종·공정 4단계·검색) | 완성 — 진단 입력 핵심 |
| law_viewer | /law/article (조문·판례 조회, read-only) | 완성 |
| documents | /documents (문서 CRUD, services 의존) | 완성 |
| document_forms | /document-forms (법정 서식) | 완성 |
| document_schema | /document-schema (스키마 레지스트리) | 완성 |
| kosha_collect | /kosha-collect (KOSHA 수집 v1.6.0) | 완성 (배치) |
| inspection_templates | /inspection-templates (수동 점검 템플릿) | 완성 |
| document_runtime | 미확인 | 패턴상 완성 추정 |
| inspection_set_auto | 미확인 | 패턴상 완성 추정 |

## 2. 기획 판단 2개 (코드 실측)
| 파일 | 내용 | 판정 |
|---|---|---|
| pw_reset | /auth/pw-reset (SMS OTP 비번재설정, 완성) | 등록 후보. 단 auth.py 기존 비번재설정과 중복 점검 필요 |
| safety_reports | /safety-reports (이상신고 + 긴급 FCM, 완성) | 등록 후보. 근로자 참여형 안전관리 핵심 |

## 3. 격리한 43개 재감사 (크기 스캔 기반)
| 분류 | 개수 | 파일 |
|---|---|---|
| **명백 잔재** | 2 | factory_process(202B), factory_process_v2(205B) — 스텁 |
| **이관 완료(45cminc)** | 19 | watch_engine_* 12개, semantic_adapter_api, production_guard_api, control_runtime_gateway_api, synthetic_control_api, calibration_api, trans_engine_api, browser_synthetic |
| **중복 의심** | 3 | oauth(20KB), auth_oauth(7KB), workers(6KB) — 현역 auth.py·worker_registry 존재. 개별 확인 후 택일 |
| **완성 기능 의심** | 19 | alert_messages, areas, buildings, connect_provider(13KB), contacts(15KB), debug, emergency_report, feature_flags, fix_matching_api, industry, kin_generate, posts(13KB), process_management(15KB), roles, slack_kin, teams, uploads, workflow_integrity, tbm_issue |

※ "완성 기능 의심" 19개는 크기·이름 기반 추정이며, 개별 코드 확인 미완. 등록 복구 결정 전 파일별 확인 필요.

## 4. 방향 전환 — 권고
1. **격리 롤백:** "명백 잔재(2) + diagnosis_input_draft(1)" 와 "이관 완료(19)"만 `_archive` 유지. 나머지 21개는 `routers/`로 복원.
2. **성격 전환:** 이후 작업은 잔재 정리가 아니라 **기능별 의사결정** —
   - (a) 등록해서 살림 (router_registry 그룹에 추가)
   - (b) 현역과 중복이면 폐기
3. **등록 우선순위(완성·핵심):** ksic_engine, safety_reports, inspection_templates, documents/document_forms/document_schema, pw_reset(중복점검 후), law_viewer.
4. **중복 택일 대상:** oauth/auth_oauth(↔auth.py), workers(↔worker_registry).
5. **개별 확인 잔여:** document_runtime, inspection_set_auto + "완성 의심" 19개.

## 5. 근본 원인 및 재발 방지
- 원인: 라우터 파일 생성 후 `router_registry/{group}.py` 등록 단계 누락이 14회 반복 개발 중 누적.
- 재발 방지: 신규 라우터 PR 시 "그룹 파일 등록 + /health MODULE_STATUS 확인"을 체크리스트로 강제. 미등록 파일 정기 점검(grep: routers/*.py vs ROUTERS 목록 diff).

## 6. 현재 상태
- main: fb4a88a 기준, `_archive/routers_20260608/`에 43개 격리. 실삭제 0건.
- /health 200, 10개 그룹 정상.
- 다음: 본 문서 기준 "롤백 + 기능별 등록/폐기" 작업 지시서 작성 예정.
