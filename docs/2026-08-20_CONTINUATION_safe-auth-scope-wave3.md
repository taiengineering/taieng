# CONTINUATION — safe auth·scope (Wave 3 진행중 · 직접MCP)

> 2026-08-20 기획창. 선행: `2026-08-20_HANDOFF_safe-auth-scope-wave1-done.md` · `2026-08-20_CONTINUATION_safe-auth-scope-wave2.md`(Wave2 중간) · 설계 `2026-08-20_safe-auth-scope-module-design.md`. 이 문서 = **Wave 2 완료 + Wave 3 진행 스냅샷**. 새 창은 이 문서만 열면 이어감.

## 작업 방식 (고정)
- **Cursor 미사용. 직접 MCP만.** 절차: fresh `github-1_get_file_contents`(sha 확보) → 전체 파일 재작성 `github-1_create_or_update_file`(sha 필수, 전체본만) → **배포 SUCCESS로 무결성 확인**.
- 배포 폴: `railway_list_deployments`(project `7c3ab53b-feb6-40a4-a4f0-7ade3f6e524b` / service `4cf52678-1fbf-42f4-8bd7-f59fab98c3ae` / env `9dacb6f0-5d2a-4064-839e-e050af50bf30`, 3개 다 필수). BUILDING/INITIALIZING→DEPLOYING→SUCCESS. 커밋마다 배포 큐잉, 최신이 라이브·나머지 REMOVED.
- 재현 무결성: 크기 delta가 추가 스코프 라인과 일치하는지 확인. `\uXXXX` 이스케이프·오타는 verbatim 보존.
- 운영자 지시: 컨텍스트 문제 제기 금지. 단답 승인("계속")이면 다음 라우터 진행.

## ✅ 완료·배포 SUCCESS (tai-api main)
```
ef547c8  company_scope 헬퍼 2개(require_company_id, scoped_list_company)
7c61574  companies          03e1350  documents          6d5a89a5 미출시 9개 격리
f3ea782  safety_meetings    9189875  work_schedules
326fc5e  risk_assessments   4f01094  ra_items           2e5666c  ra_report
79e7228  ra_settings        9ee5c09  overdue_checker    d075700  tbm      ← Wave2 완료(전부 SUCCESS 확인)
a7ffb24  subcontractors     dbc01bb  equipment_assets   535fdef  equipment_checkins  ← Wave3 (배포 DEPLOYING, SUCCESS 확인 필요)
```
**다음 창 첫 폴**: `a7ffb24`·`dbc01bb`·`535fdef` SUCCESS 확인(직접 재작성 무결성 최종). FAILED면 직전 커밋으로 원복.

## 스코프 패턴 (확립)
- 생성: `_forced = require_company_id(current, sb); if _forced: body.company_id = _forced` (비-ALL 토큰강제·무회사 403 / ALL은 body·derived 폴백)
- 목록: `scoped_cid, deny = scoped_list_company(current, sb, company_id); if deny: 빈결과; company_id = scoped_cid`
- 단건: 행 company_id 조회 → `_ensure_own_company(cid, current, sb, msg)` (변경·삭제 前 선행)
- **부모경유 자식**: `_ensure_assessment_own`/`_ensure_item_own`/`_ensure_control_own`(ra_items), `_ensure_site_own`/`_ensure_sub_own`(subcontractors), `_ensure_asset_own`(equipment_assets)
- **factory→company**(직접 company_id 없는 테이블): `_ensure_factory_own(sb, factory_id, current)` + 목록은 `_own_factory_ids(sb, current)`(ALL→None전체 / 무회사→[] / else 자사 factory id들 → `.in_("factory_id", own)`)
- 배치 id목록: `_owned_ids(sb, ids, current)` 타사 skip
- ALL 전용(전사 집계 뷰): `_require_admin(current, sb)` (equipment_assets `/overview`)
- 공개 유지 예외: tbm 서명(sign-info/sign/register_sign), equipment_checkins `POST`(현장 익명 스캔), overdue `/check`(cron), ra `policy-params`(법정상수), equipment `/model/search`(마스터 카탈로그=로그인만)
- import: `from routers.auth import get_current_user` + `from services.company_scope import (...)`. `current: dict = Depends(get_current_user)`.
- 헬퍼는 `services/company_scope.py`에서 가져오거나 라우터 상단 로컬 정의(`_own_factory_ids` 등). company_scope.py 자체는 ADDITIVE만.

