# DESIGN — safe 라우터 인증·회사스코프 전체 적용 (모듈화)

> 발행: 기획창 2026-08-20. 설계·구현·검증 전부 본 창 담당(GPT 미협업). 참조 구현: §73 `construction_sites_router`. 정본 모듈: `services/company_scope.py`(기존).

## 1. 목표 (운영자 3규칙)
1. safe 페이지는 로그인 필수(사용자에 `users.sector` 실림 — `current["sector"]`로 접근).
2. `company_id`는 로그인 후 회사등록 시 생성 → **로그인했으나 회사 없는 상태** 존재. 무회사는 회사데이터 0건(남의 것·전체 노출 금지).
3. safe 전 페이지는 자기 회사 것만. TAI 총관리자(ALL)만 전사.

## 2. 검증된 근거 (실측)
- `routers/auth.get_current_user`(Depends): Bearer 토큰 검증 → **users 행 전체 반환**(id, `company_id`[nullable], `role_code`, `sector`…). 토큰 없음/무효 → 401.
- `services/company_scope.py`(기존): `_scope`(role→scope_type, 미정의 TEAM), `_is_admin`(=="ALL"만), `_ensure_own_company`(비-ALL 타사/무회사 → **404**), `_forced_company_id`(비-ALL이면 토큰 company_id 강제), `_ensure_factory_own`.
- `role_data_scope` 실측: **001=ALL** / 002=COMPANY / 003·008=FACTORY / 004·013=TEAM / 005·006·007=ASSIGNED. → 001만 전사, 나머지 자기 회사. (회사 스코프는 COMPANY 레벨로 충분 — factory/team 세분화는 leader_scope 별도 관심사, 본 설계 범위 밖.)
- `services/construction_svc.run_list_query` 등 목록 쿼리는 **None 필터 skip** → 무회사에 None 넘기면 전체 노출. 목록은 "무회사 → 빈 결과" 명시 필요.
- **OPEN 인벤토리(무인증·무스코프) ~21개**: `companies` `personnel` `documents` `tbm` `safety_meetings` `risk_assessments` `ra_items` `ra_report` `ra_settings` `work_schedules` `org` `overdue_checker` `equipment_assets` `equipment_checkins` `inspection_checklist` `inspection_sets` `inspection_setup` `corrective_actions` `subcontractors` `construction_workflow_router` `safety_template` `tbm_templates`. (이미 스코프됨: diagnosis·quotes·factories·contracts·education·inspection_schedule·construction_sites(§73).)

## 3. 아키텍처 — 2계층

### Layer 1: 로그인 게이트 (라우터 단위, 즉효)
각 OPEN 라우터의 `APIRouter(...)`에 **`dependencies=[Depends(get_current_user)]`** 한 줄 추가 → 그 라우터 전 엔드포인트 로그인 강제. 공개 라우터·엔진은 손대지 않음(라우터 단위라 교차오염 없음).
- **예외(공개 엔드포인트 혼재)**: `tbm`의 `/{id}/sign-info`·`/sign`·`/request-sign`는 비공개링크(무로그인) 서명 흐름 → 라우터 단위 게이트 금지, **엔드포인트별** 적용.

### Layer 2: 회사 스코프 (라우터별 배선, 필수)
로그인 게이트만으로는 A사 로그인 사용자가 B사 데이터를 못 막음. 라우터별로 기존 3헬퍼 배선:
- **생성**: `company_id = require_company_id(current)`(무회사 403) → payload에 강제 주입(body 값 무시, P13).
- **목록**: `scoped_cid, deny = scoped_list_company(current, sb, company_id)` → `deny`면 빈 봉투 반환, 아니면 `scoped_cid`로 필터.
- **단건/수정/삭제/실행**: 자원의 company_id 조회 → `_ensure_own_company(company_id, current, sb, "…없습니다.")`(타사/무회사 404).

