# HANDOFF — safe 인증·회사스코프 전체 적용 (Wave 1 완료 · Wave 2 착수)

> 2026-08-20 기획창. 설계·구현·검증 전부 본 창 담당(GPT 미협업 — 이 경계는 법령엔진에만 적용, auth/scope는 "엔진을 라이브에 잇는" 서비스 인프라라 본 창 영역). 설계 정본: `2026-08-20_safe-auth-scope-module-design.md`. 결정: `2026-08-20_DECISION_single-sector-no-scope-merge.md`.

## 완료 (tai-api main, 검증·배포 SUCCESS)
```
ef547c8  company_scope 헬퍼 2개 가산 (require_company_id·scoped_list_company)
7c61574  companies 인증·스코프 (by-id 14개 _ensure_own_company, 공개 등록유틸 예외)
6d5a89a5 미출시 9개 라우터 격리
03e1350  documents 인증·스코프  ← 라이브 SUCCESS(/health 200)
```
- **§73 construction_sites**: 이전 완료·검증.
- **표준 헬퍼**(services/company_scope.py, 가산): `require_company_id`(생성·무회사 403), `scoped_list_company`(목록 (scoped_cid,deny_all)·None-skip 전체노출 차단). 기존 6함수 불변.
- **패턴**: 생성=require_company_id 토큰주입 / 목록=scoped_list_company 무회사 빈결과 / 단건=_ensure_own_company 타사 404. 관리자=ALL(001)만 bypass(role_data_scope 실측).

## 미출시 격리 (commit 6d5a89a5, registry 미등록 = 라우트 언마운트, 파일 존치 → 주석해제로 복원)
선임연결·매칭·수선·정산 클러스터 9개:
- construction.py: `personnel`
- external.py: `repair`·`fix_providers_api`·`matching`·`matching_commission`·`experts`
- payment.py: `contracts_engine`·`connection_commission`·`settlements`
**격리 잔여(미완):**
- `connect_provider` (TAI Fix 공급자가격, /connect/provider) — 등록위치 미확인 → 찾아서 격리 필요
- `connect_registration` (/connect/register, connect_pre_registration) — **공개 사전등록 리드폼**. 유지/격리 **제품결정 대기**
- `fix_chat` (external.py 등록됨) — TAI Fix 상담 추정, 미독 → 격리 전 내용 확인
- `matching_deps`(deps 모듈 추정·미등록), `agent_service`(매칭 무관 추정) — 격리 불필요

## 섹터 결정 (기록)
회사=단일섹터 확정 → company_id 스코프만으로 "산업/건설 안 섞임" 자동 달성. 섹터를 백엔드 스코프에 **미병합**(프론트 gate.ts 메뉴필터 유지). 후속(독립·미완): ①단일섹터 등록강제 부재(companies.business_sector 자유입력) ②다중섹터 회사 105/178 정리(시드 가능성, 원문대조 후).

## OPEN 인벤토리 — 남은 테넌트 라우터 (auth·scope 필요)
**Wave 2 (핵심 안전운영):** `tbm`(서명3 공개예외) · `safety_meetings`(hard delete) · `risk_assessments` · `ra_items`·`ra_report`·`ra_settings`(부모 assessment 경유) · `work_schedules`(생성없음) · `overdue_checker`
**Wave 3 (점검·설비·건설):** `inspection_checklist`·`inspection_sets`·`inspection_setup` · `equipment_assets`·`equipment_checkins` · `corrective_actions` · `subcontractors` · `construction_workflow_router` · `safety_template` · `tbm_templates`
**Wave 4 (복잡):** `org`(부서→팀→그룹 부모체인 스코프)

**이미 스코프됨(정답):** diagnosis·quotes·factories·contracts·education·inspection_schedule·construction_sites·companies·documents.

앞서 READ로 OPEN 확정: tbm·safety_meetings·risk_assessments·work_schedules·org(전부 무인증·클라 company_id 필터·None-skip 전체노출). ra_*·overdue_checker·inspection_*·equipment_*·corrective_actions·subcontractors·construction_workflow·templates = get_current_user 검색 부재로 OPEN(미독 상세).

## 방식
소형·ASCII → 직접 MCP. 20KB+·한국어·핵심보안 → Cursor 작업지시서(`taieng/docs/{날짜}_{제목}.md`). 각 wave=한 배포. 검증: 비로그인 401 / 타사 404 / 무회사 빈결과 / 자사만. 배포 SUCCESS(=/health 200) 전 완료 단정 금지.

## 다음 액션
Wave 2 착수 — `safety_meetings` 먼저(OPEN·hard delete·패턴 단순). 지시서 → Cursor → 검증 → 다음.