## ▶ 다음 작업 = corrective_actions (읽음, 편집 대기)
`routers/corrective_actions.py` v1.1.0, prefix `/corrective-actions`, tag 이창보고서. **sha `4f317578a15b8474fa2079c5accf14847cafe13f`, 8490B.** 테이블 `corrective_actions`에 **factory_id·company_id 직접 보유**. 3 엔드포인트 전부 무인증 → 배선:
- **import 추가**: `Depends`, `get_current_user`, `_ensure_own_company`, `_ensure_factory_own` (`_scope`,`_is_admin`는 목록 company 스코프에 사용).
- **GET `` list_corrective_actions**: `current` 추가. company_id 컬럼 존재하므로 —
  - `factory_id` 주면 `_ensure_factory_own(sb, factory_id, current)` + `.eq("factory_id",...)`
  - else 비-ALL이면 `cid=current.company_id; if not cid: 빈결과; q=q.eq("company_id", cid)` (ALL은 무필터). equipment_checkins get_checkins 패턴 그대로.
  - `_normalize()` 및 status/assignee or_ 필터·페이지네이션 **verbatim 보존**.
- **POST `` create_corrective_action**: `current` 추가. `_forced = require_company_id(current, sb); if _forced: body.company_id = _forced` (import에 `require_company_id`도 추가). body.factory_id 주어지면 `_ensure_factory_own`도 선택. row 조립(assigned_user_id↔assignee_id, status↔status_code 동기화) verbatim.
- **PATCH `/{action_id}` update_corrective_action**: `current` 추가. 현재 `chk`가 `select("id")` → **`select("id, company_id")`로 바꾸고** not-found 후 `_ensure_own_company(chk.data[0].get("company_id"), current, sb, "이창을 찾을 수 없습니다.")`. payload 동기화 로직 verbatim.
- 커밋 후 배포 SUCCESS 확인.

## Wave 3 잔여 (corrective_actions 다음)
`inspection_checklist` · `inspection_sets` · `inspection_setup` · `construction_workflow_router`(33KB, 대형—여유시) · `safety_template` · `tbm_templates`
- 대부분 factory→company 또는 부모경유. inspection_* 는 inspection_set/schedule 부모 체인 예상 → 읽고 판단.

## Wave 4
`org` (부서→팀→그룹; teams/groups 직접 company_id 없음 → 부모 부서→회사 체인, 최고난도). 읽고 부모 컬럼 확인 후 설계.

## 격리 잔여 (미출시, registry 미등록으로 404화)
- `connect_provider`(TAI Fix 공급자가격) — 등록위치 미확인 → 찾아 격리
- `connect_registration`(사전등록 리드폼/waitlist) — 유지/격리 **제품결정 대기**
- `fix_chat` — TAI Fix 상담 추정, 미독 → 확인 후 격리
- 격리 방식: 해당 그룹 `router_registry/*.py`의 ROUTERS 스펙 주석처리 `# ISOLATED 2026-08-20 (unlaunched ...)`. 파일은 유지(가역).

## 플래그 (별건, 스코프 밖)
- overdue `/check`: cron-secret 헤더 검증 필요(무단 대량 SMS 차단). 코드에 TODO 있음.
- equipment_assets `/overview`: ALL 전용으로 했음. 회사대면 페이지가 쓰면 재검토.
- companies onboarding/create가 users.company_id 미설정 가능 → 가입자 자사조회 404 위험(가입플로우 버그, 별건).
- 단일섹터: company_id 스코프로 산업/건설 비혼재 달성. 등록시 단일섹터 강제 미적용, 데이터상 105/178 다중섹터(시드 아티팩트?).

## 검증 원칙
커밋 존재 ≠ 해소(실제 READ). 추측 금지. 모든 변경은 GET/배포 SUCCESS로 확인. company_scope.py는 ADDITIVE만. P13: company_id는 토큰에서만. Admin=`_is_admin`(ALL/001)만. SUCCESS 로그 없이 완료 선언 금지.