## 4. 표준 헬퍼 (company_scope.py에 **가산만** — 기존 7개 라우터 불변)
```python
def require_company_id(current, supabase):
    """생성용: 비-ALL은 토큰 company_id 필수. 무회사 → 403."""
    if _is_admin(_scope(supabase, current.get("role_code"))):
        return current.get("company_id")  # ALL은 None 허용(있으면 사용)
    cid = current.get("company_id")
    if not cid:
        raise HTTPException(403, "회사 등록이 필요합니다.")
    return cid

def scoped_list_company(current, supabase, company_id):
    """목록용: (scoped_cid, deny_all) 반환. None-skip 전체노출 차단.
    비-ALL이고 회사 없으면 deny_all=True → 라우터는 빈 결과."""
    if _is_admin(_scope(supabase, current.get("role_code"))):
        return company_id, False           # ALL: 클라 값 유지(None=전체)
    cid = current.get("company_id")
    if not cid:
        return None, True                  # 무회사 → 빈 결과
    return cid, False                      # 자기 회사 강제
```
(단건은 기존 `_ensure_own_company` 그대로 사용.)

## 5. 특수 케이스
- **companies**: 사용자는 **자기 회사 레코드**를 본다. 스코프 키가 FK가 아니라 **행의 `id` == current.company_id**. 목록/단건 모두 `id` 기준 스코프(별도 처리). ALL은 전체.
- **org**(부서→팀→그룹): 팀/그룹에 company_id 직접 없음 → 생성 시 부모(부서/팀)의 company_id 해석, 단건 스코프도 부모체인 조회. **가장 복잡 — 마지막 wave.**
- **work_schedules**: 사용자 생성 없음(엔진 생성). 목록 스코프 + 단건/일괄변경 시 자원 company_id로 `_ensure_own_company`. `confirm/{factory_id}`는 factory 소유 확인(`_ensure_factory_own`).
- **ra_items/ra_report**: 자원이 `assessment_id` 경유 → 부모 `risk_assessments.company_id`로 스코프.
- **tbm**: 서명 3엔드포인트 공개 유지(Layer1 예외), CRUD만 스코프.

## 6. 우선순위 (민감도순)
- **Wave 1 (최고민감)**: `companies` · `personnel` · `documents`
- **Wave 2 (핵심 안전운영)**: `tbm` · `safety_meetings` · `risk_assessments`(+`ra_items`·`ra_report`·`ra_settings`) · `work_schedules` · `overdue_checker`
- **Wave 3 (점검·설비·건설)**: `inspection_checklist`·`inspection_sets`·`inspection_setup` · `equipment_assets`·`equipment_checkins` · `corrective_actions` · `subcontractors` · `construction_workflow_router` · `safety_template` · `tbm_templates`
- **Wave 4 (복잡)**: `org`(부모체인)

## 7. 구현 방식
1. company_scope.py에 §4 헬퍼 2개 가산(단일 커밋). 기존 함수·시그니처 불변.
2. 라우터별 str_replace: ①APIRouter에 `dependencies=` 1줄 ②import 추가 ③create/list/by-id 배선. 20KB+·한국어 다수 라우터는 Cursor 수술 편집, 소형은 직접 MCP.
3. Wave 단위로 커밋·배포·검증. 한 wave = 한 배포.

## 8. 검증 (라우터별 확인 한 줄, 본 창이 실행)
- 비로그인 임의 엔드포인트 → **401**.
- 로그인+타사 company_id로 생성 → 저장 행 company_id = 내 회사.
- 무회사 계정 목록 → **0건**(전체 아님).
- 타사 자원 id 단건/삭제 → **404**.
- 자사 계정 목록 → 자사만.
- role_data_scope 001=ALL 실측 확인됨 → 총관리자 전사 정상.

## 9. 회귀 금지
- 클라 `company_id`/`factory_id` 신뢰 금지(P13). 회사귀속은 토큰에서만.
- 관리자 판정은 `_is_admin(_scope(...))`(ALL)만. role_code 직접 비교 금지.
- company_scope.py는 **가산만** — 기존 7개 라우터 동작 불변.
- 자동 진단·일정·서명 등 업무 로직 불변, 인증·스코프만 앞단 추가.
- 목록 무회사에 None을 쿼리로 넘기지 말 것(전체 노출).

## 10. 진행 로그 (본 창 갱신)
- [ ] 헬퍼 2개 가산 (company_scope.py)
- [ ] Wave 1: companies · personnel · documents
- [ ] Wave 2: tbm · safety_meetings · risk_assessments(+ra_*) · work_schedules · overdue_checker
- [ ] Wave 3: inspection_* · equipment_* · corrective_actions · subcontractors · construction_workflow · templates
- [ ] Wave 4: org
